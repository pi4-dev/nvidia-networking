"""Scoped hardware facts and qualification; lab evidence never implies vendor support."""

from copy import deepcopy

from .models import PortGroup, numeric_version


def effective_host(snapshot, selection):
    device = next((d for d in snapshot["devices"] if d["id"] == selection.device_id), None)
    if not device:
        raise KeyError("Unknown device")
    group = next((g for g in device["port_groups"] if g["id"] == selection.port_group_id), None)
    if not group:
        raise KeyError("Unknown port group")
    profile = None
    group = deepcopy(group)
    if selection.hardware_profile_id:
        profile = next((p for p in snapshot.get("hardware_profiles", []) if p["id"] == selection.hardware_profile_id), None)
        if not profile or profile["device_id"] != device["id"]:
            raise KeyError("Hardware profile does not belong to the selected device")
        port = next((p for p in profile["ports"] if p["port_group_id"] == group["id"]), None)
        if not port:
            raise KeyError("Port group is outside the selected hardware profile")
        for field in ("module_speed_gbps", "count", "fabrics", "modes"):
            if port.get(field):
                group[field] = deepcopy(port[field])
        group["hardware_evidence"] = deepcopy(port["evidence"])
    return device, group, profile


def validate_hardware_catalog(snapshot):
    """Reject dangling or contradictory overlays before activating a snapshot."""
    from .models import HostSelection

    products = {p["id"]: p for p in snapshot["interconnects"]}
    all_pns = {pn for p in products.values() for pn in p["part_numbers"]}
    for profile in snapshot["hardware_profiles"]:
        groups = {}
        for port in profile["ports"]:
            _, group, _ = effective_host(snapshot, HostSelection(device_id=profile["device_id"],
                port_group_id=port["port_group_id"], hardware_profile_id=profile["id"]))
            # Retain canonical connector/fixed-port restrictions; overrides cannot change them.
            PortGroup.model_validate({k: v for k, v in group.items() if k in PortGroup.model_fields})
            for field in port["evidence"]:
                if not field.startswith("modes.") and (group.get(field) is None or group.get(field) == []):
                    raise ValueError("evidence cannot annotate an unknown inherited fact")
            groups[group["id"]] = group
        for q in profile["qualifications"]:
            group = groups.get(q["port_group_id"])
            if not group or not set(q["mode_ids"]).issubset({m["id"] for m in group["modes"]}):
                raise ValueError("qualification references an absent hardware port/mode")
            if not set(q["product_ids"]).issubset(products) or not set(q["part_numbers"]).issubset(all_pns):
                raise ValueError("qualification references an absent product/PN")
            if q["product_ids"] and q["part_numbers"] and not set(q["part_numbers"]).issubset(
                    {pn for pid in q["product_ids"] for pn in products[pid]["part_numbers"]}):
                raise ValueError("qualification PN is outside its product scope")
            if group["fabrics"] and q["fabric"] not in group["fabrics"]:
                raise ValueError("qualification fabric outside the selected hardware port")
    if all_pns.intersection(f["part_number"] for f in snapshot["fiber_assemblies"]):
        raise ValueError("fiber PN duplicates an interconnect PN")


def gap(code, message, action):
    return {"code": code, "message": message, "action": action}


def identity_checks(profile, runtime):
    checks = []
    if profile:
        for field, fact in profile["identity"].items():
            observed = getattr(runtime, field)
            if observed:
                checks.append({"code": "hardware." + field,
                    "state": "pass" if observed == fact["value"] else "fail", "required": True,
                    "message": f"Observed {field}: {observed}; profile: {fact['value']}.",
                    "source_url": fact["evidence"]["source_url"]})
    return checks


def inspect_hardware(snapshot, selection):
    device, group, profile = effective_host(snapshot, selection)
    facts, gaps = [], []
    if profile:
        for field, fact in profile["identity"].items():
            facts.append({"field": field, **fact})
    else:
        gaps.append(gap("hardware.profile", "No exact hardware profile selected.",
                        "Read the board OPN/SKU and select its matching profile; add a sourced profile if absent."))
    evidence = group.get("hardware_evidence", {})
    for field in ("connector_family", "accepted_connector_families", "accepted_interface_types", "pluggable", "module_speed_gbps", "count", "fabrics"):
        value = group.get(field)
        facts.append({"field": field, "value": value, "evidence": evidence.get(field), "source_url": group.get("source_url")})
        if value is None or value == []:
            if field == "accepted_interface_types" and group["connector_family"] != "OSFP":
                continue
            gaps.append(gap("hardware." + field, f"{field} is not documented.", "Add the exact board's port specification with its source, scope and verification date."))
    if not group["modes"]:
        gaps.append(gap("hardware.modes", "No explicit port modes.", "Verify per-port links and speed in the board's supported port configurations."))
    for mode in group["modes"]:
        if selection.mode_id and mode["id"] != selection.mode_id:
            continue
        facts.append({"field": "modes." + mode["id"], "value": mode,
                      "evidence": evidence.get("modes." + mode["id"]), "source_url": group.get("source_url")})
        for key in ("electrical_lanes", "lane_rate_gbps", "fec"):
            if not mode.get(key):
                gaps.append(gap("hardware.modes." + mode["id"] + "." + key,
                    f"{mode['id']}: {key} is missing.", "Check the board and module electrical specifications; record the documented setting."))
    runtime = selection.runtime.model_dump()
    for field in (profile or {}).get("required_context", []):
        if not runtime[field]:
            gaps.append(gap("runtime." + field, f"Observed {field} has not been provided.",
                            "Read this value from the installed adapter/host and enter it in the runtime fields."))
    if not (profile or {}).get("qualifications"):
        gaps.append(gap("hardware.qualification", "No product-specific firmware/OS qualification evidence.",
                        "Add the manufacturer's support entry or an internal lab report, scoped to this OPN, product, fabric, mode and software versions."))
    undated = [f["field"] for f in facts if f["value"] and not f.get("evidence")]
    if undated:
        gaps.append(gap("hardware.provenance", "Some inherited catalog facts have no verification date: " + ", ".join(undated),
                        "Reverify the original source and add dated evidence in the exact hardware profile."))
    return {"revision": snapshot["revision"], "device": device["model"], "profile": profile,
            "effective_port": group, "runtime": runtime, "facts": facts, "gaps": gaps,
            "checks": identity_checks(profile, selection.runtime)}


def version_matches(value, scope):
    if not value:
        return False
    if scope["versions"]:
        return value in scope["versions"]
    parsed = numeric_version(value)
    return parsed is not None and (not scope["minimum"] or parsed >= numeric_version(scope["minimum"])) and (
        not scope["maximum"] or parsed <= numeric_version(scope["maximum"]))


def qualify(snapshot, selection, item, fabric, mode_id):
    _, _, profile = effective_host(snapshot, selection)
    checks = identity_checks(profile, selection.runtime)
    runtime = selection.runtime.model_dump()
    missing = [k for k in (profile or {}).get("required_context", []) if not runtime[k]]
    matches = []
    for q in (profile or {}).get("qualifications", []):
        if q["port_group_id"] != selection.port_group_id or q["fabric"] != fabric:
            continue
        if q["product_ids"] and item["id"] not in q["product_ids"]:
            continue
        if q["part_numbers"] and getattr(selection, "part_number", None) not in q["part_numbers"]:
            continue
        if q["mode_ids"] and mode_id not in q["mode_ids"]:
            continue
        # A runtime field declared relevant by the board profile also needs
        # qualification scope; merely entering a version cannot confirm it.
        if any(not q.get(k) and k not in profile["identity"] for k in profile["required_context"]):
            continue
        if any(q[k] and q[k] != runtime[k] for k in ("psid", "os_name")):
            continue
        if any(q[k] and not version_matches(runtime[k], q[k]) for k in ("firmware", "os_version")):
            continue
        matches.append(q)
    denied = [q for q in matches if q["outcome"] == "unsupported"]
    supported = [q for q in matches if q["outcome"] == "supported"]
    manufacturer = [q for q in supported if q["evidence"]["kind"] == "manufacturer"]
    lab = [q for q in supported if q["evidence"]["kind"] == "lab"]
    mismatch = any(c["state"] == "fail" for c in checks)
    status = ("unsupported" if denied or mismatch else "unknown" if missing else
              "manufacturer-confirmed" if manufacturer else "lab-tested" if lab else "unknown")
    message = {"unsupported": "Explicit unsupported qualification or hardware identity mismatch.",
        "unknown": "No applicable qualification. Missing/untested versions are unknown, not automatically unsupported.",
        "manufacturer-confirmed": "Manufacturer qualification applies to the selected hardware, product and runtime scope.",
        "lab-tested": "Internal lab evidence applies; manufacturer qualification is not established."}[status]
    if missing:
        message += " Missing runtime: " + ", ".join(missing) + "."
    if denied and supported:
        message += " Conflicting qualification records require review."
    checks.append({"code": "hardware.qualification", "state": "fail" if status == "unsupported" else
                   "pass" if status == "manufacturer-confirmed" else "unknown",
                   "required": status != "lab-tested", "message": message,
                   "source_url": matches[0]["evidence"]["source_url"] if matches else None})
    return {"status": status, "manufacturer_confirmed": bool(manufacturer) and status == "manufacturer-confirmed",
            "lab_tested": bool(lab), "records": matches, "missing_runtime": missing, "checks": checks}


def actionable_gaps(checks):
    actions = {"fec": "Verify a common FEC setting in the host and module documentation.",
        "qualification": "Record exact OPN/PSID, firmware and OS; add a scoped manufacturer support entry or lab report.",
        "pinout": "Verify both module receptacles, cable gender, Type A/B polarity and lane mapping against drawings.",
        "reach": "Verify this fiber grade and actual assembly length against both modules' reach tables.",
        "sku": "Select a documented ordering part number with its exact length.",
        "mode": "Verify and configure a supported link count and per-link speed on both ports."}
    return [gap(c["code"], c["message"], next((v for k, v in actions.items() if k in c["code"]),
                "Verify this parameter in the exact hardware specification and add a dated, scoped source."))
            for c in checks if c["state"] == "unknown"]
