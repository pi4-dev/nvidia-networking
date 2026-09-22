"""Validate every physical termination in one fanout, with one explicit head mode."""

from collections import defaultdict

from .hardware import actionable_gaps, effective_host, qualify
from .models import ConnectionRequest, Selection
from .rules import (check, decide, evaluate, resolve, validate_connection,
                    _required_host_checks, _selected_sku)


def plain_selection(selected):
    return Selection.model_validate({k: v for k, v in selected.model_dump().items() if k in Selection.model_fields})


def selected_mode(group, selected):
    return next((m for m in group["modes"] if m["id"] == selected.mode_id), None)


def physical_checks(snapshot, assignments):
    """An instance is one device; its group/ordinal names exactly one cage."""
    checks, ports, instances, allocations = [], {}, {}, []
    for label, selection in assignments:
        key = (selection.instance_id, selection.port_group_id, selection.port_number)
        if key in ports:
            checks.append(check("ports.duplicate", "fail", f"{label} and {ports[key]} occupy the same cage: {key[0]}/{key[1]}/{key[2]}."))
        else:
            ports[key] = label
        signature = (selection.device_id, selection.hardware_profile_id)
        previous = instances.setdefault(selection.instance_id, (signature, {}, label))
        if previous[0] != signature:
            checks.append(check("ports.instance_identity", "fail", f"Device instance {selection.instance_id} has conflicting model or exact-board profiles ({previous[2]}, {label})."))
        for field, value in selection.runtime.model_dump().items():
            if value is not None:
                if field in previous[1] and previous[1][field] != value:
                    checks.append(check("ports.instance_runtime", "fail", f"Device instance {selection.instance_id} has conflicting {field} values."))
                previous[1][field] = value
        try:
            _, group, _ = effective_host(snapshot, selection)
        except KeyError:
            checks.append(check("ports.profile", "unknown", f"{label}: device/port profile could not be resolved."))
            capacity = None
        else:
            capacity = group.get("count")
            checks.append(check("ports.range", "unknown" if capacity is None else "pass" if selection.port_number <= capacity else "fail",
                f"{label}: cage {selection.port_number} in {selection.port_group_id}; documented cage count {capacity if capacity is not None else 'unknown'}.", group.get("source_url")))
        allocations.append({"reference": label, "instance_id": key[0], "device_id": selection.device_id,
            "hardware_profile_id": selection.hardware_profile_id, "port_group_id": key[1], "port_number": key[2],
            "mode_id": selection.mode_id, "group_cage_count": capacity})
    return checks, allocations


def endpoint_for(item, selected, role):
    if selected.endpoint_id:
        return next((e for e in item["endpoints"] if e["id"] == selected.endpoint_id), None)
    return next((e for e in item["endpoints"] if e["role"] == role), None)


def common_fec(sets, code, message):
    known = [s for s in sets if s]
    common = set.intersection(*known) if known else set()
    state = "fail" if known and not common else "unknown" if len(known) != len(sets) else "pass"
    return check(code, state, message), sorted(common) if state == "pass" else []


def _end_fec(endpoint, mode, fabric):
    if not endpoint or not mode:
        return set()
    alternatives = [e for e in endpoint["modes"] if (e["links"], e["speed_gbps"]) == (mode["links"], mode["speed_gbps"])
                    and (not e.get("fabrics") or fabric in e["fabrics"])
                    and all(e.get(k) is None or mode.get(k) is None or e[k] == mode[k] for k in ("electrical_lanes", "lane_rate_gbps"))
                    and (not e.get("fabrics") or not mode.get("fabrics") or set(e["fabrics"]) & set(mode["fabrics"]))]
    if not alternatives or any(not e.get("fec") for e in alternatives):
        return set()
    return set.union(*(set(e["fec"]) for e in alternatives))


def _optical_branch(snapshot, request, branch, head_item, head_group, item, group):
    head, tail = plain_selection(request.head), plain_selection(branch.selection)
    checks = []
    ports, qualification = {}, {}
    for side, selected, port, product in (("a", head, head_group, head_item), ("b", tail, group, item)):
        ports[side] = evaluate(port, product, request.fabric, selected.mode_id, selected.endpoint_id)
        checks += _required_host_checks(ports[side], side.upper())
        checks.append(_selected_sku(product, selected.part_number, side.upper())[1])
        checks.append(check(side + ".transceiver", "pass" if product["category"] == "Transceiver" else "fail", "Optical fanout requires a transceiver at every host."))
        qualification[side] = qualify(snapshot, selected, product, request.fabric, selected.mode_id)
    fanout = request.optical_fanout
    oa, ob = head_item.get("optics") or {}, item.get("optics") or {}
    if not fanout:
        checks.append(check("optical.harness", "unknown", "Supply the full optical harness specification and lane map."))
    else:
        for side, product, optics, connector in (("A", head_item, oa, fanout.fiber.connector_a), ("B", item, ob, fanout.fiber.connector_b)):
            medium = product.get("medium")
            checks.append(check(side + ".fiber_medium", "unknown" if not medium else "pass" if medium == fanout.fiber.medium else "fail", "Harness medium must match the module.", product.get("source_url")))
            actual = optics.get("connector")
            checks.append(check(side + ".optical_connector", "unknown" if not actual else "pass" if connector == actual else "fail", f"Harness connector {connector}; module connector {actual or 'unknown'}.", product.get("source_url")))
            reach = product.get("reach") or {}
            limit = reach.get("max_m") if fanout.fiber.medium == "SM" else reach.get(fanout.fiber.fiber_type + "_m")
            checks.append(check(side + ".reach", "unknown" if limit is None or request.length_m is None else "pass" if request.length_m <= limit else "fail", f"Whole optical path {request.length_m}m; documented reach {limit}m.", product.get("source_url")))
    for field in ("lane_rate_gbps", "wavelengths_nm"):
        av, bv = oa.get(field), ob.get(field)
        checks.append(check("optical." + field, "unknown" if not av or not bv else "pass" if av == bv else "fail", f"Optical {field}: head {av or 'unknown'}, branch {bv or 'unknown'}."))
    standards_equal = bool(oa.get("standard") and oa.get("standard") == ob.get("standard"))
    evidence = branch.interop_evidence
    checks.append(check("optical.standard", "pass" if standards_equal or evidence and evidence.kind == "manufacturer" else "unknown",
        "Verify per-lane interoperability; equal aggregate bandwidth is insufficient. " + (evidence.scope if evidence else "No scoped interoperability evidence supplied."),
        evidence.source_url if evidence else None, required=not (evidence and evidence.kind == "lab")))
    mapped_head, mapped_branch = branch.head_optical_lanes, branch.branch_optical_lanes
    checks.append(check("optical.lane_pairs", "unknown" if not mapped_head or not mapped_branch else
        "pass" if len(mapped_head) == len(mapped_branch) else "fail", "Each optical transmit/receive lane pair needs one mapped lane at the other end."))
    count = ob.get("lanes")
    coverage = set(mapped_branch)
    state = "unknown" if not count or not mapped_branch else "fail" if len(coverage) != len(mapped_branch) or max(coverage) > count else "pass" if coverage == set(range(1, count + 1)) else "unknown"
    checks.append(check("optical.branch_lanes", state, f"Branch optical lanes {mapped_branch}; documented lane count {count or 'unknown'}."))
    mode = selected_mode(group, branch.selection)
    needed = mode["links"] * mode["speed_gbps"] if mode else None
    supplied = len(mapped_head) * oa["lane_rate_gbps"] if mapped_head and oa.get("lane_rate_gbps") else None
    checks.append(check("optical.branch_bandwidth", "unknown" if needed is None or supplied is None else "pass" if needed == supplied else "fail", f"Mapped optical bandwidth {supplied}G; branch host mode needs {needed}G."))
    branch_ports = item.get("interface_count")
    if branch_ports is None or branch_ports > 1:
        checks.append(check("optical.branch_scope", "unknown", "The branch module has multiple or undocumented optical connectors; full remote connector coverage is not established."))
    technical_status = decide(checks)
    for side, q in qualification.items():
        checks.extend({**c, "code": side.upper() + "." + c["code"]} for c in q["checks"])
    return {"status": decide(checks), "technical_status": technical_status, "checks": checks,
            "qualification": qualification, "port_results": ports,
            "modes": {"a": head.mode_id, "b": tail.mode_id}, "scope": "breakout-branch"}


def validate_breakout(snapshot, request):
    _, head_group, head_item = resolve(snapshot, request.head)
    head_mode = selected_mode(head_group, request.head)
    head_end = endpoint_for(head_item, request.head, "head" if request.topology == "cable" else "module")
    global_checks, allocations = physical_checks(snapshot, [("head", request.head)] + [(b.id, b.selection) for b in request.branches])
    results, used_links, used_terminations, optical_lanes = [], [], [], []
    child_capacity = 0
    capacity_known = True
    fec_sets = [set((head_mode or {}).get("fec") or []), _end_fec(head_end, head_mode, request.fabric)]
    optical_fec_sets = [set((head_item.get("optics") or {}).get("fec") or [])]
    expected = None
    if request.topology == "cable":
        ends = [e for e in head_item["endpoints"] if e["role"] == "branch"]
        expected = ends[0]["count"] if len(ends) == 1 else None
        global_checks.append(check("breakout.head", "unknown" if not head_end else "pass" if head_end["role"] == "head" and head_end["count"] == 1 else "fail", "Select the single head termination of a documented breakout assembly."))
    elif request.optical_fanout:
        fanout = request.optical_fanout
        expected = fanout.branch_count
        global_checks.append(check("optical.harness_evidence", "pass" if fanout.evidence and fanout.evidence.kind == "manufacturer" else "unknown",
            "Harness ordering number, full path length, connector count and lane map need scoped evidence.", fanout.evidence.source_url if fanout.evidence else None,
            required=not (fanout.evidence and fanout.evidence.kind == "lab")))
        global_checks.append(check("optical.harness_pn", "pass" if fanout.part_number and fanout.evidence else "unknown", "Use the documented ordering number of the complete harness assembly."))
        if fanout.part_number and (any(f["part_number"] == fanout.part_number for f in snapshot.get("fiber_assemblies", [])) or
                                  any(fanout.part_number in p["part_numbers"] for p in snapshot["interconnects"])):
            global_checks.append(check("optical.harness_identity", "fail", "This ordering number already identifies a catalog transceiver, integrated cable or point-to-point fiber; it cannot also identify a separate passive fanout harness."))
        global_checks.append(check("optical.pinout", "pass" if fanout.fiber.pinout_verified else "unknown", "Verify harness gender, polarity and the complete Tx/Rx lane map against its drawing."))
        connectors = head_item.get("interface_count")
        global_checks.append(check("optical.head_ports", "unknown" if connectors is None else "pass" if connectors == fanout.head_ports else "fail", f"Harness covers {fanout.head_ports} head connectors; module documents {connectors} connectors."))
    global_checks.append(check("breakout.mapping", "pass" if request.mapping_verified else "unknown", "Physical termination labels and logical host links must be verified against the assembly drawing and configured port split."))
    for branch in request.branches:
        _, group, item = resolve(snapshot, branch.selection)
        mode = selected_mode(group, branch.selection)
        end = endpoint_for(item, branch.selection, "branch" if request.topology == "cable" else "module")
        if request.topology == "cable":
            head = plain_selection(request.head).model_copy(update={"endpoint_id": head_end["id"] if head_end else request.head.endpoint_id})
            tail = plain_selection(branch.selection).model_copy(update={"endpoint_id": end["id"] if end else branch.selection.endpoint_id})
            result = validate_connection(snapshot, ConnectionRequest(a=head, b=tail, fabric=request.fabric, length_m=request.length_m, revision=request.revision))
            # The complete fanout checks below replace the single-leg scope warning.
            result["checks"] = [c for c in result["checks"] if c["code"] != "link.scope"]
            result["checks"].append(check("breakout.branch_end", "unknown" if not end else "pass" if end["role"] == "branch" else "fail", "Each child must use a branch termination of the same assembly."))
        else:
            result = _optical_branch(snapshot, request, branch, head_item, head_group, item, group)
            optical_lanes.extend((branch.head_optical_port, lane) for lane in branch.head_optical_lanes)
            optical_fec_sets.append(set((item.get("optics") or {}).get("fec") or []))
        result["checks"].append(check("breakout.link_map", "unknown" if not branch.head_links or not mode else
            "pass" if len(branch.head_links) == mode["links"] else "fail", f"Head links {branch.head_links} map to {mode['links'] if mode else 'unknown'} links at branch {branch.id}."))
        result["checks"].append(check("breakout.link_rate", "unknown" if not mode or not head_mode else
            "pass" if mode["speed_gbps"] == head_mode["speed_gbps"] else "fail", "Every branch link must use the head mode's per-link rate."))
        used_links.extend(branch.head_links)
        used_terminations.append(branch.termination)
        if mode:
            child_capacity += mode["links"] * mode["speed_gbps"]
        else:
            capacity_known = False
        fec_sets.extend([set((mode or {}).get("fec") or []), _end_fec(end, mode, request.fabric)])
        result["status"] = decide(result["checks"])
        result["technical_status"] = decide([c for c in result["checks"] if ".hardware." not in c["code"]])
        result["gaps"] = actionable_gaps(result["checks"])
        results.append({"id": branch.id, "termination": branch.termination, "head_links": branch.head_links,
            "selection": branch.selection.model_dump(), "validation": result})
    duplicate_links = len(set(used_links)) != len(used_links)
    duplicate_ends = len(set(used_terminations)) != len(used_terminations)
    global_checks.append(check("breakout.termination_unique", "fail" if duplicate_ends else "pass", "Every physical branch termination must be assigned exactly once."))
    global_checks.append(check("breakout.termination_count", "unknown" if expected is None else
        "fail" if any(t > expected for t in used_terminations) or len(used_terminations) > expected else
        "pass" if set(used_terminations) == set(range(1, expected + 1)) else "unknown",
        f"Assigned {len(used_terminations)} branch terminations; complete assembly needs {expected if expected is not None else 'an undocumented number'}."))
    links = head_mode["links"] if head_mode else None
    global_checks.append(check("breakout.head_links", "fail" if duplicate_links or links and any(i > links for i in used_links) else
        "unknown" if links is None or set(used_links) != set(range(1, links + 1)) else "pass", f"Head link allocation {used_links}; selected mode has {links} links. No overlap or omitted links are allowed in a complete fanout."))
    head_capacity = head_mode["links"] * head_mode["speed_gbps"] if head_mode else None
    global_checks.append(check("breakout.bandwidth", "unknown" if not capacity_known or head_capacity is None else
        "fail" if child_capacity > head_capacity else "pass" if child_capacity == head_capacity else "unknown",
        f"Branches require {child_capacity if capacity_known else 'unknown'}G total; head mode provides {head_capacity}G. Per-link rate is checked separately."))
    if request.topology == "cable":
        fec_check, common = common_fec(fec_sets, "breakout.common_fec", "One documented FEC setting must work for the head and every cable branch simultaneously.")
    else:
        fec_check, common = common_fec(optical_fec_sets, "breakout.optical_fec", "One documented optical FEC setting must work on every passive optical path.")
        fanout = request.optical_fanout
        lanes = (head_item.get("optics") or {}).get("lanes")
        count = fanout.head_ports if fanout else None
        expected_lanes = {(p, lane) for p in range(1, (count or 0) + 1) for lane in range(1, (lanes or 0) + 1)}
        allocated = set(optical_lanes)
        state = "fail" if len(allocated) != len(optical_lanes) or expected_lanes and allocated - expected_lanes else "unknown" if not expected_lanes or allocated != expected_lanes else "pass"
        global_checks.append(check("optical.head_lane_map", state, "Every optical lane on every head connector must be mapped once; duplicate, out-of-range and unassigned lanes are detected."))
    global_checks.append(fec_check)
    checks = global_checks + [{**c, "code": b["id"] + "." + c["code"]} for b in results for c in b["validation"]["checks"]]
    return {"revision": snapshot["revision"], "scope": "complete-breakout", "status": decide(checks),
        "technical_status": decide([c for c in checks if ".hardware." not in c["code"]]),
        "checks": checks, "gaps": actionable_gaps(checks), "branches": results, "port_allocations": allocations,
        "expected_branches": expected, "assigned_branches": len(results), "common_fec": common,
        "head_mode": head_mode, "selection": request.model_dump(),
        "notes": ["All head and branch operating modes are explicit; independently valid branches do not imply a valid full fanout.",
                  "Port numbers are 1-based ordinals within the selected physical port group."]}
