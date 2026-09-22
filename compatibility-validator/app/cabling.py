"""Installation rows and one label per physical cable termination."""

import hashlib
import json


def build_cabling(snapshot, project, validation):
    products = {p["id"]: p for p in snapshot["interconnects"]}
    devices = {d["id"]: d for d in snapshot["devices"]}
    locations = {p.instance_id: p.model_dump(exclude={"instance_id"}) for p in project.cabling.locations}
    port_labels = {(p.instance_id, p.port_group_id, p.port_number): p.label for p in project.cabling.port_labels}
    settings = {c.entry_id: c for c in project.cabling.cables}
    validations = {r["id"]: r for r in validation["results"]}
    sku_lengths = {s["part_number"]: s.get("length_m") for p in snapshot["interconnects"] for s in p["skus"]}
    sku_lengths.update({s["part_number"]: s["length_m"] for s in snapshot.get("fiber_assemblies", [])})
    rows, labels = [], []

    def endpoint(selection, optical_port=None):
        device = devices.get(selection.device_id, {})
        item = products.get(selection.product_id, {})
        return {"instance_id": selection.instance_id, "model": device.get("model", selection.device_id),
            "port_group_id": selection.port_group_id, "port_number": selection.port_number,
            "port_label": port_labels.get((selection.instance_id, selection.port_group_id, selection.port_number)),
            "optical_port": optical_port, "mode_id": selection.mode_id,
            "product_pn": selection.part_number,
            "module_pn": selection.part_number if item.get("category") == "Transceiver" else None,
            "rack": locations.get(selection.instance_id, {}).get("rack"),
            "rack_u": locations.get(selection.instance_id, {}).get("rack_u")}

    def label(cable_id, suffix, local, peers, pn):
        value = {"label_id": cable_id + "/" + suffix, "cable_id": cable_id, "end": suffix,
                 "local": local, "peers": peers, "part_number": pn}
        labels.append(value)
        return value["label_id"]

    def add_row(entry, branch, cable_id, pn, a, b, a_label, b_label, progress):
        branch_id = branch.id if branch else None
        length = entry.length_m if entry.length_m is not None else sku_lengths.get(pn)
        config = entry.model_dump(exclude={"revision"})
        if "branches" in config:
            config["branches"].sort(key=lambda b: b["id"])
        # Whole-breakout changes invalidate its old leg declarations. Metadata and
        # status timestamps are deliberately not inferred from file import time.
        payload = {"entry": config, "branch": branch_id, "cable_id": cable_id,
                   "source": a, "destination": b, "part_number": pn, "length_m": length}
        fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()
        stored = next((p for p in progress if p.branch_id == branch_id), None)
        stale = bool(stored and (stored.installed or stored.checked) and stored.definition != fingerprint)
        result = validations[entry.id]
        row = {"entry_id": entry.id, "branch_id": branch_id,
            "termination": branch.termination if branch else None,
            "head_links": branch.head_links if branch else [],
            "head_optical_lanes": branch.head_optical_lanes if branch else [],
            "branch_optical_lanes": branch.branch_optical_lanes if branch else [],
            "cable_id": cable_id, "part_number": pn,
            "length_m": length,
            "documented_length_m": sku_lengths.get(pn), "fabric": entry.fabric,
            "source": a, "destination": b, "source_label": a_label, "destination_label": b_label,
            "validation_status": result["status"], "definition": fingerprint,
            "installed": bool(stored and stored.installed and not stale),
            "checked": bool(stored and stored.checked and not stale), "progress_stale": stale,
            "notes": stored.notes if stored else ""}
        rows.append(row)

    for kind, entry in [("connection", e) for e in project.connections] + [("breakout", e) for e in project.breakouts]:
        setting = settings.get(entry.id)
        cable_id = setting.cable_id if setting and setting.cable_id else "C-" + entry.id
        progress = setting.progress if setting else []
        if kind == "connection":
            optical = any(products.get(s.product_id, {}).get("category") == "Transceiver" for s in (entry.a, entry.b))
            pn = entry.fiber_part_number if optical else entry.a.part_number
            a, b = endpoint(entry.a), endpoint(entry.b)
            al, bl = label(cable_id, "A", a, [b], pn), label(cable_id, "B", b, [a], pn)
            add_row(entry, None, cable_id, pn, a, b, al, bl, progress)
        else:
            optical = entry.topology == "optical"
            pn = entry.optical_fanout.part_number if optical and entry.optical_fanout else None if optical else entry.head.part_number
            heads = {}
            ports = set(b.head_optical_port if optical else 0 for b in entry.branches)
            if optical and entry.optical_fanout:
                ports.update(range(1, entry.optical_fanout.head_ports + 1))
            for port in sorted(ports):
                a = endpoint(entry.head, port or None)
                peers = [endpoint(b.selection) for b in entry.branches if not optical or b.head_optical_port == port]
                heads[port] = (a, label(cable_id, "H" + (str(port) if optical else ""), a, peers, pn))
            for branch in sorted(entry.branches, key=lambda b: (b.termination, b.id)):
                a, al = heads[branch.head_optical_port if optical else 0]
                b = endpoint(branch.selection)
                bl = label(cable_id, "BR-" + branch.id, b, [a], pn)
                add_row(entry, branch, cable_id, pn, a, b, al, bl, progress)
    missing = []
    for row in rows:
        for side in ("source", "destination"):
            end = row[side]
            if not end["rack"]:
                missing.append(f"{row['cable_id']}: rack missing for {end['instance_id']}.")
            if not end["port_label"]:
                missing.append(f"{row['cable_id']}: verify physical port label for {end['instance_id']}/{end['port_group_id']}/{end['port_number']}.")
        if not row["part_number"]:
            missing.append(f"{row['cable_id']}: cable/harness ordering PN is unknown.")
        if row["length_m"] is None:
            missing.append(f"{row['cable_id']}: actual cable/path length is unknown.")
    issues = list(dict.fromkeys(missing))
    return {"scope": "cabling-plan", "name": project.name, "revision": snapshot["revision"],
        "status": validation["status"], "provisional": validation["status"] != "compatible" or bool(issues),
        "rows": rows, "labels": labels, "issues": issues,
        "summary": {"cables": len(project.connections) + len(project.breakouts), "legs": len(rows), "labels": len(labels),
            "installed": sum(r["installed"] for r in rows), "checked": sum(r["checked"] for r in rows),
            "stale_confirmations": sum(r["progress_stale"] for r in rows)},
        "notes": ["Installed and checked are user declarations for this exact installation definition; they do not change compatibility or manufacturer qualification.",
            "A breakout is one assembly: rows describe its legs, and labels identify the shared head and each physical branch.",
            "Named port labels are user-supplied markings; the catalog validation still uses the physical group and 1-based cage ordinal.",
            "Project JSON preserves locations, cable IDs, port labels and installation progress. PDF and XLSX are report snapshots."]}


def endpoint_text(end, model=False):
    rack = end["rack"] or "Rack unknown"
    if end["rack_u"] is not None:
        rack += " / U" + str(end["rack_u"])
    port = end["port_label"] or "Label unconfirmed"
    port += f" ({end['port_group_id']}/{end['port_number']})"
    if end["optical_port"]:
        port += f" / optical {end['optical_port']}"
    parts = [rack, end["instance_id"], port]
    if model:
        parts += [end["model"], "Mode: " + (end["mode_id"] or "auto")]
        if end["module_pn"]:
            parts.append("Module PN: " + end["module_pn"])
    return "\n".join(parts)
