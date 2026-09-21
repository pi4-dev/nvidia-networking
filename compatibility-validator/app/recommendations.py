"""Bounded, deterministic selection of one cable or two modules plus fiber."""

from collections import Counter
from itertools import product

from .hardware import actionable_gaps, effective_host
from .models import ConnectionRequest, FiberCable, Selection
from .rules import RANK, check, decide, evaluate, validate_connection

MAX_EVALUATIONS = 3000


def _host_options(group, items, host, request):
    result = []
    for item in items:
        if item["status"] != "active":
            continue
        if item.get("fabric_compatibility") and request.fabric not in item["fabric_compatibility"]:
            continue
        for endpoint in item.get("endpoints") or [None]:
            endpoint_modes = (endpoint or {}).get("modes", [])
            if endpoint_modes and not any(m["speed_gbps"] == request.speed_gbps and
                    (not m.get("fabrics") or request.fabric in m["fabrics"]) for m in endpoint_modes):
                continue
            modes = [m for m in group["modes"] if m["speed_gbps"] == request.speed_gbps and
                     (not host.mode_id or m["id"] == host.mode_id) and
                     (not m.get("fabrics") or request.fabric in m["fabrics"])]
            if group["modes"] and not modes:
                continue
            for mode in modes or [None]:
                mode_id = mode["id"] if mode else host.mode_id
                endpoint_id = endpoint["id"] if endpoint else None
                fit = evaluate(group, item, request.fabric, mode_id, endpoint_id)
                if fit["status"] == "incompatible":
                    continue
                for sku in item.get("skus") or [{"part_number": None, "length_m": None}]:
                    if item["category"] != "Transceiver" and sku["length_m"] is not None and sku["length_m"] < request.minimum_length_m:
                        continue
                    selected = Selection(**{**host.model_dump(), "mode_id": mode_id}, product_id=item["id"],
                                         endpoint_id=endpoint_id, part_number=sku["part_number"])
                    result.append((item, sku, selected))
    return result


def _component(item, sku, side):
    return {"role": "module" if item["category"] == "Transceiver" else "cable", "side": side,
            "model": item["model"], "product_id": item["id"], "part_number": sku["part_number"],
            "length_m": sku.get("length_m"), "quantity": 1,
            "source_url": sku.get("source_url") or item.get("source_url"), "evidence": None}


def _fiber_options(snapshot, a, b, request):
    oa, ob = a.get("optics") or {}, b.get("optics") or {}
    matches = []
    for fiber in snapshot.get("fiber_assemblies", []):
        if fiber["length_m"] < request.minimum_length_m:
            continue
        if request.fiber_type != "any" and fiber["fiber_type"] != request.fiber_type:
            continue
        if any(item.get("medium") and item["medium"] != fiber["medium"] for item in (a, b)):
            continue
        if any(optics.get("connector") and optics["connector"] != fiber["connector_" + side]
               for optics, side in ((oa, "a"), (ob, "b"))):
            continue
        matches.append(fiber)
    if matches:
        return matches
    # Preserve a useful unresolved specification, never invent an ordering PN.
    medium = a.get("medium") or b.get("medium") or "SM"
    grade = request.fiber_type if request.fiber_type != "any" else "SM-unspecified" if medium == "SM" else "OM4"
    if (grade in {"OS2", "SM-unspecified"}) != (medium == "SM"):
        return []
    return [{"part_number": None, "model": "Fiber assembly: ordering number unresolved", "length_m": request.minimum_length_m,
             "medium": medium, "fiber_type": grade, "connector_a": oa.get("connector") or "Unspecified",
             "connector_b": ob.get("connector") or "Unspecified", "evidence": None}]


def _uses_required(components, request):
    return not request.reuse_part_number or any(c["part_number"] == request.reuse_part_number and
        (request.reuse_side == "either" or c["side"] in {request.reuse_side, "both"}) for c in components)


def _inventory(components, request):
    owned = {p.part_number: p.quantity for p in request.owned_parts}
    if request.reuse_part_number:
        owned.setdefault(request.reuse_part_number, 1)
    required = Counter(c["part_number"] for c in components if c["part_number"])
    result = [{"part_number": pn, "required": qty, "owned": owned.get(pn, 0),
               "reused": min(qty, owned.get(pn, 0)), "to_buy": max(0, qty - owned.get(pn, 0))}
              for pn, qty in sorted(required.items())]
    return result, sum(row["reused"] for row in result)


def recommend(snapshot, request):
    _, ga, _ = effective_host(snapshot, request.a)
    _, gb, _ = effective_host(snapshot, request.b)
    items = [i for i in snapshot["interconnects"] if
             request.technology == "any" or
             (request.technology == "optical" and i["category"] == "Transceiver") or
             (request.technology == "cable" and i["category"] != "Transceiver") or
             i.get("cable_type") == request.technology]
    options_a = _host_options(ga, items, request.a, request)
    options_b = _host_options(gb, items, request.b, request)
    candidates, seen = [], set()
    examined, rejected, truncated = 0, 0, False

    def proposals():
        for (a, sa, ha), (b, sb, hb) in product(options_a, options_b):
            optical = a["category"] == "Transceiver"
            if optical != (b["category"] == "Transceiver"):
                continue
            if not optical:
                if a["id"] != b["id"] or sa["part_number"] != sb["part_number"] or ha.endpoint_id == hb.endpoint_id:
                    continue
                components = [_component(a, sa, "both")]
                if _uses_required(components, request):
                    yield ConnectionRequest(a=ha, b=hb, fabric=request.fabric, length_m=sa["length_m"],
                        revision=snapshot["revision"]), components, a.get("cable_type", "cable")
            else:
                for fiber in _fiber_options(snapshot, a, b, request):
                    components = [_component(a, sa, "a"), {"role": "fiber", "side": "both", "quantity": 1,
                        **{k: fiber[k] for k in ("model", "part_number", "length_m", "evidence")},
                        "source_url": (fiber.get("evidence") or {}).get("part_number", {}).get("source_url")}, _component(b, sb, "b")]
                    if not _uses_required(components, request):
                        continue
                    cable = FiberCable(**{k: fiber[k] for k in ("medium", "fiber_type", "connector_a", "connector_b")})
                    yield ConnectionRequest(a=ha, b=hb, fabric=request.fabric, length_m=fiber["length_m"], fiber=cable,
                        fiber_part_number=fiber["part_number"], revision=snapshot["revision"]), components, "optical"

    for connection, components, technology in proposals():
        key = connection.model_dump_json()
        if key in seen:
            continue
        seen.add(key)
        if examined >= MAX_EVALUATIONS:
            truncated = True
            break
        examined += 1
        result = validate_connection(snapshot, connection)
        if technology == "optical" and not connection.fiber_part_number:
            result["checks"].append(check("link.fiber_sku", "unknown", "No matching fiber ordering number in this catalog; complete the fiber specification and source a verified assembly."))
        # Explicit requested per-link speed is also checked when the host modes are unknown.
        documented_rate = all(any(m["id"] == result["modes"][side] and m["speed_gbps"] == request.speed_gbps
                                 for m in group["modes"]) for side, group in (("a", ga), ("b", gb)))
        result["checks"].append(check("request.speed", "pass" if documented_rate else "unknown",
            f"Required bandwidth: {request.speed_gbps}G per link; aggregate/breakout bandwidth is not substituted."))
        result["status"] = decide(result["checks"])
        result["gaps"] = actionable_gaps(result["checks"])
        if result["status"] == "incompatible" or (result["status"] == "unknown" and not request.include_unknown):
            rejected += 1
            continue
        inventory, reused = _inventory(components, request)
        unknowns = sum(c["state"] == "unknown" for c in result["checks"])
        passed = sum(c["state"] == "pass" for c in result["checks"])
        mode_settings = {side: next((m for m in group["modes"] if m["id"] == result["modes"][side]), None)
                         for side, group in (("a", ga), ("b", gb))}
        candidates.append({"technology": technology, "components": components, "component_count": len(components),
            "ordering_complete": all(c["part_number"] for c in components), "length_m": connection.length_m,
            "inventory": inventory, "reused_count": reused,
            "evidence_summary": {"passed_checks": passed, "unknown_checks": unknowns,
                "manufacturer_qualified_hosts": sum(q["manufacturer_confirmed"] for q in result["qualification"].values()),
                "lab_tested_hosts": sum(q["lab_tested"] for q in result["qualification"].values())},
            "settings": mode_settings, "connection": connection.model_dump(), "validation": result})

    def ranking(c):
        evidence = (c["evidence_summary"]["unknown_checks"], -c["evidence_summary"]["manufacturer_qualified_hosts"],
                    -c["evidence_summary"]["lab_tested_hosts"])
        preferred = {"evidence": (*evidence, c["component_count"], -c["reused_count"]),
                     "fewest_components": (c["component_count"], *evidence, -c["reused_count"]),
                     "reuse": (-c["reused_count"], *evidence, c["component_count"])}[request.sort_by]
        return (RANK[c["validation"]["status"]], not c["ordering_complete"], *preferred,
                c["length_m"] if c["length_m"] is not None else float("inf"),
                tuple(p["part_number"] or "" for p in c["components"]), c["connection"]["a"]["mode_id"] or "")

    candidates.sort(key=ranking)
    return {"revision": snapshot["revision"], "scope": "single-link", "request": request.model_dump(),
            "candidates": candidates[:request.limit], "total_candidates": len(candidates), "examined": examined,
            "rejected": rejected, "truncated": truncated, "evaluation_limit": MAX_EVALUATIONS,
            "notes": ["Results describe one link or one breakout leg. Remaining legs require separate validation.",
                      "Ranking: compatibility status, complete ordering numbers, selected priority, shortest adequate assembly.",
                      "Unknown evidence must be resolved before treating a proposal as qualified."] +
                     (["Search limit reached; narrow the technology, port modes or required part number."] if truncated else []) +
                     (["No proposal meets these constraints in this catalog. Check speed, port mode, length and required PN; this is not proof that no solution exists."] if not candidates else [])}
