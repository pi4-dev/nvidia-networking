# NVIDIA Networking Compatibility Validator

Interactive web application for validating NVIDIA LinkX transceivers and cable assemblies against NVIDIA switches, adapters and DGX port profiles using the repository's live `data/nvidia-interconnects.json` dataset.

## Web GUI

The application exposes a browser GUI at:

```text
http://localhost:8080/
```

The workflow is intentionally validation-only:

1. Select equipment category, device/system and physical port group.
2. Browse only active LinkX products that pass compatibility validation for that port group.
3. Filter products by model/part number, category, fabric and medium.
4. Select a transceiver, AOC or copper assembly.
5. Review validation confidence and the exact reasons why the product is accepted.
6. Review device, port and LinkX product details, including direct links to NVIDIA documentation and the cage/module compatibility source.

There is no BOM calculation, port quantity planning, cable-count calculation or endpoint-side quantity output.

## What it validates

The compatibility engine checks:

- product status (`active`)
- fabric compatibility (`ETH`, `IB`, `NVL` where applicable)
- host-side connector/form factor
- module/cage compatibility from schema v8 `port_interface_compatibility`
- exact OSFP mechanical variant (`finned` vs `flat-top`) when encoded or otherwise known by the explicit device profile
- module speed against advertised device port/module modes
- aggregate cage capacity, including twin-port 1.6T OSFP cases such as Quantum-X800

Compatibility confidence shown in the GUI:

- `exact` — exact mechanical/form-factor match
- `backward-compatible` — the catalog explicitly allows a different module generation in the selected cage

## Schema v8 module / cage compatibility

For schema v8 and newer, `data/nvidia-interconnects.json` is the authoritative source for device-side pluggable compatibility:

```text
port_interface_compatibility
  ethernet_switching
  infiniband_and_appliances
  dpu
  supernic
```

The validator consumes these fields directly:

- `pluggable`
- `accepted_pluggables`
- `fixed_interfaces`
- `source_url`
- `variants`
- `scope_note`

For devices with multiple physical cage families, `accepted_pluggables` is applied per matching form-factor class. Example: on SN5400 the QSFP-DD group uses the QSFP entries while the SFP28 group uses the SFP entry; the device-wide list is not blindly copied to every port group.

`fixed_interfaces` always wins over a device-level `pluggable=true`. This prevents fixed interfaces such as RJ45 or CPO interfaces from being treated as pluggable cages.

The GUI shows both the raw catalog list (`Catalog accepts`) and the effective per-port-group list (`Accepted modules`), together with the compatibility source link.

For older schema snapshots without `port_interface_compatibility`, the application retains a legacy form-factor fallback. This fallback is not used when schema v8 compatibility data exists for the selected device.

## DPU / SuperNIC support from schema v8

Schema v8 can make devices validation-ready even when the compact portfolio record does not contain physical port counts. The validator builds validation-only cage groups from `accepted_pluggables` without inventing quantities.

Examples include:

- BlueField-3 DPU: QSFP112 / QSFP56 / QSFP28
- BlueField-4 DPU: QSFP112 for the documented scope in the dataset
- ConnectX-8 / ConnectX-9 SuperNIC: separate OSFP (RHS cage) and QSFP112 variants

When a physical port count is not present in the source, the GUI displays `—` rather than inferring a value.

## OSFP mechanics

OSFP is treated separately because the cooling/mechanical variant matters. Explicit `RHS`, `flat` or `flattop` qualifiers map to flat-top modules, while explicit `IHS` or `finned` qualifiers map to finned modules.

For switch-side OSFP records where schema v8 currently states only `OSFP` without an IHS/RHS qualifier, the existing NVIDIA switch-side finned constraint is retained. DGX system profiles continue to carry their explicit server-side flat-top requirement.

## Device profiles

The canonical repository JSON now contains normalized cage/module data for switches, DPUs, SuperNICs and relevant appliances. `compatibility-validator/data/device-profiles.json` remains only as a small auditable overlay for system-level port profiles not represented in the canonical dataset.

Current profiles include:

- DGX B200
- DGX B300
- DGX GB200 Compute Tray
- MQM9700-NS2F

Devices for which the catalog intentionally does not assert an external cage type remain visible but are marked as not validation-ready.

## Live reload

The application does not copy the mounted JSON into a database. It checks file metadata (`mtime` + size) and reloads the catalog on the next request when either file changes:

- `/data/nvidia-interconnects.json`
- `/profiles/device-profiles.json`

The browser polls `/api/meta` every 5 seconds and refreshes device data automatically when the dataset revision changes.

## Run

From the repository root:

```bash
docker compose -f compatibility-validator/docker-compose.yml up -d --build
```

Open:

```text
http://localhost:8080/
```

Health check:

```text
http://localhost:8080/healthz
```

The compose file bind-mounts the canonical JSON read-only, so regenerating `data/nvidia-interconnects.json` is visible to the running application without an application restart.

## Runtime hardening and data safety

The service validates both JSON inputs before activating a new catalog revision. A changed dataset is accepted only when its structure passes validation and its file size is within the configured limit.

Default limits:

- canonical catalog: 2 MiB (`MAX_DATA_BYTES`)
- device profiles: 512 KiB (`MAX_PROFILE_BYTES`)
- compatibility-result cache: 256 entries (`COMPAT_CACHE_MAX_ENTRIES`)
- Uvicorn concurrency: 100 requests
- listen backlog: 128
- keep-alive timeout: 5 seconds

If a live-mounted JSON file changes but the new content is invalid, malformed or over the configured size limit, the process continues serving the last-known-good in-memory snapshot. If no valid snapshot has ever been loaded, API access returns `503`.

`/healthz` intentionally exposes only:

```json
{"status":"ok"}
```

`/api/meta` does not expose filesystem paths. Compatibility results are cached by catalog revision, device ID and port-group ID, so a newly accepted catalog revision automatically uses a separate cache namespace.

The container runs as UID/GID `10001`, with a read-only root filesystem, all Linux capabilities dropped and `no-new-privileges` enabled. The Compose definition also applies CPU, memory, PID and file-descriptor limits.


## Dependency integrity

Runtime dependencies are split into:

- `requirements.in` — the two direct application dependencies, pinned to exact versions.
- `requirements.txt` — the complete transitive runtime dependency set, pinned to exact versions and authenticated with SHA-256 hashes.

The image build installs dependencies with `pip --require-hashes --only-binary=:all:` from the explicit PyPI index and runs `pip check`. A package with an unexpected artifact hash, an unpinned transitive dependency, or an inconsistent dependency graph fails the image build.

Regenerate the lock after an intentional dependency update with Python 3.12:

```bash
python -m pip install pip-tools
pip-compile --generate-hashes --output-file=requirements.txt requirements.in
```

The runtime uses base `uvicorn` rather than `uvicorn[standard]` because this application does not require the optional watch/reload, WebSocket acceleration, dotenv, YAML or uvloop dependency set. This keeps the runtime dependency graph smaller.

## Error handling

Startup/catalog-loading failures are logged through the Uvicorn error logger, including the server-side traceback. API clients receive only the constant HTTP 503 response detail `Service unavailable`; internal exception strings, mount points and filesystem paths are not propagated to the response.

## API

The GUI uses the same backend API:

- `GET /healthz`
- `GET /api/meta`
- `GET /api/devices`
- `GET /api/compatible?device_id=...&port_group_id=...`

`GET /api/devices` exposes the effective validation groups together with fields such as:

- `accepted_pluggables`
- `fixed_interfaces`
- `compatibility_source_url`
- `accepted_connector_families`
- `compatibility_source`
- `catalog_accepted_pluggables`
- `scope_note`
- `variants`

`GET /api/compatible` returns only active products accepted for the selected port group and includes:

- `fabric_compatibility`
- `interface_type`
- `interface_count`
- `interface_speed`
- `interface_connector`
- `speed`
- `medium`
- `reach`
- `part_numbers`
- `source_url`
- `compatibility_confidence`
- `compatibility_reasons`

The validator does not calculate quantities or generate a bill of materials.
