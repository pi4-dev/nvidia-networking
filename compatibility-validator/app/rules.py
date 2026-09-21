"""Explainable host-port and single-link checks; no missing fact implies a pass."""

from itertools import product

from .models import ConnectionRequest, FiberCable
from .hardware import actionable_gaps, effective_host, qualify

RANK = {"compatible": 0, "conditional": 1, "unknown": 2, "incompatible": 3}


def check(code, state, message, source=None, required=True):
    return {"code": code, "state": state, "message": message,
            "source_url": source, "required": required}


def decide(checks):
    if any(c["state"] == "fail" for c in checks):
        return "incompatible"
    if any(c["state"] == "unknown" and c["required"] for c in checks):
        return "unknown"
    if any(c["state"] == "unknown" for c in checks):
        return "conditional"
    return "compatible"


def choose(results):
    return min(results, key=lambda r: (RANK[r["status"]], sum(c["state"] != "pass" for c in r["checks"])))


def evaluate_endpoint(group, item, endpoint, fabric=None, mode_id=None):
    checks = []
    source = group.get("source_url")
    item_source = item.get("source_url")
    pluggable = group.get("pluggable")
    checks.append(check("port.pluggable", "unknown" if pluggable is None else ("pass" if pluggable else "fail"),
                        "Pluggable port confirmed." if pluggable else "Port is fixed or its pluggable status is unknown.", source))
    # Lifecycle is deliberately separate from physical interoperability.
    checks.append(check("product.lifecycle", "pass" if item.get("status") == "active" else "unknown",
                        f"Product lifecycle: {item.get('status', 'unknown')}.", item_source, required=False))
    gf, pf = set(group.get("fabrics") or []), set(item.get("fabric_compatibility") or [])
    if not gf or not pf:
        state, message = "unknown", "Fabric support is missing for the port or product."
    elif fabric:
        state = "pass" if fabric in gf.intersection(pf) else "fail"
        message = f"Requested fabric {fabric}: port {sorted(gf)}, product {sorted(pf)}."
    else:
        state = "pass" if gf.intersection(pf) else "fail"
        message = f"Common fabrics: {', '.join(sorted(gf.intersection(pf))) or 'none'}."
    checks.append(check("port.fabric", state, message, item_source))
    accepted = group.get("accepted_connector_families") or []
    family = endpoint.get("connector_family") if endpoint else None
    checks.append(check("port.connector", "unknown" if not accepted or not family else ("pass" if family in accepted else "fail"),
                        f"Endpoint family {family or 'unknown'}; accepted: {', '.join(accepted) or 'unknown'}.", source))
    match_type = "unknown"
    if endpoint:
        match_type = ("exact" if family == group.get("connector_family") else "backward-compatible") if family in accepted else "mismatch"
        if family == "OSFP" and group.get("connector_family") == "OSFP":
            mechanics = group.get("accepted_interface_types") or []
            actual = endpoint.get("interface_type")
            if not mechanics or actual == "OSFP":
                state = "unknown"
                match_type = "unknown"
            else:
                state = "pass" if actual in mechanics else "fail"
                if state == "fail":
                    match_type = "mismatch"
            checks.append(check("port.mechanics", state, f"OSFP shell {actual}; accepted: {', '.join(mechanics) or 'not documented'}.", source))
    if not item.get("speed_gbps"):
        checks.append(check("product.speed", "unknown", "Product aggregate rate is not documented.", item_source))
    else:
        checks.append(check("product.speed", "pass", f"Product aggregate rate: {item['speed_gbps']}G.", item_source))
    gm = [m for m in group.get("modes", []) if not fabric or not m.get("fabrics") or fabric in m["fabrics"]]
    if mode_id:
        gm = [m for m in gm if m["id"] == mode_id]
    em = [m for m in (endpoint or {}).get("modes", []) if not fabric or not m.get("fabrics") or fabric in m["fabrics"]]
    matches = [(g, e) for g in gm for e in em if (g["links"], g["speed_gbps"]) == (e["links"], e["speed_gbps"])]
    if mode_id and not gm:
        checks.append(check("port.mode", "fail", "Selected port mode does not exist in this profile.", source))
    elif not gm or not em:
        checks.append(check("port.mode", "unknown", "Explicit link count and per-link rate are missing.", source))
    else:
        checks.append(check("port.mode", "pass" if matches else "fail",
                            f"Port modes: {', '.join(m['id'] for m in gm)}; endpoint modes: {', '.join(m['id'] for m in em)}.", source))
    capacity = group.get("module_speed_gbps")
    if not capacity or not em:
        checks.append(check("port.capacity", "unknown", "Per-cage or endpoint capacity is not documented.", source))
    else:
        checks.append(check("port.capacity", "pass" if any(m["links"] * m["speed_gbps"] <= capacity for m in em) else "fail",
                            f"Cage capacity: {capacity}G; checked the selected termination, not the whole cable assembly.", source))
    # These facts are optional in the host-fit view, but are promoted to required
    # checks for a complete A-to-B validation below.
    if matches:
        electrical = []
        for g, e in matches:
            candidate = []
            for field, label in (("electrical_lanes", "Electrical lane count"), ("lane_rate_gbps", "Electrical lane rate")):
                a, b = g.get(field), e.get(field)
                candidate.append(check("port." + field, "unknown" if a is None or b is None else ("pass" if a == b else "fail"),
                                       f"{label}: port {a if a is not None else 'unknown'}, module {b if b is not None else 'unknown'}.", source, False))
            ga, ea = set(g.get("fec") or []), set(e.get("fec") or [])
            candidate.append(check("port.fec", "unknown" if not ga or not ea else ("pass" if ga.intersection(ea) else "fail"),
                                   "Host/module FEC must have a documented common setting.", source, False))
            electrical.append({"status": decide(candidate), "checks": candidate, "mode": g["id"]})
        best = choose(electrical)
        checks.extend(best["checks"])
    for i, condition in enumerate((group.get("conditions") or []) + (item.get("conditions") or [])):
        checks.append(check(f"condition.{i}", "unknown", condition, item_source, False))
    if endpoint is None:
        checks.append(check("product.endpoints", "unknown", "No explicit endpoint profile is available.", item_source))
    return {"status": decide(checks), "checks": checks, "match_type": match_type,
            "endpoint_id": endpoint["id"] if endpoint else None,
            "endpoint_role": endpoint["role"] if endpoint else None,
            "matched_modes": sorted({g["id"] for g, _ in matches}),
            "scope": "host-port"}


def evaluate(group, item, fabric=None, mode_id=None, endpoint_id=None):
    endpoints = item.get("endpoints") or []
    if endpoint_id:
        endpoints = [e for e in endpoints if e["id"] == endpoint_id]
        if not endpoints:
            return {"status": "incompatible", "checks": [check("product.endpoint", "fail", "Requested termination does not exist.")],
                    "endpoint_id": None, "endpoint_role": None, "matched_modes": [], "match_type": "unknown", "scope": "host-port", "alternatives": []}
    evaluations = [evaluate_endpoint(group, item, end, fabric, mode_id) for end in endpoints or [None]]
    best = dict(choose(evaluations))
    best["alternatives"] = evaluations
    return best


def resolve(snapshot, selection):
    device, group, _ = effective_host(snapshot, selection)
    item = next((i for i in snapshot["interconnects"] if i["id"] == selection.product_id), None)
    if not item:
        raise KeyError("Unknown product")
    return device, group, item


def _selected_sku(item, pn, side):
    if not pn:
        return None, check(side + ".sku", "unknown", "Select an ordering part number.", item.get("source_url"))
    sku = next((s for s in item.get("skus", []) if s["part_number"] == pn), None)
    return sku, check(side + ".sku", "pass" if sku else "fail", f"Ordering part number: {pn}.", item.get("source_url"))


def _required_host_checks(evaluation, side):
    return [{**c, "code": side + "." + c["code"],
             "required": c["required"] or c["code"] in {"port.electrical_lanes", "port.lane_rate_gbps", "port.fec"}}
            for c in evaluation["checks"]]


def _optical_checks(a, b, request):
    checks = []
    fiber = request.fiber
    oa, ob = a.get("optics") or {}, b.get("optics") or {}
    if not fiber:
        return [check("link.fiber", "unknown", "Select fiber type, connector ends and verified pinout.")]
    for side, item, optics, connector in (("A", a, oa, fiber.connector_a), ("B", b, ob, fiber.connector_b)):
        medium = item.get("medium")
        checks.append(check(side + ".fiber_medium", "unknown" if not medium else ("pass" if medium == fiber.medium else "fail"),
                            f"Fiber medium {fiber.medium}; module medium {medium or 'unknown'}.", item.get("source_url")))
        actual = optics.get("connector")
        checks.append(check(side + ".optical_connector", "unknown" if not actual else ("pass" if actual == connector else "fail"),
                            f"Optical connector/polish: module {actual or 'unknown'}, cable {connector}.", item.get("source_url")))
        reach = item.get("reach") or {}
        limit = reach.get(fiber.fiber_type + "_m") if fiber.medium == "MM" else reach.get("max_m")
        checks.append(check(side + ".reach", "unknown" if request.length_m is None or limit is None else ("pass" if request.length_m <= limit else "fail"),
                            f"Requested length {request.length_m if request.length_m is not None else 'unknown'}m; documented {fiber.fiber_type} limit {limit if limit is not None else 'unknown'}m.", item.get("source_url")))
    for field, label in (("standard", "Optical standard"), ("lanes", "Optical lanes per connector"), ("lane_rate_gbps", "Optical lane rate"), ("wavelengths_nm", "Optical wavelengths")):
        av, bv = oa.get(field), ob.get(field)
        state = "unknown" if not av or not bv else ("pass" if av == bv else "fail")
        # Different standards may interoperate via a documented splitter/gearbox;
        # a same-shell guess is never accepted as that documentation.
        if field == "standard" and state == "fail":
            state = "unknown"
        checks.append(check("link." + field, state, f"{label}: A {av or 'unknown'}; B {bv or 'unknown'}."))
    fa, fb = set(oa.get("fec") or []), set(ob.get("fec") or [])
    checks.append(check("link.optical_fec", "unknown" if not fa or not fb else ("pass" if fa.intersection(fb) else "fail"),
                        "Optical FEC interoperability requires a documented common setting."))
    checks.append(check("link.pinout", "pass" if fiber.pinout_verified else "unknown",
                        "Connector gender, polarity and lane mapping verified by the user." if fiber.pinout_verified else "Verify connector gender, polarity and lane mapping against the cable drawing."))
    return checks


def _cable_fec(ga, gb, ea, eb, va, vb, fabric):
    combinations = []
    ga_modes = [m for m in ga["modes"] if m["id"] in va["matched_modes"]]
    gb_modes = [m for m in gb["modes"] if m["id"] in vb["matched_modes"]]
    for gma, gmb, ma, mb in product(ga_modes, gb_modes, (ea or {}).get("modes", []), (eb or {}).get("modes", [])):
        if any(m.get("fabrics") and fabric not in m["fabrics"] for m in (gma, gmb, ma, mb)):
            continue
        if any((g["links"], g["speed_gbps"]) != (e["links"], e["speed_gbps"]) for g, e in ((gma, ma), (gmb, mb))):
            continue
        sets = [set(m.get("fec") or []) for m in (ma, mb, gma, gmb)]
        fec_state = "unknown" if not all(sets) else ("pass" if set.intersection(*sets) else "fail")
        checks = [check("link.cable_fec", fec_state, "Both cable ends and hosts require one common FEC setting."),
                  check("link.cable_rate", "pass" if ma["speed_gbps"] == mb["speed_gbps"] else "fail", "Per-link rates must agree across the cable, including breakout legs.")]
        combinations.append({"status": decide(checks), "checks": checks})
    return choose(combinations)["checks"] if combinations else [check("link.cable_mode", "unknown", "A common cable operating mode could not be established.")]


def _mode_options(group, endpoint, requested):
    if requested:
        return [requested]
    rates = {(m["links"], m["speed_gbps"]) for m in (endpoint or {}).get("modes", [])}
    return [m["id"] for m in group["modes"] if (m["links"], m["speed_gbps"]) in rates] or [None]


def validate_connection(snapshot, request: ConnectionRequest):
    da, ga, a = resolve(snapshot, request.a)
    db, gb, b = resolve(snapshot, request.b)
    optical = a.get("category") == "Transceiver" and b.get("category") == "Transceiver"
    mixed = (a.get("category") == "Transceiver") != (b.get("category") == "Transceiver")
    fiber_checks, fiber_assembly = [], None
    if request.fiber_part_number:
        fiber_assembly = next((f for f in snapshot.get("fiber_assemblies", []) if f["part_number"] == request.fiber_part_number), None)
        if not fiber_assembly:
            raise KeyError("Unknown fiber assembly part number")
        if not optical:
            fiber_checks.append(check("link.fiber_assembly", "fail", "A separate fiber assembly requires two transceivers."))
        else:
            fields = {k: fiber_assembly[k] for k in ("medium", "fiber_type", "connector_a", "connector_b")}
            if request.fiber is None:
                request = request.model_copy(update={"fiber": FiberCable(**fields)})
            agrees = all(getattr(request.fiber, k) == v for k, v in fields.items())
            fiber_checks.append(check("link.fiber_assembly", "pass" if agrees else "fail",
                "Selected fiber properties must match its ordering number.", fiber_assembly["evidence"]["part_number"]["source_url"]))
            fiber_checks.append(check("link.fiber_length", "unknown" if request.length_m is None else
                "pass" if request.length_m == fiber_assembly["length_m"] else "fail",
                f"Fiber assembly {fiber_assembly['part_number']} is {fiber_assembly['length_m']}m long."))
    ends_a = [e for e in a.get("endpoints", []) if not request.a.endpoint_id or e["id"] == request.a.endpoint_id] or [None]
    ends_b = [e for e in b.get("endpoints", []) if not request.b.endpoint_id or e["id"] == request.b.endpoint_id] or [None]
    candidates = []
    for ea, eb in product(ends_a, ends_b):
        # All electrical and link checks must refer to the same pair of modes.
        # Choosing independent best host modes can otherwise invent a passing link.
        for mode_a, mode_b in product(_mode_options(ga, ea, request.a.mode_id), _mode_options(gb, eb, request.b.mode_id)):
            va = evaluate(ga, a, request.fabric, mode_a, ea["id"] if ea else request.a.endpoint_id)
            vb = evaluate(gb, b, request.fabric, mode_b, eb["id"] if eb else request.b.endpoint_id)
            checks = _required_host_checks(va, "A") + _required_host_checks(vb, "B") + fiber_checks
            sa, ca = _selected_sku(a, request.a.part_number, "A")
            sb, cb = _selected_sku(b, request.b.part_number, "B")
            checks += [ca, cb]
            if mixed:
                checks.append(check("link.topology", "fail", "Select two optical modules plus fiber, or both ends of one cable assembly."))
            elif optical:
                checks += _optical_checks(a, b, request)
                ma = [m for m in ga["modes"] if m["id"] in va["matched_modes"]]
                mb = [m for m in gb["modes"] if m["id"] in vb["matched_modes"]]
                rates_a, rates_b = {m["speed_gbps"] for m in ma}, {m["speed_gbps"] for m in mb}
                checks.append(check("link.rate", "unknown" if not rates_a or not rates_b else ("pass" if rates_a.intersection(rates_b) else "fail"),
                                    f"Per-link rates: A {sorted(rates_a)}G, B {sorted(rates_b)}G."))
                if (a.get("interface_count") or 1) > 1 or (b.get("interface_count") or 1) > 1:
                    checks.append(check("link.scope", "unknown", "This result covers one optical link; validate each remaining twin-port/breakout link separately.", required=False))
            else:
                checks += _cable_fec(ga, gb, ea, eb, va, vb, request.fabric)
                checks.append(check("link.assembly", "pass" if a["id"] == b["id"] else "fail", "Both ports must terminate the same cable assembly and variant."))
                checks.append(check("link.orientation", "unknown" if not ea or not eb else ("pass" if ea["id"] != eb["id"] else "fail"),
                                    f"Termination at device A: {(ea or {}).get('id', 'unknown')}; device B: {(eb or {}).get('id', 'unknown')}."))
                if sa and sb:
                    checks.append(check("link.same_sku", "pass" if sa["part_number"] == sb["part_number"] else "fail", "Use the same cable part number at both ends."))
                length = (sa or {}).get("length_m")
                checks.append(check("link.length", "unknown" if length is None or request.length_m is None else ("pass" if length == request.length_m else "fail"),
                                    f"Selected cable SKU length {length if length is not None else 'unknown'}m; requested {request.length_m if request.length_m is not None else 'unknown'}m."))
                if (ea or {}).get("role") == "branch" or (eb or {}).get("role") == "branch":
                    checks.append(check("link.scope", "unknown", "This result covers one breakout leg. Other legs need separate endpoint validation.", required=False))
            technical_status = decide(checks)
            qualification = {side: qualify(snapshot, selection, item, request.fabric, mode)
                for side, selection, item, mode in (("a", request.a, a, mode_a), ("b", request.b, b, mode_b))}
            for side, q in qualification.items():
                checks.extend({**c, "code": side.upper() + "." + c["code"]} for c in q["checks"])
            result = {"status": decide(checks), "technical_status": technical_status,
                      "qualification": qualification, "scope": "single-link", "checks": checks,
                      "orientation": {"a": va["endpoint_id"], "b": vb["endpoint_id"]},
                      "modes": {"a": mode_a, "b": mode_b}, "port_results": {"a": va, "b": vb}}
            candidates.append(result)
    result = choose(candidates)
    return {**result, "revision": snapshot["revision"], "selection": request.model_dump(),
            "gaps": actionable_gaps(result["checks"]), "fiber_assembly": fiber_assembly,
            "devices": {"a": da["model"], "b": db["model"]},
            "products": {"a": a["model"], "b": b["model"]}}
