"""Whole-project checks, physical ownership, deterministic BOM and bounded CSV import."""

import csv
import io
from collections import Counter

from pydantic import ValidationError

from .hardware import actionable_gaps
from .models import ConnectionRequest, FiberCable, Selection
from .rules import check, decide, validate_connection
from .topology import physical_checks, plain_selection, validate_breakout
from .topology_models import ProjectConnection, ProjectRequest


class StaleProject(ValueError):
    pass


def project_assignments(project):
    assignments = []
    for connection in project.connections:
        assignments += [(connection.id + ".A", connection.a), (connection.id + ".B", connection.b)]
    for breakout in project.breakouts:
        assignments.append((breakout.id + ".head", breakout.head))
        assignments.extend((breakout.id + "." + b.id, b.selection) for b in breakout.branches)
    return assignments


def build_bom(snapshot, project):
    products = {p["id"]: p for p in snapshot["interconnects"]}
    fibers = {f["part_number"]: f for f in snapshot.get("fiber_assemblies", [])}
    components, seen = [], {}

    def add(role, selected, reference, asset):
        item = products.get(selected.product_id)
        key = (asset, selected.product_id, selected.part_number)
        if key in seen:
            seen[key]["references"].add(reference)
            return
        known = bool(item and selected.part_number in item["part_numbers"])
        component = {"role": role, "part_number": selected.part_number, "model": item["model"] if item else selected.product_id,
                     "verified_ordering": known, "source_url": item.get("source_url") if item else None, "references": {reference}}
        components.append(component); seen[key] = component

    def module(selected, reference):
        add("module", selected, reference, (selected.instance_id, selected.port_group_id, selected.port_number))

    def fiber(pn, reference):
        entry = fibers.get(pn)
        components.append({"role": "fiber", "part_number": pn, "model": entry["model"] if entry else "Unresolved fiber assembly",
            "verified_ordering": bool(entry), "source_url": entry["evidence"]["part_number"]["source_url"] if entry else None,
            "references": {reference}})

    for connection in project.connections:
        a, b = products.get(connection.a.product_id), products.get(connection.b.product_id)
        optical_a = a and a["category"] == "Transceiver"
        optical_b = b and b["category"] == "Transceiver"
        if optical_a or optical_b:
            for selected, optical in ((connection.a, optical_a), (connection.b, optical_b)):
                if optical:
                    module(selected, connection.id)
                else:
                    add("unresolved", selected, connection.id, (connection.id, selected.instance_id))
            fiber(connection.fiber_part_number, connection.id)
        else:
            add("cable", connection.a, connection.id, (connection.id, "assembly"))
            if (connection.a.product_id, connection.a.part_number) != (connection.b.product_id, connection.b.part_number):
                add("cable", connection.b, connection.id, (connection.id, "conflicting-assembly"))
    for breakout in project.breakouts:
        if breakout.topology == "cable":
            add("cable", breakout.head, breakout.id, (breakout.id, "assembly"))
            for branch in breakout.branches:
                if (branch.selection.product_id, branch.selection.part_number) != (breakout.head.product_id, breakout.head.part_number):
                    add("cable", branch.selection, breakout.id, (breakout.id, "conflicting-assembly", branch.id))
        else:
            module(breakout.head, breakout.id)
            for branch in breakout.branches:
                module(branch.selection, breakout.id)
            fanout = breakout.optical_fanout
            components.append({"role": "harness", "part_number": fanout.part_number if fanout else None,
                "model": "Complete optical fanout harness", "verified_ordering": bool(fanout and fanout.part_number and fanout.evidence),
                "source_url": fanout.evidence.source_url if fanout and fanout.evidence else None, "references": {breakout.id}})
    grouped = {}
    for component in components:
        # Known ordering numbers are globally unique in the catalog. Do not merge
        # unrelated unresolved specifications just because both lack a PN.
        key = (component["part_number"], "") if component["part_number"] else (None, component["role"] + ":" + component["model"])
        row = grouped.setdefault(key, {"part_number": component["part_number"], "model": component["model"],
            "roles": set(), "required": 0, "verified_ordering": True, "references": set(), "source_urls": set()})
        row["required"] += 1
        row["roles"].add(component["role"])
        row["references"].update(component["references"])
        row["verified_ordering"] = row["verified_ordering"] and component["verified_ordering"]
        if component["source_url"]:
            row["source_urls"].add(component["source_url"])
    owned = {p.part_number: p.quantity for p in project.owned_parts}
    rows = []
    for row in grouped.values():
        available = owned.get(row["part_number"], 0)
        rows.append({**row, "roles": sorted(row["roles"]), "references": sorted(row["references"]),
            "source_urls": sorted(row["source_urls"]), "owned": available,
            "reused": min(row["required"], available), "to_buy": max(0, row["required"] - available)})
    rows.sort(key=lambda row: (row["part_number"] is None, row["part_number"] or row["model"]))
    consumed = {r["part_number"]: r["reused"] for r in rows if r["part_number"]}
    return {"rows": rows, "ordering_complete": all(r["verified_ordering"] for r in rows),
            "total_components": sum(r["required"] for r in rows), "reused": sum(r["reused"] for r in rows),
            "to_buy": sum(r["to_buy"] for r in rows),
            "unused_inventory": [{"part_number": pn, "quantity": qty - consumed.get(pn, 0)} for pn, qty in sorted(owned.items()) if qty > consumed.get(pn, 0)]}


def validate_project(snapshot, project):
    entries = [*(('connection', c) for c in project.connections), *(('breakout', b) for b in project.breakouts)]
    if any(entry.revision and entry.revision != snapshot["revision"] for _, entry in entries):
        raise StaleProject("A project entry refers to an older catalog revision; reload and revalidate the whole project")
    checks, allocations = physical_checks(snapshot, project_assignments(project))
    harnesses = {}
    for breakout in project.breakouts:
        fanout = breakout.optical_fanout
        if breakout.topology != "optical" or not fanout or not fanout.part_number:
            continue
        fingerprint = (fanout.head_ports, fanout.branch_count, breakout.length_m,
            tuple(sorted(fanout.fiber.model_dump(exclude={"pinout_verified"}).items())),
            tuple(sorted((b.termination, b.head_optical_port, tuple(b.head_optical_lanes), tuple(b.branch_optical_lanes)) for b in breakout.branches)))
        previous = harnesses.setdefault(fanout.part_number, (fingerprint, breakout.id))
        if previous[0] != fingerprint:
            checks.append(check("project.harness_identity", "fail", f"Harness PN {fanout.part_number} has contradictory lengths, connectors or lane maps in {previous[1]} and {breakout.id}."))
    results = []
    for kind, entry in entries:
        try:
            if kind == "connection":
                request = ConnectionRequest.model_validate({**{k: v for k, v in entry.model_dump().items() if k in ConnectionRequest.model_fields},
                    "a": plain_selection(entry.a).model_dump(), "b": plain_selection(entry.b).model_dump()})
                result = validate_connection(snapshot, request)
                # A full project cannot hide incomplete twin-port or single-leg scope.
                for c in result["checks"]:
                    if c["code"] == "link.scope":
                        c["required"] = True
                        c["message"] += " Represent a shared head as one complete breakout entry."
                result["status"] = decide(result["checks"])
                result["technical_status"] = decide([c for c in result["checks"] if ".hardware." not in c["code"]])
                result["gaps"] = actionable_gaps(result["checks"])
            else:
                result = validate_breakout(snapshot, entry)
        except KeyError as exc:
            result = {"status": "unknown", "checks": [check("catalog.lookup", "unknown", exc.args[0])], "gaps": []}
            result["gaps"] = actionable_gaps(result["checks"])
        results.append({"id": entry.id, "type": kind, "status": result["status"], "validation": result})
        checks.extend({**c, "code": entry.id + "." + c["code"]} for c in result["checks"])
    bom = build_bom(snapshot, project)
    if not bom["ordering_complete"]:
        checks.append(check("project.ordering", "unknown", "One or more required ordering numbers/specifications are unresolved; the BOM is provisional."))
    status = decide(checks)
    bom["provisional"] = status != "compatible" or not bom["ordering_complete"]
    counts = Counter(row["status"] for row in results)
    return {"revision": snapshot["revision"], "scope": "connection-project", "name": project.name,
            "status": status, "checks": checks, "gaps": actionable_gaps(checks), "results": results,
            "summary": {"connections": len(project.connections), "breakouts": len(project.breakouts),
                "branches": sum(len(b.branches) for b in project.breakouts),
                "device_instances": len({p["instance_id"] for p in allocations}),
                "physical_cages": len({(p["instance_id"], p["port_group_id"], p["port_number"]) for p in allocations}),
                "outcomes": {s: counts[s] for s in ("compatible", "conditional", "unknown", "incompatible")}},
            "port_allocations": allocations, "bom": bom, "project": project.model_dump(),
            "notes": ["Inventory is allocated once across the entire project, by exact ordering number.",
                "One breakout assembly and one shared head module are counted once. Unresolved/failed entries remain visible in the provisional BOM.",
                "A physical cage cannot be shared by separate entries. Combine all branches under a single breakout head.",
                "This validates declared connections and port ownership; it does not certify routing, redundancy, congestion or fabric-wide performance."]}


def csv_cell(value):
    text = str(value if value is not None else "")
    # Prevent formula execution when a catalog or imported label is opened in Excel.
    return "'" + text if text.lstrip().startswith(("=", "+", "-", "@")) or text.startswith(("\t", "\r", "\n")) else text


def bom_csv(report):
    out = io.StringIO(newline="")
    writer = csv.writer(out)
    writer.writerow(["part_number", "model", "roles", "required", "owned", "reused", "to_buy", "verified_ordering", "references", "project_status", "provisional"])
    for row in report["bom"]["rows"]:
        writer.writerow([csv_cell(v) for v in [row["part_number"], row["model"], ";".join(row["roles"]), row["required"],
            row["owned"], row["reused"], row["to_buy"], row["verified_ordering"], ";".join(row["references"]), report["status"], report["bom"]["provisional"]]])
    return out.getvalue()


RUNTIME_FIELDS = ("sku", "opn", "adapter_variant", "psid", "firmware", "os_name", "os_version")
HOST_FIELDS = ("instance", "device", "group", "port", "mode", "profile", "product", "end", "pn") + RUNTIME_FIELDS
CSV_FIELDS = ["id"] + [side + "_" + f for side in ("a", "b") for f in HOST_FIELDS] + ["fabric", "length_m", "fiber_pn", "fiber_type", "connector_a", "connector_b", "pinout_verified"]


def import_project_csv(snapshot, request):
    content = request.csv.lstrip("\ufeff")
    try:
        dialect = csv.Sniffer().sniff(content[:8192], delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    reader = csv.DictReader(io.StringIO(content, newline=""), dialect=dialect)
    fields = reader.fieldnames or []
    if len(fields) != len(set(fields)) or not fields or any(f not in CSV_FIELDS for f in fields):
        raise ValueError("CSV has duplicate, missing or unsupported column names; download the project CSV template")
    required = {"id", "fabric", "a_instance", "a_device", "a_port", "b_instance", "b_device", "b_port"}
    if not required.issubset(fields):
        raise ValueError("CSV is missing required columns: " + ", ".join(sorted(required - set(fields))))
    connections = []
    for number, row in enumerate(reader, 2):
        if len(connections) >= 200:
            raise ValueError("CSV exceeds 200 connections")
        if None in row or any(v is None for v in row.values()):
            raise ValueError(f"CSV row {number}: column count differs from header")
        row = {k: v.strip() for k, v in row.items()}
        def host(side):
            value = lambda key: row.get(side + "_" + key) or None
            found = [d for d in snapshot["devices"] if value("device") in (d["id"], d["model"])]
            if len(found) != 1:
                raise ValueError("device must be an exact catalog ID or unique model")
            device = found[0]
            group = value("group") or (device["port_groups"][0]["id"] if len(device["port_groups"]) == 1 else None)
            if not group:
                raise ValueError("physical group is required for a device with multiple groups")
            pid = value("product")
            if not pid:
                products = [p for p in snapshot["interconnects"] if value("pn") in p["part_numbers"]]
                if len(products) != 1:
                    raise ValueError("supply a product ID or a unique catalog part number")
                pid = products[0]["id"]
            port = value("port") or ""
            if not port.isascii() or not port.isdigit():
                raise ValueError("physical port ordinal must be an integer")
            return dict(instance_id=value("instance"), device_id=device["id"], port_group_id=group, port_number=int(port),
                        mode_id=value("mode"), hardware_profile_id=value("profile"), product_id=pid, endpoint_id=value("end"),
                        part_number=value("pn"), runtime={f: value(f) for f in RUNTIME_FIELDS})
        try:
            pinout = row.get("pinout_verified", "").lower()
            if pinout not in {"", "false", "true", "0", "1"}:
                raise ValueError("pinout_verified must be true/false or 1/0")
            fiber = None
            if row.get("fiber_type"):
                fiber = FiberCable(medium="SM" if row["fiber_type"] in {"OS2", "SM-unspecified"} else "MM",
                    fiber_type=row["fiber_type"], connector_a=row.get("connector_a", ""), connector_b=row.get("connector_b", ""), pinout_verified=pinout in {"true", "1"})
            connections.append(ProjectConnection(id=row["id"], a=host("a"), b=host("b"), fabric=row["fabric"],
                length_m=float(row["length_m"]) if row.get("length_m") else None, fiber=fiber,
                fiber_part_number=row.get("fiber_pn") or None, revision=request.revision))
        except ValidationError as exc:
            location = ".".join(str(x) for x in exc.errors()[0]["loc"])
            raise ValueError(f"CSV row {number}: invalid {location}") from None
        except ValueError as exc:
            raise ValueError(f"CSV row {number}: {exc}") from None
    return ProjectRequest(name=request.name, connections=connections, revision=request.revision)


def connection_csv(project):
    if project.breakouts:
        raise ValueError("Use project JSON to preserve complete breakout definitions")
    out = io.StringIO(newline=""); writer = csv.DictWriter(out, fieldnames=CSV_FIELDS)
    writer.writeheader()
    for connection in project.connections:
        row = {"id": connection.id, "fabric": connection.fabric, "length_m": connection.length_m, "fiber_pn": connection.fiber_part_number}
        for side in ("a", "b"):
            host = getattr(connection, side)
            mapping = dict(instance=host.instance_id, device=host.device_id, group=host.port_group_id, port=host.port_number,
                mode=host.mode_id, profile=host.hardware_profile_id, product=host.product_id, end=host.endpoint_id, pn=host.part_number, **host.runtime.model_dump())
            row.update({side + "_" + k: v for k, v in mapping.items()})
        if connection.fiber:
            row.update({k: getattr(connection.fiber, k) for k in ("fiber_type", "connector_a", "connector_b", "pinout_verified")})
        writer.writerow({k: csv_cell(v) for k, v in row.items()})
    return out.getvalue()
