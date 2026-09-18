import hashlib
import json
import logging
import os
import re
import threading
from collections import OrderedDict
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = Path(os.getenv("NVIDIA_DATA_PATH", "/data/nvidia-interconnects.json"))
PROFILE_PATH = Path(os.getenv("DEVICE_PROFILES_PATH", "/profiles/device-profiles.json"))
STATIC_DIR = BASE_DIR / "static"
MAX_DATA_BYTES = int(os.getenv("MAX_DATA_BYTES", str(2 * 1024 * 1024)))
MAX_PROFILE_BYTES = int(os.getenv("MAX_PROFILE_BYTES", str(512 * 1024)))
COMPAT_CACHE_MAX_ENTRIES = int(os.getenv("COMPAT_CACHE_MAX_ENTRIES", "256"))
logger = logging.getLogger("uvicorn.error")

app = FastAPI(title="NVIDIA Networking Compatibility Validator", version="0.5.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Schema v8 port_interface_compatibility is authoritative. This matrix is used
# only by older snapshots and local DGX profiles which predate that catalog data.
LEGACY_CAGE_MODULE_COMPATIBILITY: dict[str, set[str]] = {
    "OSFP": {"OSFP"},
    "QSFP-DD": {"QSFP-DD", "QSFP56", "QSFP28", "QSFP+"},
    "QSFP112": {"QSFP112", "QSFP56", "QSFP28", "QSFP+"},
    "QSFP56": {"QSFP56", "QSFP28", "QSFP+"},
    "QSFP28": {"QSFP28", "QSFP+"},
    "QSFP+": {"QSFP+"},
    "SFP56": {"SFP56", "SFP28", "SFP+"},
    "SFP28": {"SFP28", "SFP+"},
    "SFP+": {"SFP+"},
    "MMC-12": {"MMC-12"},
    "RJ45": {"RJ45"},
}
CONNECTOR_PATTERN = r"OSFP|QSFP-DD|QSFP112|QSFP56|QSFP28|QSFP\+|QSFP|SFP56|SFP28|SFP\+|SFP|MMC-12|RJ45"


def _rows(section: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not section:
        return []
    return [dict(zip(section.get("fields", []), row)) for row in section.get("items", [])]


def _speed_gbps(value: Any) -> int | None:
    if value is None:
        return None
    match = re.search(r"(\d+(?:\.\d+)?)\s*(T(?:b)?|G(?:b)?)", str(value), re.I)
    if not match:
        return None
    speed = float(match.group(1))
    if match.group(2).upper().startswith("T"):
        speed *= 1000
    return int(speed)


def _connector_family(value: str | None) -> str | None:
    if not value:
        return None
    v = value.strip().upper()
    for family in (
        "QSFP-DD", "QSFP112", "QSFP56", "QSFP28", "QSFP+", "QSFP",
        "SFP56", "SFP28", "SFP+", "SFP", "OSFP", "MMC-12", "RJ45",
    ):
        if v.startswith(family):
            if family == "QSFP":
                return "QSFP+"
            if family == "SFP":
                return "SFP+"
            return family
    return v.split()[0] if v else None


def _family_class(family: str | None) -> str | None:
    if not family:
        return None
    if family == "OSFP":
        return "OSFP"
    if family.startswith("QSFP"):
        return "QSFP"
    if family.startswith("SFP"):
        return "SFP"
    return family


def _host_side(interface_type: str | None) -> str | None:
    return interface_type.split("->", 1)[0].strip() if interface_type else None


def _interconnect_id(item: dict[str, Any]) -> str:
    return "|".join([
        str(item.get("category") or "Unknown"),
        str(item.get("model") or "Unknown"),
        str(item.get("variant") or "-"),
    ])


def _device_id(kind: str, model: str) -> str:
    return f"{kind}:{model}"


def _legacy_accepted(cage_family: str | None) -> set[str]:
    if not cage_family:
        return set()
    return LEGACY_CAGE_MODULE_COMPATIBILITY.get(cage_family, {cage_family})


def _normalized_pluggables(entry: dict[str, Any] | None) -> list[tuple[str, str]]:
    result: list[tuple[str, str]] = []
    for raw in (entry or {}).get("accepted_pluggables") or []:
        family = _connector_family(str(raw))
        if family:
            result.append((str(raw), family))
    return result


def _fixed_families(entry: dict[str, Any] | None) -> set[str]:
    return {
        family
        for raw in (entry or {}).get("fixed_interfaces") or []
        if (family := _connector_family(str(raw)))
    }


def _accepted_for_cage(cage_family: str | None, entry: dict[str, Any] | None) -> tuple[set[str], str]:
    if entry is not None and "accepted_pluggables" in entry:
        cage_class = _family_class(cage_family)
        accepted = {
            family
            for _, family in _normalized_pluggables(entry)
            if _family_class(family) == cage_class
        }
        return accepted, "dataset-v8"
    return _legacy_accepted(cage_family), "legacy-fallback"


def _mechanical_interfaces(raw_label: str, family: str | None) -> list[str]:
    if family != "OSFP":
        return []
    upper = raw_label.upper()
    if "RHS" in upper or "FLAT" in upper:
        return ["OSFP-flattop"]
    if "IHS" in upper or "FINNED" in upper:
        return ["OSFP-finned"]
    return []


def _compat_entry(raw: dict[str, Any], bucket: str, model: str) -> dict[str, Any] | None:
    return ((raw.get("port_interface_compatibility") or {}).get(bucket) or {}).get(model)


def _parse_switch_port_groups(
    record: dict[str, Any],
    fabric: str,
    compatibility_entry: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    connectors = str(record.get("connectors") or "")
    if not connectors:
        return []

    matches: list[tuple[int, int, str, int | None, int]] = []
    occupied: list[tuple[int, int]] = []
    for m in re.finditer(rf"(\d+)x(\d+)\s+({CONNECTOR_PATTERN})", connectors, re.I):
        matches.append((m.start(), m.end(), m.group(3), None, int(m.group(1)) * int(m.group(2))))
        occupied.append((m.start(), m.end()))
    for m in re.finditer(rf"(\d+)x\s+({CONNECTOR_PATTERN})", connectors, re.I):
        if any(a <= m.start() < b for a, b in occupied):
            continue
        remainder = connectors[m.end():]
        separator = re.search(r"\s+\+\s+", remainder)
        segment = remainder[: separator.start()] if separator else remainder
        lane = re.search(r"(?:(\d+)x)?\s*(\d+(?:\.\d+)?)\s*(Tb/s|TbE|Gb/s|GbE)", segment, re.I)
        module_speed = None
        if lane:
            lane_speed = _speed_gbps(f"{lane.group(2)} {lane.group(3)}")
            module_speed = int(lane.group(1) or 1) * lane_speed if lane_speed else None
        matches.append((m.start(), m.end(), m.group(2), module_speed, int(m.group(1))))
    if not matches:
        return []

    port_counts = record.get("port_counts") or {}
    groups: list[dict[str, Any]] = []
    high_speed_matches = [m for m in matches if _connector_family(m[2]) not in {"SFP28", "SFP+", "RJ45"}]
    fixed_families = _fixed_families(compatibility_entry)

    for idx, (_, _, connector, parsed_speed, count) in enumerate(matches, start=1):
        family = _connector_family(connector)
        module_speed = parsed_speed
        breakouts: list[dict[str, int]] = []
        mode_speeds: set[int] = set()
        accepted_families, compatibility_source = _accepted_for_cage(family, compatibility_entry)

        explicit_mechanics: set[str] = set()
        for raw_label, raw_family in _normalized_pluggables(compatibility_entry):
            if raw_family == family:
                explicit_mechanics.update(_mechanical_interfaces(raw_label, raw_family))
        accepted_interfaces = sorted(explicit_mechanics)
        if family == "OSFP" and not accepted_interfaces:
            accepted_interfaces = ["OSFP-finned"]

        if len(high_speed_matches) == 1 and family not in {"SFP28", "SFP+", "RJ45", "MMC-12"}:
            for speed_key, logical_count in port_counts.items():
                speed = _speed_gbps(speed_key)
                if speed and isinstance(logical_count, int) and count and logical_count % count == 0:
                    ratio = logical_count // count
                    if 1 <= ratio <= 8:
                        mode_speeds.add(speed)
                        breakouts.append({"links_per_port": ratio, "link_speed_gbps": speed})
            if breakouts and module_speed is None:
                module_speed = max(x["links_per_port"] * x["link_speed_gbps"] for x in breakouts)
        if module_speed is None:
            module_speed = _speed_gbps(record.get("speed"))
        if module_speed:
            mode_speeds.add(module_speed)

        if compatibility_entry is None:
            pluggable = family != "MMC-12"
        elif compatibility_entry.get("pluggable") is False:
            pluggable = False
        elif family in fixed_families:
            pluggable = False
        else:
            pluggable = bool(accepted_families)

        groups.append({
            "id": f"ports-{idx}",
            "label": f"{count} × {family}" + (f" ({module_speed}G module capacity)" if module_speed else ""),
            "count": count,
            "connector_family": family,
            "accepted_connector_families": sorted(accepted_families),
            "accepted_interface_types": accepted_interfaces,
            "module_speed_gbps": module_speed,
            "supported_module_speeds_gbps": sorted(mode_speeds),
            "fabrics": [fabric],
            "breakouts": breakouts,
            "pluggable": pluggable,
            "compatibility_source": compatibility_source,
            "compatibility_source_url": (compatibility_entry or {}).get("source_url"),
            "catalog_accepted_pluggables": (compatibility_entry or {}).get("accepted_pluggables") or [],
            "fixed_interfaces": (compatibility_entry or {}).get("fixed_interfaces") or [],
            "notes": (
                "Switch-side OSFP is constrained to finned-top modules."
                if family == "OSFP"
                else "Accepted module families are taken from port_interface_compatibility when available."
            ),
        })
    return groups


def _catalog_groups(item: dict[str, Any], entry: dict[str, Any] | None, fabric: str | None = None) -> list[dict[str, Any]]:
    if not entry or entry.get("pluggable") is not True:
        return []
    normalized = _normalized_pluggables(entry)
    if not normalized:
        return []

    by_class: dict[str, list[tuple[str, str]]] = {}
    for raw_label, family in normalized:
        by_class.setdefault(_family_class(family) or family, []).append((raw_label, family))

    groups: list[dict[str, Any]] = []
    capacity = _speed_gbps(item.get("speed"))
    for idx, values in enumerate(by_class.values(), start=1):
        primary_family = values[0][1]
        mechanics: set[str] = set()
        for raw_label, family in values:
            mechanics.update(_mechanical_interfaces(raw_label, family))
        groups.append({
            "id": f"catalog-{idx}",
            "label": "Catalog cage — " + " / ".join(raw_label for raw_label, _ in values),
            "count": None,
            "connector_family": primary_family,
            "accepted_connector_families": sorted({family for _, family in values}),
            "accepted_interface_types": sorted(mechanics),
            "module_speed_gbps": capacity,
            "supported_module_speeds_gbps": [],
            "fabrics": [fabric] if fabric else [],
            "breakouts": [],
            "pluggable": True,
            "compatibility_source": "dataset-v8",
            "compatibility_source_url": entry.get("source_url"),
            "catalog_accepted_pluggables": entry.get("accepted_pluggables") or [],
            "fixed_interfaces": entry.get("fixed_interfaces") or [],
            "scope_note": entry.get("scope_note"),
            "variants": entry.get("variants") or [],
            "notes": "Built from schema v8 port_interface_compatibility; physical port quantity is not inferred.",
        })
    return groups



def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _validate_table(section_name: str, section: Any) -> None:
    _require(isinstance(section, dict), f"{section_name} must be an object")
    fields = section.get("fields")
    items = section.get("items")
    _require(isinstance(fields, list) and fields, f"{section_name}.fields must be a non-empty array")
    _require(all(isinstance(x, str) and x for x in fields), f"{section_name}.fields must contain non-empty strings")
    _require(len(fields) == len(set(fields)), f"{section_name}.fields contains duplicate names")
    _require(isinstance(items, list), f"{section_name}.items must be an array")
    for idx, row in enumerate(items):
        _require(isinstance(row, list), f"{section_name}.items[{idx}] must be an array")
        _require(len(row) == len(fields), f"{section_name}.items[{idx}] length does not match fields")


def _validate_rows(name: str, fields: Any, rows: Any, required_fields: set[str] | None = None) -> None:
    _require(isinstance(fields, list) and fields, f"{name} fields must be a non-empty array")
    _require(all(isinstance(x, str) and x for x in fields), f"{name} fields must contain non-empty strings")
    _require(len(fields) == len(set(fields)), f"{name} fields contains duplicate names")
    if required_fields:
        missing = required_fields.difference(fields)
        _require(not missing, f"{name} fields missing required keys: {sorted(missing)}")
    _require(isinstance(rows, list), f"{name} rows must be an array")
    for idx, row in enumerate(rows):
        _require(isinstance(row, list), f"{name}[{idx}] must be an array")
        _require(len(row) == len(fields), f"{name}[{idx}] length does not match fields")


def _validate_dataset_schema(raw: Any) -> None:
    _require(isinstance(raw, dict), "catalog root must be an object")
    for key in (
        "schema_version", "snapshot_date", "generated_at", "timezone", "sources",
        "linkx", "ethernet", "infiniband", "silicon_photonics", "dpu", "supernic",
        "summary", "notes", "port_interface_compatibility",
    ):
        _require(key in raw, f"catalog missing required key: {key}")
    _require(isinstance(raw["schema_version"], int) and raw["schema_version"] >= 1, "schema_version must be a positive integer")
    _require(isinstance(raw["snapshot_date"], str) and raw["snapshot_date"], "snapshot_date must be a non-empty string")
    _require(isinstance(raw["generated_at"], str) and raw["generated_at"], "generated_at must be a non-empty string")
    _require(isinstance(raw["timezone"], str) and raw["timezone"], "timezone must be a non-empty string")

    sources = raw["sources"]
    _require(isinstance(sources, dict) and sources, "sources must be a non-empty object")
    for key, value in sources.items():
        _require(isinstance(key, str) and key, "source keys must be non-empty strings")
        _require(isinstance(value, str) and value, f"sources.{key} must be a non-empty string")

    for name in ("ethernet", "infiniband", "silicon_photonics", "supernic", "dpu"):
        _validate_table(name, raw[name])

    summary = raw["summary"]
    _require(isinstance(summary, dict), "summary must be an object")
    for key, value in summary.items():
        _require(isinstance(key, str) and key, "summary keys must be non-empty strings")
        _require(isinstance(value, int) and value >= 0, f"summary.{key} must be a non-negative integer")
    _require(isinstance(raw["notes"], list) and all(isinstance(x, str) for x in raw["notes"]), "notes must be an array of strings")

    linkx = raw["linkx"]
    _require(isinstance(linkx, dict), "linkx must be an object")
    _validate_rows(
        "linkx.active",
        linkx.get("product_fields"),
        linkx.get("active"),
        {"model", "speed", "category"},
    )
    _validate_rows(
        "linkx.no_longer_for_sale",
        linkx.get("product_fields"),
        linkx.get("no_longer_for_sale"),
        {"model", "speed", "category"},
    )
    _validate_rows(
        "linkx.transceivers",
        linkx.get("transceiver_fields"),
        linkx.get("transceivers"),
        {"category", "model", "status", "speed", "interface_type"},
    )
    _validate_rows(
        "linkx.aoc",
        linkx.get("detailed_interconnect_fields"),
        linkx.get("aoc"),
        {"category", "model", "status", "speed", "interface_type"},
    )
    _validate_rows(
        "linkx.copper",
        linkx.get("detailed_interconnect_fields"),
        linkx.get("copper"),
        {"category", "model", "status", "speed", "interface_type"},
    )

    fabric_map = linkx.get("transceiver_fabric_compatibility", {})
    _require(isinstance(fabric_map, dict), "linkx.transceiver_fabric_compatibility must be an object")
    for key, value in fabric_map.items():
        _require(isinstance(key, str) and key, "fabric compatibility keys must be non-empty strings")
        _require(isinstance(value, list) and all(isinstance(x, str) for x in value), f"fabric compatibility for {key} must be an array of strings")

    compatibility = raw.get("port_interface_compatibility", {})
    _require(isinstance(compatibility, dict), "port_interface_compatibility must be an object")
    for bucket, models in compatibility.items():
        _require(isinstance(bucket, str) and bucket, "compatibility bucket name must be a non-empty string")
        _require(isinstance(models, dict), f"port_interface_compatibility.{bucket} must be an object")
        for model, entry in models.items():
            _require(isinstance(model, str) and model, f"{bucket} model key must be a non-empty string")
            _require(isinstance(entry, dict), f"{bucket}.{model} must be an object")
            if "pluggable" in entry:
                _require(isinstance(entry["pluggable"], bool), f"{bucket}.{model}.pluggable must be boolean")
            for list_key in ("accepted_pluggables", "fixed_interfaces"):
                if list_key in entry:
                    _require(
                        isinstance(entry[list_key], list) and all(isinstance(x, str) and x for x in entry[list_key]),
                        f"{bucket}.{model}.{list_key} must be an array of non-empty strings",
                    )
            for string_key in ("source_url", "scope_note"):
                if string_key in entry and entry[string_key] is not None:
                    _require(isinstance(entry[string_key], str), f"{bucket}.{model}.{string_key} must be a string")
            if "variants" in entry:
                _require(isinstance(entry["variants"], list), f"{bucket}.{model}.variants must be an array")


def _validate_profiles_schema(raw: Any) -> None:
    _require(isinstance(raw, dict), "profiles root must be an object")
    _require(isinstance(raw.get("schema_version"), int) and raw["schema_version"] >= 1, "profiles.schema_version must be a positive integer")
    profiles = raw.get("profiles")
    _require(isinstance(profiles, list), "profiles must be an array")
    seen_profile_ids: set[str] = set()
    for pidx, profile in enumerate(profiles):
        _require(isinstance(profile, dict), f"profiles[{pidx}] must be an object")
        for key in ("id", "kind", "model", "port_groups"):
            _require(key in profile, f"profiles[{pidx}] missing required key: {key}")
        for key in ("id", "kind", "model"):
            _require(isinstance(profile[key], str) and profile[key], f"profiles[{pidx}].{key} must be a non-empty string")
        _require(profile["id"] not in seen_profile_ids, f"duplicate profile id: {profile['id']}")
        seen_profile_ids.add(profile["id"])
        groups = profile["port_groups"]
        _require(isinstance(groups, list), f"profiles[{pidx}].port_groups must be an array")
        seen_group_ids: set[str] = set()
        for gidx, group in enumerate(groups):
            prefix = f"profiles[{pidx}].port_groups[{gidx}]"
            _require(isinstance(group, dict), f"{prefix} must be an object")
            for key in ("id", "label", "connector_family", "pluggable"):
                _require(key in group, f"{prefix} missing required key: {key}")
            for key in ("id", "label", "connector_family"):
                _require(isinstance(group[key], str) and group[key], f"{prefix}.{key} must be a non-empty string")
            _require(group["id"] not in seen_group_ids, f"{prefix}.id must be unique within profile")
            seen_group_ids.add(group["id"])
            _require(isinstance(group["pluggable"], bool), f"{prefix}.pluggable must be boolean")
            if "count" in group:
                _require(group["count"] is None or (isinstance(group["count"], int) and group["count"] >= 0), f"{prefix}.count must be a non-negative integer or null")
            for key in ("module_speed_gbps",):
                if key in group and group[key] is not None:
                    _require(isinstance(group[key], int) and group[key] > 0, f"{prefix}.{key} must be a positive integer")
            for key in ("accepted_interface_types", "fabrics", "supported_module_speeds_gbps"):
                if key in group:
                    _require(isinstance(group[key], list), f"{prefix}.{key} must be an array")
            for bidx, breakout in enumerate(group.get("breakouts") or []):
                _require(isinstance(breakout, dict), f"{prefix}.breakouts[{bidx}] must be an object")
                _require(isinstance(breakout.get("links_per_port"), int) and breakout["links_per_port"] > 0, f"{prefix}.breakouts[{bidx}].links_per_port must be positive")
                _require(isinstance(breakout.get("link_speed_gbps"), int) and breakout["link_speed_gbps"] > 0, f"{prefix}.breakouts[{bidx}].link_speed_gbps must be positive")


def _read_json_limited(path: Path, max_bytes: int, label: str) -> tuple[Any, bytes]:
    try:
        size = path.stat().st_size
    except FileNotFoundError as exc:
        raise ValueError(f"{label} file not found") from exc
    _require(size <= max_bytes, f"{label} exceeds size limit ({size} > {max_bytes} bytes)")
    data = path.read_bytes()
    _require(len(data) <= max_bytes, f"{label} exceeds size limit")
    try:
        return json.loads(data), data
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} is not valid UTF-8 JSON") from exc


class LiveCatalog:
    def __init__(self, data_path: Path, profile_path: Path):
        self.data_path = data_path
        self.profile_path = profile_path
        self._lock = threading.RLock()
        self._signature: tuple[Any, ...] | None = None
        self._snapshot: dict[str, Any] = {}
        self._last_error: str | None = None

    @staticmethod
    def _file_signature(path: Path) -> tuple[int, int] | None:
        try:
            stat = path.stat()
            return stat.st_mtime_ns, stat.st_size
        except FileNotFoundError:
            return None

    def get(self) -> dict[str, Any]:
        signature = (self._file_signature(self.data_path), self._file_signature(self.profile_path))
        with self._lock:
            if signature != self._signature:
                try:
                    candidate = self._load()
                except Exception as exc:
                    self._signature = signature
                    self._last_error = str(exc)
                    if not self._snapshot:
                        raise
                    logger.exception("Catalog reload rejected; serving last-known-good snapshot")
                else:
                    self._snapshot = candidate
                    self._signature = signature
                    self._last_error = None
            return self._snapshot

    def _load(self) -> dict[str, Any]:
        raw, data_bytes = _read_json_limited(self.data_path, MAX_DATA_BYTES, "catalog")
        _validate_dataset_schema(raw)

        profiles_raw, profile_bytes = _read_json_limited(self.profile_path, MAX_PROFILE_BYTES, "profiles")
        _validate_profiles_schema(profiles_raw)
        profiles = profiles_raw["profiles"]

        revision = hashlib.sha256(data_bytes + b"\0" + profile_bytes).hexdigest()[:12]
        return {
            "raw": raw,
            "devices": self._build_devices(raw, profiles),
            "interconnects": self._build_interconnects(raw),
            "revision": revision,
            "schema_version": raw.get("schema_version"),
            "snapshot_date": raw.get("snapshot_date"),
            "generated_at": raw.get("generated_at"),
        }

    @staticmethod
    def _build_interconnects(raw: dict[str, Any]) -> list[dict[str, Any]]:
        linkx = raw.get("linkx", {})
        result: list[dict[str, Any]] = []
        fields = linkx.get("transceiver_fields", [])
        fabric_map = linkx.get("transceiver_fabric_compatibility", {})
        for row in linkx.get("transceivers", []):
            item = dict(zip(fields, row))
            key = item.get("model") if not item.get("variant") else f"{item.get('model')}|{item.get('variant')}"
            item["fabric_compatibility"] = fabric_map.get(key, fabric_map.get(item.get("model"), []))
            item["id"] = _interconnect_id(item)
            result.append(item)
        detailed_fields = linkx.get("detailed_interconnect_fields", [])
        for bucket in ("aoc", "copper"):
            for row in linkx.get(bucket, []):
                item = dict(zip(detailed_fields, row))
                item["id"] = _interconnect_id(item)
                result.append(item)
        return result

    @staticmethod
    def _build_devices(raw: dict[str, Any], profiles: list[dict[str, Any]]) -> list[dict[str, Any]]:
        devices: list[dict[str, Any]] = []
        for item in _rows(raw.get("ethernet")):
            compat = _compat_entry(raw, "ethernet_switching", item["model"])
            groups = _parse_switch_port_groups(item, "ETH", compat)
            devices.append({
                "id": _device_id("ethernet", item["model"]), "kind": "Ethernet switch",
                "model": item["model"], "family": item.get("family"), "speed": item.get("speed"),
                "port_groups": groups, "validation_ready": any(g.get("pluggable") for g in groups),
                "source": "dataset", "accepted_pluggables": (compat or {}).get("accepted_pluggables") or [],
                "fixed_interfaces": (compat or {}).get("fixed_interfaces") or [],
                "compatibility_source_url": (compat or {}).get("source_url"),
            })
        for item in _rows(raw.get("infiniband")):
            compat = _compat_entry(raw, "infiniband_and_appliances", item["model"])
            groups = _parse_switch_port_groups(item, "IB", compat)
            if not groups:
                groups = _catalog_groups(item, compat, "IB")
            devices.append({
                "id": _device_id("infiniband", item["model"]), "kind": "InfiniBand switch / appliance",
                "model": item["model"], "family": item.get("family"), "speed": item.get("speed"),
                "port_groups": groups, "validation_ready": any(g.get("pluggable") for g in groups),
                "source": "dataset", "accepted_pluggables": (compat or {}).get("accepted_pluggables") or [],
                "fixed_interfaces": (compat or {}).get("fixed_interfaces") or [],
                "compatibility_source_url": (compat or {}).get("source_url"),
                "scope_note": (compat or {}).get("scope_note"), "variants": (compat or {}).get("variants") or [],
            })
        for section, kind in (("supernic", "SuperNIC / adapter"), ("dpu", "DPU")):
            for item in _rows(raw.get(section)):
                compat = _compat_entry(raw, section, item["model"])
                groups = _catalog_groups(item, compat, "ETH" if section == "supernic" else None)
                devices.append({
                    "id": _device_id(section, item["model"]), "kind": kind,
                    "model": item["model"], "family": section, "speed": item.get("speed"),
                    "port_groups": groups, "validation_ready": bool(groups), "source": "dataset",
                    "accepted_pluggables": (compat or {}).get("accepted_pluggables") or [],
                    "fixed_interfaces": (compat or {}).get("fixed_interfaces") or [],
                    "compatibility_source_url": (compat or {}).get("source_url"),
                    "scope_note": (compat or {}).get("scope_note"), "variants": (compat or {}).get("variants") or [],
                    "warning": None if groups else "The catalog does not assert enough external cage information for pluggable validation.",
                })
        for raw_profile in profiles:
            profile = dict(raw_profile)
            profile.setdefault("id", _device_id("system", profile["model"]))
            profile.setdefault("kind", "NVIDIA system")
            profile.setdefault("source", "profile")
            for group in profile.get("port_groups", []):
                group.setdefault("accepted_connector_families", sorted(_legacy_accepted(group.get("connector_family"))))
                group.setdefault("compatibility_source", "profile")
            profile["validation_ready"] = bool(profile.get("port_groups"))
            devices.append(profile)
        return sorted(devices, key=lambda x: (x.get("kind", ""), x.get("model", "")))

    @staticmethod
    def compatible(group: dict[str, Any], item: dict[str, Any]) -> tuple[bool, str, list[str]]:
        if item.get("status") != "active":
            return False, "rejected", ["interconnect is not active"]
        if not group.get("pluggable", True):
            return False, "rejected", ["port is not a pluggable interface"]

        reasons: list[str] = []
        group_fabrics = set(group.get("fabrics") or [])
        item_fabrics = set(item.get("fabric_compatibility") or [])
        if group_fabrics and item_fabrics and not group_fabrics.intersection(item_fabrics):
            return False, "rejected", ["fabric mismatch"]

        host = _host_side(item.get("interface_type"))
        host_family = _connector_family(host)
        cage_family = _connector_family(group.get("connector_family"))
        raw_accepted = group.get("accepted_connector_families")
        accepted_families = set(raw_accepted) if raw_accepted is not None else _legacy_accepted(cage_family)
        accepted_interfaces = set(group.get("accepted_interface_types") or [])

        if cage_family == "OSFP" and accepted_interfaces:
            if host not in accepted_interfaces:
                return False, "rejected", [f"mechanical mismatch: requires one of {sorted(accepted_interfaces)}"]
            exact_mechanical = True
        else:
            exact_mechanical = bool(host_family == cage_family)
        if cage_family and host_family not in accepted_families:
            return False, "rejected", [
                f"connector mismatch: {host_family} module is not accepted by {cage_family} cage; accepted families: {sorted(accepted_families)}"
            ]

        item_speed = _speed_gbps(item.get("speed"))
        allowed_speeds = set(group.get("supported_module_speeds_gbps") or [])
        module_capacity = group.get("module_speed_gbps")
        if allowed_speeds and item_speed and item_speed not in allowed_speeds:
            return False, "rejected", [
                f"module speed {item_speed}G is not an advertised port mode; supported modes: {sorted(allowed_speeds)}"
            ]
        if module_capacity and item_speed and item_speed > module_capacity:
            return False, "rejected", [f"module speed {item_speed}G exceeds {module_capacity}G port capacity"]

        if cage_family == "OSFP" and exact_mechanical:
            confidence = "exact"
            reasons.append("exact OSFP mechanical interface match")
        elif host_family == cage_family:
            confidence = "exact"
            reasons.append("exact connector-family match")
        else:
            confidence = "backward-compatible"
            reasons.append(f"catalog accepts {host_family} module in {cage_family} cage")
        if group.get("compatibility_source") == "dataset-v8":
            reasons.append("module/cage compatibility confirmed by schema v8 catalog")
        if allowed_speeds and item_speed:
            reasons.append(f"{item_speed}G is an advertised device port/module mode")
        if group_fabrics.intersection(item_fabrics):
            reasons.append("fabric compatibility match")
        return True, confidence, reasons


catalog = LiveCatalog(DATA_PATH, PROFILE_PATH)
_compat_cache: OrderedDict[tuple[str, str, str], list[dict[str, Any]]] = OrderedDict()
_compat_cache_lock = threading.RLock()


def _snapshot_or_503() -> dict[str, Any]:
    try:
        return catalog.get()
    except Exception:
        logger.exception("Catalog unavailable")
        raise HTTPException(status_code=503, detail="Service unavailable") from None


def _find_device(snapshot: dict[str, Any], device_id: str) -> dict[str, Any]:
    device = next((d for d in snapshot["devices"] if d["id"] == device_id), None)
    if not device:
        raise HTTPException(status_code=404, detail="Unknown device")
    return device


def _find_group(device: dict[str, Any], group_id: str) -> dict[str, Any]:
    group = next((g for g in device.get("port_groups", []) if g["id"] == group_id), None)
    if not group:
        raise HTTPException(status_code=404, detail="Unknown port group")
    return group


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    _snapshot_or_503()
    return {"status": "ok"}


@app.get("/api/meta")
def meta() -> dict[str, Any]:
    snapshot = _snapshot_or_503()
    return {
        "revision": snapshot["revision"], "schema_version": snapshot["schema_version"],
        "snapshot_date": snapshot["snapshot_date"], "generated_at": snapshot["generated_at"],
        "device_count": len(snapshot["devices"]), "interconnect_count": len(snapshot["interconnects"]),
    }


@app.get("/api/devices")
def devices() -> list[dict[str, Any]]:
    return _snapshot_or_503()["devices"]


@app.get("/api/compatible")
def compatible(
    device_id: str = Query(..., min_length=1, max_length=128),
    port_group_id: str = Query(..., min_length=1, max_length=64),
) -> list[dict[str, Any]]:
    snapshot = _snapshot_or_503()
    cache_key = (snapshot["revision"], device_id, port_group_id)
    with _compat_cache_lock:
        cached = _compat_cache.get(cache_key)
        if cached is not None:
            _compat_cache.move_to_end(cache_key)
            return cached

    device = _find_device(snapshot, device_id)
    group = _find_group(device, port_group_id)
    result = []
    for item in snapshot["interconnects"]:
        ok, confidence, reasons = catalog.compatible(group, item)
        if ok:
            result.append({**item, "compatibility_confidence": confidence, "compatibility_reasons": reasons})
    result = sorted(result, key=lambda x: (_speed_gbps(x.get("speed")) or 0, x.get("model", "")), reverse=True)

    with _compat_cache_lock:
        _compat_cache[cache_key] = result
        _compat_cache.move_to_end(cache_key)
        while len(_compat_cache) > COMPAT_CACHE_MAX_ENTRIES:
            _compat_cache.popitem(last=False)
    return result
