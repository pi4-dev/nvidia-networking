"""Versioned, bounded catalog loading with atomic last-known-good activation."""

import hashlib
import json
import logging
import re
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import MAX_DATA_BYTES, MAX_PROFILE_BYTES
from .models import CatalogDocument, ProfileDocument

logger = logging.getLogger("uvicorn.error")


class CatalogUnavailable(RuntimeError):
    pass


def rows(table: dict) -> list[dict]:
    return [dict(zip(table["fields"], row)) for row in table["items"]]


def product_id(item: dict) -> str:
    return "|".join([item["category"], item["model"], item.get("variant") or "-"])


def speed_gbps(value: str | None) -> int | None:
    if not value:
        return None
    # ProductRow already validates the numeric rate. This is not used to infer
    # per-port capacity from device descriptions or aggregate adapter bandwidth.
    match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(G|T)(?:b/s|bE)?", value, re.I)
    return int(float(match[1]) * (1000 if match[2].upper() == "T" else 1)) if match else None


def connector_family(label: str) -> str:
    return label.split()[0].removesuffix("-finned").removesuffix("-flattop")


def _no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("JSON contains duplicate keys")
        result[key] = value
    return result


def read_json_limited(path: Path, limit: int) -> tuple[dict, bytes]:
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError("catalog input exceeds configured size limit")
    raw = json.loads(data, object_pairs_hook=_no_duplicate_keys,
                     parse_constant=lambda _: (_ for _ in ()).throw(ValueError("non-finite JSON number")))
    return raw, data


def build_devices(raw: dict, profiles: ProfileDocument) -> list[dict]:
    devices = {}
    sections = [("ethernet", "Ethernet switch", "ethernet_switching"),
                ("infiniband", "InfiniBand switch / appliance", "infiniband_and_appliances"),
                ("supernic", "SuperNIC / adapter", "supernic"), ("dpu", "DPU", "dpu")]
    for section, kind, bucket in sections:
        for item in rows(raw[section]):
            entry = raw["port_interface_compatibility"].get(bucket, {}).get(item["model"], {})
            id_ = f"{section}:{item['model']}"
            devices[id_] = {**item, "id": id_, "kind": kind, "source": "catalog",
                            "port_groups": [], "interface_compatibility": entry,
                            "source_url": entry.get("source_url")}
    for profile in profiles.profiles:
        value = profile.model_dump()
        original = devices.get(profile.id, {})
        if not original and profile.id.split(":", 1)[0] in {"ethernet", "infiniband", "dpu", "supernic"}:
            raise ValueError("port profile references an absent canonical device")
        entry = original.get("interface_compatibility", {})
        for group in value["port_groups"]:
            accepted = {connector_family(a) for a in entry.get("accepted_pluggables", [])}
            fixed = {connector_family(a) for a in entry.get("fixed_interfaces", [])}
            if entry:
                if (entry.get("pluggable") is False or group["connector_family"] in fixed) and group["pluggable"] is True:
                    raise ValueError("port profile conflicts with fixed catalog interface")
                if "accepted_pluggables" in entry and not set(group["accepted_connector_families"]).issubset(accepted):
                    raise ValueError("port profile accepts a family absent from the canonical catalog")
            group["compatibility_source"] = "explicit-profile-v2"
        devices[profile.id] = {**original, **value, "source": "explicit-profile"}
    for device in devices.values():
        device["validation_ready"] = any(g["pluggable"] is True for g in device["port_groups"])
        if not device["port_groups"]:
            device["warning"] = "No explicit port profile is available. Hardware compatibility is unknown."
    return sorted(devices.values(), key=lambda d: (d["kind"], d["model"]))


def build_products(raw: dict, profiles: ProfileDocument) -> list[dict]:
    linkx = raw["linkx"]
    products = {}
    pns = set()
    for bucket, fields in (("transceivers", "transceiver_fields"), ("aoc", "detailed_interconnect_fields"), ("copper", "detailed_interconnect_fields")):
        for item in rows({"fields": linkx[fields], "items": linkx[bucket]}):
            id_ = product_id(item)
            if id_ in products:
                raise ValueError("duplicate interconnect ID")
            if bucket == "transceivers":
                key = item["model"] + ("|" + item["variant"] if item["variant"] else "")
                item["fabric_compatibility"] = linkx["transceiver_fabric_compatibility"].get(key, linkx["transceiver_fabric_compatibility"].get(item["model"], []))
            detail = profiles.interconnect_details.get(id_)
            normalized = detail.model_dump() if detail else {"endpoints": [], "skus": [], "cable_type": "Unknown", "optics": None, "conditions": []}
            if detail:
                if set(s.part_number for s in detail.skus) != set(item["part_numbers"]):
                    raise ValueError("SKU profile must match the canonical part numbers")
                # Parse only to verify overlay integrity, never to invent port
                # capacity or modes at request time. A changed source must not
                # silently retain endpoint definitions from the older snapshot.
                declaration = item.get("interface_type")
                if declaration and detail.endpoints:
                    parts = [p.strip() for p in declaration.split("->")]
                    if item["category"] != "Transceiver" and len(parts) == 1:
                        parts *= 2
                    if len(parts) != len(detail.endpoints):
                        raise ValueError("endpoint profile disagrees with canonical termination count")
                    for part, endpoint in zip(parts, detail.endpoints):
                        match = re.fullmatch(r"(?:(\d+)x)?(.+)", part)
                        if int(match[1] or 1) != endpoint.count or match[2] != endpoint.interface_type:
                            raise ValueError("endpoint profile disagrees with canonical connector/mechanics")
                cap = speed_gbps(item.get("speed"))
                for endpoint in detail.endpoints:
                    if cap and any(m.capacity * endpoint.count > cap for m in endpoint.modes):
                        raise ValueError("interconnect endpoint mode exceeds assembly capacity")
                for sku in detail.skus:
                    if sku.length_m and (item.get("reach") or {}).get("max_m") and sku.length_m > item["reach"]["max_m"]:
                        raise ValueError("SKU length exceeds declared assembly reach")
            for pn in item["part_numbers"]:
                if pn in pns:
                    raise ValueError("part number assigned to multiple interconnect variants")
                pns.add(pn)
            products[id_] = {**item, **normalized, "source_url": item.get("source_url"), "id": id_, "speed_gbps": speed_gbps(item.get("speed"))}
    if set(profiles.interconnect_details).difference(products):
        raise ValueError("interconnect profile references an absent catalog product")
    # Legacy products remain searchable for diagnostics even when their detailed
    # electrical/mechanical specifications are absent from this snapshot.
    known = {p["model"] for p in products.values()}
    for item in rows({"fields": linkx["product_fields"], "items": linkx["no_longer_for_sale"]}):
        if item["model"] in known:
            continue
        id_ = product_id(item)
        products[id_] = {**item, "id": id_, "status": "no_longer_for_sale", "variant": None,
                         "speed_gbps": speed_gbps(item["speed"]), "endpoints": [], "skus": [], "part_numbers": [],
                         "fabric_compatibility": [], "medium": None, "reach": None, "optics": None,
                         "cable_type": "Unknown", "conditions": [], "source_url": raw["sources"].get("linkx_interconnects")}
    return sorted(products.values(), key=lambda p: (p["model"], p.get("variant") or ""))


class LiveCatalog:
    def __init__(self, data_path: Path, profile_path: Path):
        self.data_path = data_path
        self.profile_path = profile_path
        self._lock = threading.RLock()
        self._attempted_signature = None
        self._snapshot: dict[str, Any] | None = None
        self._last_success = None
        self._last_failure = None
        self._error_code = None
        self._next_retry = 0.0

    @staticmethod
    def _file_signature(path: Path):
        try:
            stat = path.stat()
            return stat.st_ino, stat.st_mtime_ns, stat.st_ctime_ns, stat.st_size
        except OSError:
            return None

    def _signature(self):
        return self._file_signature(self.data_path), self._file_signature(self.profile_path)

    def _load(self):
        raw, data_bytes = read_json_limited(self.data_path, MAX_DATA_BYTES)
        CatalogDocument.model_validate(raw)
        profiles_raw, profile_bytes = read_json_limited(self.profile_path, MAX_PROFILE_BYTES)
        profiles = ProfileDocument.model_validate(profiles_raw)
        return {"devices": build_devices(raw, profiles), "interconnects": build_products(raw, profiles),
                "revision": hashlib.sha256(data_bytes + b"\0" + profile_bytes).hexdigest()[:12],
                "schema_version": raw["schema_version"], "profiles_schema_version": profiles.schema_version,
                "snapshot_date": raw["snapshot_date"], "generated_at": raw["generated_at"]}

    def get(self):
        with self._lock:
            signature = self._signature()
            retry = self._snapshot is None and time.monotonic() >= self._next_retry
            if signature != self._attempted_signature or retry:
                try:
                    candidate = self._load()
                    if self._signature() != signature:
                        raise ValueError("catalog files changed during loading")
                except Exception:
                    self._last_failure = datetime.now(timezone.utc).isoformat()
                    self._error_code = "catalog_reload_rejected"
                    self._next_retry = time.monotonic() + 5
                    logger.exception("Catalog reload rejected")
                else:
                    self._snapshot = candidate
                    self._last_success = datetime.now(timezone.utc).isoformat()
                    self._error_code = None
                self._attempted_signature = signature
            if self._snapshot is None:
                raise CatalogUnavailable("No valid catalog snapshot")
            return self._snapshot

    def view(self) -> tuple[dict, dict]:
        """Return a snapshot and its freshness state from the same critical section."""
        with self._lock:
            snapshot = self.get()
            state = {"state": "degraded" if self._error_code else "ready", "last_successful_load": self._last_success,
                     "last_failed_load": self._last_failure, "error_code": self._error_code}
            return snapshot, state
