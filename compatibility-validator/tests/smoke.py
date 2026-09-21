"""Exercise a running container through its public API using only stdlib."""

import json
import sys
import urllib.parse
import urllib.request


def main(base):
    def request(path, body=None):
        req = urllib.request.Request(base + path, data=None if body is None else json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.load(response)

    assert request("/healthz") == {"status": "ok"}
    catalog = request("/api/catalog")
    assert catalog["meta"]["catalog"]["state"] == "ready"
    assert catalog["devices"] and catalog["products"]
    devices = {d["model"]: d for d in catalog["devices"]}
    cable = next(p for p in catalog["products"] if p["model"] == "MCA4J80-Nxxx-FTF")

    def side(model):
        device = devices[model]
        return {"device_id": device["id"], "port_group_id": device["port_groups"][0]["id"],
                "product_id": cable["id"], "part_number": "980-9I601-00N003"}

    a, b = side("MQM9700-NS2F"), side("DGX B200")
    query = urllib.parse.urlencode({k: a[k] for k in ("device_id", "port_group_id")})
    evaluated = request("/api/evaluate?" + query)
    assert evaluated["revision"] == catalog["meta"]["revision"]
    assert any(p["validation"]["status"] == "incompatible" for p in evaluated["products"])
    result = request("/api/connection", {"a": a, "b": b, "fabric": "IB", "length_m": 3,
                                        "revision": catalog["meta"]["revision"]})
    assert result["orientation"] == {"a": "B", "b": "A"}
    assert result["status"] == "unknown"  # Unspecified FEC cannot become a pass.
    assert catalog["hardware_profiles"] and catalog["fiber_assemblies"]
    hardware = request("/api/hardware/inspect", {"device_id": "supernic:ConnectX-8 SuperNIC", "port_group_id": "catalog-1",
        "hardware_profile_id": "900-9X81E-00EX-ST0", "revision": catalog["meta"]["revision"]})
    assert hardware["effective_port"]["module_speed_gbps"] == 800 and hardware["gaps"]
    proposed = request("/api/recommendations", {"a": {k: a[k] for k in ("device_id", "port_group_id")},
        "b": {k: b[k] for k in ("device_id", "port_group_id")}, "fabric": "IB", "speed_gbps": 400,
        "minimum_length_m": 3, "revision": catalog["meta"]["revision"]})
    assert proposed["candidates"][0]["components"][0]["part_number"] == "980-9I601-00N003"
    assert any(c["technology"] == "optical" and c["ordering_complete"] for c in proposed["candidates"])
    assert all(c["validation"]["status"] == "unknown" for c in proposed["candidates"])
    print(f"Smoke passed: {len(catalog['devices'])} devices, {len(catalog['products'])} products, "
          f"{proposed['total_candidates']} proposals, revision {result['revision']}")


if __name__ == "__main__":
    main(sys.argv[1].rstrip("/"))
