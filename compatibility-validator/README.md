# NVIDIA Networking Compatibility Validator

Web application for evaluating NVIDIA LinkX modules and cable assemblies against explicit switch, adapter and DGX port profiles. The interface supports **host-port fit**, **exact hardware and software qualification**, **connections between devices**, a **connection selection assistant**, **complete 1→N breakouts**, and **project validation with a consolidated BOM**.

The repository baseline is preserved in branch [`v0.01`](https://github.com/pi4-dev/nvidia-networking/tree/v0.01), at commit `6071fa9f05b7ea5e116094f518fd4b6c15992867`. Subsequent baselines are [`v0.02`](https://github.com/pi4-dev/nvidia-networking/tree/v0.02) at `d52782bd3ba8d282d1e999ba16b4f2073f501b67` and [`v0.03`](https://github.com/pi4-dev/nvidia-networking/tree/v0.03) at `a2a41c6210a3267068daae0b387a31fa0c49cee2`. Ongoing development (`0.04-dev`) is on `main`.

Version history and subsequent changes are maintained in the repository's
[CHANGELOG.md](../CHANGELOG.md).

## Run

From the repository root:

```bash
docker compose -f compatibility-validator/docker-compose.yml up -d --build
```

Open <http://localhost:8080/>. Health is available at `/healthz`; catalog freshness and revision are in `/api/meta`.

For local development with Python 3.12:

```bash
cd compatibility-validator
python -m venv .venv
. .venv/bin/activate
python -m pip install --require-hashes --only-binary=:all: --index-url https://pypi.org/simple -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8080
```

Default data paths resolve from the application directory. `NVIDIA_DATA_PATH` and `DEVICE_PROFILES_PATH` can override them. Node is only needed to run frontend regression tests; the browser application has no external JavaScript dependencies or build step.

## Workflow

**Port fit:** choose a device, physical port group and optional operating mode/fabric. Search by model or ordering PN; filter by result, lifecycle, cable technology, medium, termination capacity and reach. Select a product to see its checks, source links, matching cable end and exact SKU length where documented. “Why was a product rejected?” includes rejected and retired products.

**Connection A ↔ B:** select both devices and their ports, then either two optical modules plus fiber or the two ends of one cable assembly. Choose ordering PNs, fabric and actual length. The result covers one link or one breakout leg. For fiber, select a catalog ordering PN or a custom OS2/SM-unspecified/OM3/OM4/OM5 assembly, connectors including polish, and explicitly confirm that gender, polarity and lane mapping match the cable drawing.

**Exact hardware:** choose a documented board OPN or stay with the generic device. Expand “Observed hardware and software” to enter SKU, OPN, variant, PSID, firmware, OS and OS version. “Inspect exact hardware” shows parameter values, manufacturer/lab source, verification date and scope, followed by missing facts and actions. Exact profiles can narrow the available physical port group and add only documented modes. Generic catalog facts without dated evidence remain labeled as such. Inspection reports can be exported without selecting a product.

**Connection assistant:** choose devices/ports A and B, fabric, bandwidth **per link**, minimum length, optional technology/fiber grade, and an optional exact PN that must be reused. Enter owned inventory as one `PN,quantity` per line. The assistant compares active cable assemblies with module A + fiber + module B, including ordering numbers, actual SKU length, orientation, port modes, FEC gaps, qualification and quantities to reuse/buy. A required PN counts as one owned item unless its inventory quantity is explicitly entered. Two identical module PNs require two physical modules. “Open connection” transfers the full proposal to manual validation; optical pinout confirmation always starts unchecked.

Ranking first considers validation status and availability of complete ordering numbers, then the selected priority (evidence completeness, fewest components, or reuse), then shortest adequate length and a stable PN ordering. A 3 m requirement can select a documented 5 m SKU; the actual 5 m length is checked against optical reach. A family-level maximum never substitutes for an unknown cable SKU length. The search checks at most 3,000 combinations and explicitly reports truncation; narrow constraints to continue. By default it returns up to 25 proposals (API maximum 100). Missing fiber PNs produce an explicitly incomplete specification. No result is a purchasing approval while required evidence is unknown.

**Breakout 1→N:** select a cable assembly or an optical fanout, one explicit head mode, and an explicit mode on every remote port. Enter unique physical device instance IDs and cage ordinals. Map each branch termination to its logical head links; the validator checks complete coverage, duplicate assignments, aggregate bandwidth, every endpoint and one common FEC configuration. A passing individual branch cannot make an incomplete or contradictory fanout pass. The built-in 2×400G example is a draft with mapping confirmation unchecked.

For an optical fanout, also describe the complete harness PN, connector count, fiber, length, and the optical Tx/Rx lane pairs assigned to every branch. These lane-pair numbers are separate from logical links and individual MPO pin positions. Supply dated, scoped evidence for the harness and, where optical standards differ, per-lane interoperability. Manufacturer and internal lab evidence remain distinct. A harness declaration cannot establish firmware/OS qualification or add capabilities to the catalog. Confirm the actual gender, polarity and mapping only after checking the assembly drawing. Export/import a complete definition in the JSON editor; a changed or absent catalog revision requires fresh confirmation.

**Project / BOM:** add a validated A–B selection with its physical placements, add a complete breakout as one entry, or import a project. A device instance ID identifies one physical switch/card/system, while the cage ordinal is **1-based within the selected physical group**, not a vendor CLI port label. The same cage cannot be occupied by separate entries; branches sharing a head belong in one breakout. Reusing an instance ID with a different model, board profile or conflicting runtime is reported as an error.

Project validation preserves each connection's checks and detects project-wide port conflicts. Enter owned inventory once for the whole project. The BOM counts each cable/harness once and each physical optical module once, then reports required, owned, reused, to-buy and unused quantities by exact PN. Failed or unresolved entries remain visible; the BOM is marked provisional until all required checks and ordering specifications pass. Inventory does not remove a failed compatibility check.

Use JSON to preserve the complete project, including all breakout mappings, evidence and inventory. CSV imports/exports point-to-point connections; download the header template in the project panel. CSV accepts comma, semicolon or tab separators and reports invalid rows without partially replacing a draft. Device identifiers may be exact catalog IDs or unique model names; a unique catalog PN can resolve a product. A project containing breakouts must use JSON for topology export. The separate BOM CSV includes quantities, references and the provisional status.

Ready-to-edit examples: [complete 2×400G cable breakout](examples/breakout-2x400.json), [project with inventory](examples/project.json), and [point-to-point CSV](examples/connections.csv). They use the shipped catalog and intentionally remain `unknown` where evidence or physical confirmation is missing.

“Copy configuration link” preserves single-connection selections, filters and catalog revision. Breakouts and projects use complete JSON files for sharing. Local storage restores the last configuration and project drafts. A shared/imported configuration for an older revision shows a notice and recalculates using the available catalog; it does not retrieve historical catalog bytes. “Export JSON” includes the result, checks, selections, revision, catalog freshness, application version and timestamp. Editing a draft invalidates its report; unapplied JSON edits must be applied before validation or export.

## Results and scope

| Result | Meaning |
| --- | --- |
| `compatible` | All applicable checks have documented passing values. |
| `conditional` | Required checks pass; additional conditions or host-fit details still need verification. |
| `unknown` | Required evidence is missing. This is not an approval. |
| `incompatible` | At least one check explicitly fails. |

Mechanical `match_type` (`exact`, `backward-compatible`, `mismatch`, `unknown`) is separate from the overall result. An exact cage match alone cannot certify interoperability. Missing fabric, rate, mode, capacity or endpoint data cannot produce a positive result.

The host-port view checks pluggability, connector family, OSFP cooling shell, supported fabric, explicit link count/rate and per-cage capacity. Electrical lanes, lane rate and FEC are shown as conditions if unknown. Complete connection validation requires those facts, and also checks:

- Both cable ends, including reversed flat-top/finned assemblies and breakout branches.
- A common cable link rate and FEC across both hosts and cable ends.
- Matching cable identity/variant/PN and the selected SKU's actual length.
- Optical medium, fiber-specific reach, connector/polish, standard, lanes, lane rate, wavelengths and FEC.
- User verification of optical gender, polarity and lane mapping; a known fiber PN alone does not assert that both module receptacles match it.
- Exact-board identity and product-specific firmware/OS qualification where evidence exists.

Undocumented hardware values remain unknown. The shipped catalog does not provide every adapter cage rate, electrical mode, FEC setting or firmware qualification, so complete links and breakouts can correctly return `unknown`. The A–B view covers one link or one breakout leg; the dedicated breakout view validates every declared branch together. In projects, a single-leg or incomplete multi-connector selection remains an unresolved scope check. Optical fanouts model passive lane mapping, not arbitrary signal-splitting networks. Project validation checks declared connections and physical port ownership; it does not certify routing, redundancy, congestion or fabric-wide performance.

Complete links return `technical_status` separately from each host's `qualification`. An applicable manufacturer record can confirm qualification. A matching internal lab pass produces `lab-tested` and a conditional overall result when all required technical checks pass; it never becomes manufacturer confirmation. Missing or untested versions, absent PSIDs and out-of-scope records remain `unknown`. An explicit scoped denial or identity mismatch fails; a support record cannot override mechanical or electrical failure. Version ranges use numeric components (`2.10 > 2.9`); suffixes require exact version entries.

The initial exact profile catalog covers four ConnectX-8 OPNs (C8180 Socket Direct, C8180 DSP, C8180L and C8240) and 21 MFP7E10/MFP7E30 fiber assemblies, verified against linked NVIDIA sources on 2026-09-21. It deliberately contains **no invented PSIDs, firmware minimums, OS version qualifications or FEC values**. MFP7E30 is documented as 9/125 single-mode; its grade is `SM-unspecified` until an explicit OS2 source is recorded. Existing generic profiles remain available for other hardware.

## Data contracts

The canonical `../data/nvidia-interconnects.json` remains schema **8**. `data/device-profiles.json` uses schema **2**, with explicit port modes, cable endpoints, SKU lengths and optical details. Both inputs are checked before activating a revision. See [DATA_MODEL.md](DATA_MODEL.md) for field semantics and update instructions.

`port_interface_compatibility` remains authoritative for accepted module families and fixed interfaces. The overlay cannot broaden those permissions. Port capabilities are not inferred from free-text descriptions or aggregate adapter bandwidth. Generic and SKU-specific Quantum-2 profiles use the same twin-port capacity; SN3420 modes cannot exceed cage capacity. Unqualified OSFP shells remain unknown.

`app/models.py` and `topology_models.py` own the strict Pydantic contracts; `catalog.py` handles loading and cross-file integrity, `rules.py` single-link compatibility, `hardware.py` scoped evidence/qualification, `recommendations.py` connection selection, `topology.py` complete breakouts, `projects.py` project/BOM/CSV operations, and `api.py` HTTP routes. `main.py` remains the Uvicorn entry point. Browser helpers and UI logic live in `static/core.js`, `static/app.js` and `static/topology.js`.

## Live reload and failure handling

On each data request the loader checks inode, nanosecond timestamps and size for both files. It validates a candidate snapshot and confirms that neither input changed during loading before activating it. The revision hashes both inputs. The browser polls metadata every five seconds, preserves selections and filters on refresh, cancels obsolete requests, and checks revision and selection before displaying a response.

Compose mounts **directories** read-only so that atomic file replacement is visible inside the container. Update both related inputs together; if one temporarily disagrees with the other, the candidate is rejected until a consistent pair is present.

A malformed, oversized or inconsistent update keeps the last valid snapshot and sets `/api/meta` → `catalog.state` to `degraded`, with last-success/last-failure timestamps and a generic error code. The GUI displays this state. If no valid snapshot has ever loaded, data endpoints and `/healthz` consistently return `503`; they never return an empty successful catalog. Correcting the input recovers without restarting. API/network failures show an offline notice and a retry action.

Detailed errors remain in server logs. Public errors and metadata do not expose filesystem paths. `/healthz` returns only `{"status":"ok"}` when a valid snapshot is available, including during last-good operation; monitoring for rejected updates should inspect `/api/meta` as well.

## API

| Route | Response |
| --- | --- |
| `GET /healthz` | Minimal readiness check. |
| `GET /api/meta` | Counts, versions, revision, snapshot dates and reload state. |
| `GET /api/catalog` | Metadata, devices, products, exact hardware profiles and fiber SKUs from one coherent snapshot. |
| `GET /api/devices` | Device list; revision in `X-Catalog-Revision`. |
| `GET /api/products` | All detailed and retired diagnostic records plus revision. |
| `GET /api/evaluate` | Every product with structured checks for the selected host port. |
| `POST /api/evaluate` | Host fit with an exact hardware profile and observed runtime; includes hardware evidence. |
| `POST /api/hardware/inspect` | Effective port facts, dated sources, identity checks and actionable gaps. |
| `POST /api/recommendations` | Ranked single-link proposals, components, inventory, settings, full validation and bounded-search metadata. |
| `POST /api/connection` | One A-to-B link with technical/qualification results, checks, gaps, orientation and selected configuration. |
| `POST /api/breakout` | Complete cable/optical fanout, branch checks, head coverage, common FEC and physical allocations. |
| `POST /api/project` | All connections and breakouts, physical conflicts, summary and consolidated inventory/BOM. |
| `POST /api/project/import-csv` | Parse `{name, csv, revision}` into a project draft; reject invalid rows atomically. |
| `GET /api/project/template.csv` | Header template for point-to-point imports. |
| `POST /api/project/connections.csv` | Export a project request's point-to-point connections; breakouts require JSON. |
| `POST /api/project/bom.csv` | Revalidate a project request and download its BOM, including provisional status. |
| `GET /api/compatible` | Legacy route: active `compatible`/`conditional` host-port candidates only. |

`/api/evaluate` requires `device_id` and `port_group_id`; optional parameters are `fabric`, `mode_id` and `revision`. Identifiers and values are bounded. A stale revision returns `409`, invalid input `422`, and an absent device/group `404`.

Example body for `/api/connection` (use IDs and revision from `/api/catalog`):

```json
{
  "a": {
    "device_id": "profile:MQM9700-NS2F",
    "port_group_id": "ndr",
    "product_id": "Copper|MCA4J80-Nxxx-FTF|flat-to-finned",
    "endpoint_id": "B",
    "part_number": "980-9I601-00N003"
  },
  "b": {
    "device_id": "system:DGX B200",
    "port_group_id": "cluster",
    "product_id": "Copper|MCA4J80-Nxxx-FTF|flat-to-finned",
    "endpoint_id": "A",
    "part_number": "980-9I601-00N003"
  },
  "fabric": "IB",
  "length_m": 3
}
```

Each host can additionally contain `hardware_profile_id` and a `runtime` object with `sku`, `opn`, `adapter_variant`, `psid`, `firmware`, `os_name`, and `os_version`. The inspection endpoint takes a host plus optional `revision`; POST evaluation also accepts `fabric`. A profile for a different device or physical group returns `404`. Qualification records and profiles are maintained in the versioned JSON file; there is no unauthenticated catalog-editing API.

Example `/api/recommendations` body:

```json
{
  "a": {"device_id": "profile:MQM9700-NS2F", "port_group_id": "ndr"},
  "b": {"device_id": "system:DGX B200", "port_group_id": "cluster"},
  "fabric": "IB",
  "speed_gbps": 400,
  "minimum_length_m": 3,
  "technology": "any",
  "owned_parts": [{"part_number": "980-9I601-00N003", "quantity": 1}],
  "sort_by": "reuse",
  "include_unknown": true
}
```

Additional assistant fields are `fiber_type` (default `any`), `reuse_part_number`, `reuse_side` (`either`/`a`/`b`), `limit` (1–100), and `revision`. `technology` supports `any`, `cable`, `optical`, `DAC`, `LACC`, `ACC`, `AOC`. `sort_by` supports `evidence`, `fewest_components`, `reuse`. Connection requests accept `fiber_part_number`; supplied properties and actual length must agree with that SKU.

For single connections, `endpoint_id` and `mode_id` may be omitted to evaluate documented alternatives. Complete breakouts require an explicit `mode_id` at the head and every remote endpoint. Requesting a nonexistent endpoint/mode produces a failed validation. `revision` is optional for direct API clients and required by the GUI's workflow. A stale project or nested entry revision returns `409`. See [DATA_MODEL.md](DATA_MODEL.md) and [examples/](examples/) for complete topology request contracts. Interactive API documentation is at `/docs` (its default Swagger assets require network access).

## Limits and container configuration

| Setting | Default |
| --- | --- |
| `MAX_DATA_BYTES` | 2 MiB |
| `MAX_PROFILE_BYTES` | 512 KiB |
| `COMPAT_CACHE_MAX_ENTRIES` | 256 |
| HTTP request body, existing routes | 16 KiB |
| HTTP request body, `/api/breakout` | 256 KiB |
| HTTP request body, project POST routes | 1 MiB |
| Breakout branches / project connections / project breakouts | 16 / 200 / 64 |
| Project physical endpoint assignments / inventory PN entries | 512 / 512 |
| Uvicorn concurrency / backlog / keep-alive | 100 / 128 / 5 seconds |
| Compose CPU / memory / PIDs | 1 CPU / 256 MiB / 128 |

Input reads are bounded before JSON parsing, duplicate keys and nonfinite numbers are rejected, and generic GET evaluations are cached by revision, device, group, fabric and mode. Runtime-specific POST evaluations are independent, so one host's firmware context cannot leak into another result. The container runs as UID/GID `10001`, with a read-only root filesystem, all capabilities dropped and `no-new-privileges`. The GUI uses a same-origin Content Security Policy and escapes catalog text.

Runtime dependencies are pinned with hashes in `requirements.txt`; direct dependencies are in `requirements.in`. The Docker build uses `--require-hashes --only-binary=:all:` and `pip check`. Regenerate the lock with Python 3.12 after intentional dependency changes:

```bash
python -m pip install pip-tools
pip-compile --generate-hashes --output-file=requirements.txt requirements.in
```

## Tests and CI

From `compatibility-validator/`, after installing the runtime dependencies:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
npm ci --ignore-scripts
npm test
```

Backend tests exercise the actual repository inputs, failed startup/reload/recovery, strict schemas, hardware regressions, both-end validation and a real HTTP server. Breakout/project regressions cover complete coverage, global FEC conflicts, optical mapping, physical port conflicts, inventory allocation, CSV round trips and stale revisions. Fully passing optical examples are explicitly synthetic test fixtures, not catalog claims. Frontend tests use jsdom to run the shipped scripts, including out-of-order responses, catalog refresh, draft preservation, JSON/CSV import, export/share and startup retry.

`.github/workflows/compatibility-validator.yml` runs both suites and builds/starts the production Compose service with its resource limits. `tests/smoke.py` then checks nonempty catalog data, rejected products, both-end validation, recommendations, a complete breakout and a project BOM through HTTP:

```bash
python tests/smoke.py http://127.0.0.1:8080
```
