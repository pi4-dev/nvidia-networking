"""Exercise a running container through its public API using only stdlib."""

import json
import io
import sys
import urllib.parse
import urllib.request
from zipfile import ZipFile


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
    split_product = "Copper|MCP7Y00-Nxxx|finned head"
    head = {"instance_id": "switch-01", "port_number": 1, "device_id": "profile:MQM9700-NS2F", "port_group_id": "ndr",
            "mode_id": "2x400", "product_id": split_product, "part_number": "MCP7Y00-N003"}
    branches = [{"id": f"branch-{i}", "termination": i, "head_links": [i], "selection": {
        "instance_id": f"cx8-{i}", "port_number": 1, "device_id": "supernic:ConnectX-8 SuperNIC", "port_group_id": "catalog-1",
        "hardware_profile_id": "900-9X81E-00EX-ST0", "mode_id": "1x400-ndr", "product_id": split_product,
        "part_number": "MCP7Y00-N003"}} for i in (1, 2)]
    fanout = {"head": head, "branches": branches, "fabric": "IB", "length_m": 3,
              "mapping_verified": False, "revision": catalog["meta"]["revision"]}
    split = request("/api/breakout", fanout)
    assert split["assigned_branches"] == split["expected_branches"] == 2
    assert split["status"] == "unknown"
    project_request = {"name": "Smoke project", "breakouts": [{**fanout, "id": "fanout-01"}],
        "owned_parts": [{"part_number": "MCP7Y00-N003", "quantity": 1}], "revision": catalog["meta"]["revision"]}
    project = request("/api/project", project_request)
    assert project["bom"]["rows"][0]["required"] == 1 and project["bom"]["to_buy"] == 0
    assert project["summary"]["physical_cages"] == 3
    plan = request("/api/project/cabling", project_request)
    assert plan["summary"]["cables"] == 1 and plan["summary"]["legs"] == 2 and plan["summary"]["labels"] == 3
    assert plan["status"] == "unknown" and plan["provisional"]
    for filename in ("cabling.pdf", "labels.pdf", "cabling.xlsx"):
        req = urllib.request.Request(base + "/api/project/" + filename, data=json.dumps(project_request).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as response:
            assert response.headers["X-Catalog-Revision"] == plan["revision"]
            contents = response.read()
            if filename.endswith(".pdf"):
                assert response.headers["Content-Type"] == "application/pdf"
                assert contents.startswith(b"%PDF-") and b"/FontFile2" in contents
            else:
                assert response.headers["Content-Type"].endswith("spreadsheetml.sheet")
                with ZipFile(io.BytesIO(contents)) as archive:
                    assert "xl/worksheets/sheet2.xml" in archive.namelist()
    print(f"Smoke passed: {len(catalog['devices'])} devices, {len(catalog['products'])} products, "
          f"{proposed['total_candidates']} proposals, complete breakout, project BOM, cabling PDF/XLSX and labels, revision {result['revision']}")


if __name__ == "__main__":
    main(sys.argv[1].rstrip("/"))
