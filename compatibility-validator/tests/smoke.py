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
    print(f"Smoke passed: {len(catalog['devices'])} devices, {len(catalog['products'])} products, revision {result['revision']}")


if __name__ == "__main__":
    main(sys.argv[1].rstrip("/"))
