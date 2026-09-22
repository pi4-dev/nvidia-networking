# Validator data model

The validator activates only a mutually consistent pair of canonical schema **8** and profile schema **2** inputs. Unrecognized schema versions require an explicit code migration. Unknown facts use `null` or empty lists; do not fill them with a family's aggregate bandwidth or a guess based on a product name.

## Canonical catalog

`../data/nvidia-interconnects.json` owns model identity, product lifecycle, module families, advertised aggregate speed/reach, fabric, ordering part numbers and primary sources. Nullable `pluggable` is intentional: `null` means no assertion, `false` means fixed interfaces.

The strict row models validate every required column and its type, including fields that used to pass through unchecked. URLs must be HTTP(S) without credentials. Per-table model identifiers, per-product ordering PNs, columns and profile IDs must be unique.

## Explicit port profiles

Each `profiles` record in `data/device-profiles.json` has an ID, model/kind, source and `port_groups`. IDs beginning `ethernet:`, `infiniband:`, `dpu:` or `supernic:` refer to an existing canonical device. System profiles use `system:` IDs and SKU profiles use `profile:` IDs.

| Port-group field | Meaning |
| --- | --- |
| `count` | Physical cage count; `null` if unspecified. Not a planning quantity. |
| `connector_family` | Cage family, such as OSFP or QSFP112. |
| `accepted_connector_families` | Explicit permitted modules, constrained by the canonical compatibility map. |
| `accepted_interface_types` | OSFP-finned / OSFP-flattop; empty means mechanics unknown. |
| `module_speed_gbps` | Total capacity of **one cage**, not all ports on a card. |
| `modes` | Documented combinations of independent links and rate per link. |
| `fabrics` | Documented ETH / IB / NVL support for this group. |
| `pluggable` | `true`, `false` or unknown `null`. |
| `source_url`, `scope_note`, `conditions` | Evidence, hardware scope and unresolved prerequisites. |

A mode uses `id`, `links`, `speed_gbps`, and optional `electrical_lanes`, `lane_rate_gbps`, `fec`, and `fabrics`. Empty mode fabrics inherit group/product scope; populated fabrics constrain that specific mode. `2 × 400G` and `1 × 800G` are distinct. Electrical lanes are per cage; lane rate is nominal data rate, not encoded signaling rate. When present, lanes × nominal lane rate must equal links × link rate. No mode may exceed cage capacity.

Mode IDs are stable within the port or endpoint. Use descriptive IDs such as `2x400-ndr` when protocol variants differ. Matching uses link count and per-link rate, then electrical/FEC/fabric checks, not equality of mode IDs across products. FEC names must represent the same documented configuration to intersect; do not equate unrelated schemes by a vague label such as “FEC enabled”.

## Cable and optical details

`interconnect_details` is keyed by `category|model|variant` with `-` for an absent variant. Each record includes:

- `endpoints`: one `module` termination for a transceiver, or two termination types A/B for a cable assembly. Each has family, exact mechanical type, explicit modes and role (`module`, `peer`, `head`, `branch`). `count` represents identical ends of that type; a breakout branch has at least two.
- `skus`: exact canonical PNs with `length_m` when verified and a source. A transceiver has no cable SKU length; its fiber is selected separately. A family maximum reach is not an individual PN's cable length.
- `cable_type`: `Transceiver`, `AOC`, `DAC`, `ACC`, `LACC`, `Copper` or `Unknown`. Use generic `Copper` when the technology is not documented.
- `optics`: standard, connector including polish, lane count per optical connector, nominal optical lane rate, wavelengths and FEC. Missing values stay unknown.
- `source_url` and `conditions`: primary documentation and scope/conflicts that still need verification.

Both ends must have the same aggregate bandwidth after multiplying by endpoint count. An endpoint's mode cannot exceed the canonical assembly rate. Canonical connector declarations, termination counts and PN sets must match the overlay. A branch's compatibility uses its own modes, not the whole assembly's speed.

Connection validation requires one common electrical operating configuration, evaluates both orientations and reports the selected ends. It covers one breakout leg or one optical link. An optical module's host electrical lane count may differ from its optical lane count due to an internal gearbox; these are separate fields and checks.

## Exact hardware and provenance

Schema 2 additionally accepts `hardware_profiles` and `fiber_assemblies` (both default to empty for existing catalogs). These arrays participate in the same revision hash and atomic last-good validation as the original profiles.

A hardware record has `id`, `device_id`, `label`, `identity`, `ports`, `required_context`, `qualifications` and `notes`. `identity` maps any of `sku`, `opn`, `adapter_variant`, `psid` to `{ "value": "...", "evidence": {...} }`. Only assert identities documented for this exact board. Runtime input is an observed value, not a new catalog fact.

Every `Evidence` contains:

| Field | Required meaning |
| --- | --- |
| `kind` | `manufacturer` or `lab`; never label an internal test as manufacturer support. |
| `source_url` | HTTP(S) primary document or accessible internal test report, without embedded credentials. |
| `verified_on` | Valid, nonfuture ISO date on which the claim was checked. |
| `scope` | Exact board, mode, product and relevant environmental applicability. |
| `note` | Optional limitation or source conflict. |

Each `ports` entry selects `port_group_id` and may override `module_speed_gbps`, `count`, `fabrics`, `modes`. These overrides require evidence keys for each populated field and each `modes.<id>` entry. Evidence for a mode covers only its populated parameters; an empty FEC remains unknown. The evidence map may also annotate the inherited `connector_family`, `accepted_connector_families`, `accepted_interface_types` and `pluggable` facts without changing them. Other keys, missing evidence, evidence on unknown inherited facts, impossible capacity and out-of-scope fabrics are rejected. An exact hardware overlay cannot alter the canonical connector/fixed-interface permissions.

Selecting an exact profile restricts use to its listed physical groups. Profile IDs must be unique; device, group, mode, product and PN references must exist in the activated snapshot. Generic devices never receive another board's overrides.

`required_context` lists relevant observed fields (`psid`, `firmware`, `os_name`, `os_version`). A qualification must also cover each required field in structured conditions or the exact profile identity; entering an arbitrary version cannot make an unscoped support claim apply.

## Product qualification records

A `qualifications` entry contains `id`, `port_group_id`, `product_ids` and/or `part_numbers`, `mode_ids`, `fabric`, optional `psid`, `firmware`, `os_name`, `os_version`, `outcome` (`supported`/`unsupported`) and `evidence`.

- At least one product/PN scope is mandatory. When both are specified, both must match, and the PNs must belong to the named products.
- Empty mode IDs mean the source explicitly applies to the selected port's modes. Otherwise only the named mode matches. Fabric always matches exactly.
- Firmware and OS version use either `{"versions": ["2.10", "2.11-rc1"]}` or numeric `minimum`/`maximum` bounds. Do not infer a range from one tested version. OS version also requires `os_name`.
- Bounds compare numeric components with trailing zero padding; nonnumeric suffixes only match exact version lists. Outside a tested list/range means unknown, not unsupported. Record an explicit denial when a source actually excludes the configuration.
- A matching manufacturer pass establishes manufacturer qualification. A lab pass records lab evidence and remains conditional without manufacturer confirmation. A denial or identity mismatch wins, including conflicting support records; the UI exposes the conflict. Qualification never bypasses technical checks.
- The initial data has no qualification entries because the linked board specification pages do not establish product-specific PSID/firmware/OS support. Add actual vendor entries or labeled lab reports through the JSON/Git workflow.

## Fiber ordering assemblies

Each `fiber_assemblies` entry defines unique `part_number`, `model`, `length_m`, `medium`, `fiber_type`, `connector_a`, `connector_b`, `polarity`, `gender_a`, `gender_b`, and an `evidence` mapping with exactly one entry per fact. The PN must not duplicate a transceiver/cable PN.

`fiber_type` is OS2, SM-unspecified, OM3, OM4 or OM5. `SM-unspecified` preserves a documented single-mode cable without inventing an OS2 designation. Shipped MFP7E10 lengths through 30 m use documented OM3, longer lengths OM4; MFP7E30 remains SM-unspecified. Both families have documented female MPO-12/APC ends and Type B polarity. These cable facts do not establish the mating module gender or full lane mapping, so the user's pinout confirmation is still required.

The assistant uses exact SKU lengths at least as long as the requested minimum, then validates actual length against both endpoints. Unresolved fiber PNs remain explicit incomplete specifications. Assistant quantities describe one link; project validation separately consolidates every declared connection and complete breakout.

## Complete breakout requests

`app/topology_models.py` defines strict, bounded request contracts without changing the canonical/profile schemas. `POST /api/breakout` accepts the following fields. See [the cable example](examples/breakout-2x400.json) for a complete request using real catalog selections.

| Field | Meaning |
| --- | --- |
| `topology` | `cable` (default) or `optical`. |
| `head` | Installed host/product selection with one required explicit `mode_id`. |
| `branches` | 1–16 branch declarations; incomplete fanouts may be submitted to obtain coverage gaps. |
| `fabric`, `length_m` | Protocol and actual complete assembly/path length. Unknown length remains unresolved. |
| `mapping_verified` | User confirmation of the physical branch-to-head mapping; defaults to `false`. |
| `optical_fanout` | Complete passive harness declaration for optical topology; forbidden for a cable assembly. |
| `revision` | Optional catalog revision; a supplied stale revision returns `409`. |

Every installed selection extends the existing `Selection` with `instance_id` and `port_number`. The instance identifies one physical device. `port_number` is a **1-based cage ordinal within `port_group_id`**, bounded to 1–1024 and checked against the effective hardware profile's documented count. It does not represent a vendor CLI label. Instance IDs and entry IDs use 1–64 letters, digits, dot, underscore, colon or hyphen, beginning with a letter or digit. Exact profiles and observed runtime use the same contracts as single-link validation.

Each branch contains a unique `id`, installed `selection`, physical `termination` number (1–16), and `head_links` logical link numbers. Cable topology requires the same assembly/product/PN at the head and every termination. The complete request checks documented branch count, exact coverage, no duplicate physical cages or link assignments, capacity, common operating rate and a FEC intersection across the entire assembly. Missing or unused terminations remain `unknown`; duplicate or impossible assignments fail. The head mode is fixed for all branches, so independently valid branches cannot silently select contradictory head configurations.

Optical branches additionally contain `head_optical_port`, `head_optical_lanes`, `branch_optical_lanes`, and optional `interop_evidence`. Optical lane indices identify Tx/Rx **pairs**; the two lists describe corresponding pairs in order. They are distinct from logical link indices and raw MPO pin positions. All documented head connectors/lanes and each remote module's lanes must be covered exactly once. Multi-connector remote modules without complete coverage remain unresolved. The validator checks lane count/rate, wavelength, fiber medium, connector/polish, full path reach, aggregate bandwidth and common FEC. Different or undocumented optical standards require a dated, scoped `Evidence` record for per-lane interoperability; a matching wavelength alone is insufficient.

`optical_fanout` contains `part_number` (optional until known), `branch_count` (2–16), `head_ports` (1–16), `fiber: FiberCable`, and optional `evidence: Evidence`. Evidence must cover the complete harness's PN, length, connectors and lane map. Existing catalog transceiver, cable or point-to-point fiber PNs cannot be repurposed as a separate fanout harness. Project entries using the same external harness PN must agree on length, connectors and physical mapping. `fiber.pinout_verified` confirms gender/polarity/Tx-Rx wiring separately from the logical mapping confirmation.

Harness and interoperability evidence is supplied with the project and is not written into the catalog. Manufacturer evidence can pass its scoped technical check; lab evidence remains conditional. Neither evidence type qualifies unrelated board/firmware/OS combinations. Exported breakout reports retain every branch's result, checks, qualification and mapping, plus whole-assembly checks and `common_fec`.

## Connection projects and BOM

`POST /api/project` accepts `format: "nvidia-connection-project-v1"`, `name`, `connections`, `breakouts`, `owned_parts`, optional `cabling`, and optional `revision`. A connection extends `ConnectionRequest` with a unique `id` and installed A/B selections. A breakout extends `BreakoutRequest` with a unique `id`. IDs are unique across both collections. Projects require at least one entry and permit at most 200 connections, 64 breakouts, 512 physical endpoint assignments, and 512 unique owned PNs. The body limit is 1 MiB; standalone breakout requests allow 256 KiB.

Validation checks the complete project against one catalog snapshot. A stale nested entry also returns `409`. Unresolved catalog selections remain an `unknown` result for their entry while other entries are still evaluated. Repeated cages, conflicting device identities or incompatible runtime assertions for the same instance fail globally. Single-link scope warnings become required unknowns in a project; represent shared heads as complete breakout entries.

The response contains `results`, `summary`, `checks`, `gaps`, `port_allocations`, the input `project`, and `bom`. The BOM counts physical cable/harness assemblies once per declared connection/breakout and optical modules once per occupied cage/product/PN. Conflicting selections remain visible instead of being silently discarded. Rows group by exact PN and expose `required`, `owned`, `reused`, `to_buy`, `verified_ordering`, source URLs and entry references. Inventory is allocated once globally; unused quantities appear in `unused_inventory`. `provisional` remains true whenever ordering evidence is incomplete or the project result is not `compatible`.

JSON is the complete interchange format, including breakouts, physical mapping, runtime, evidence, inventory and cabling metadata. The browser restores drafts locally, discards saved results on import, and clears physical mapping confirmations for changed or absent revisions. It rejects obsolete responses after a draft edit. Unapplied JSON edits remain in the editor during catalog refresh and must be applied before validation/export.

## Cabling plans and installation declarations

`cabling` is optional, so existing v1 projects remain valid. It defaults to empty `locations`, `port_labels` and `cables` arrays. See [cabling-project.json](examples/cabling-project.json) for a complete example without pre-asserted installation states.

| Collection | Fields and limits |
| --- | --- |
| `locations` | Up to 512 records: unique project `instance_id`, nullable `rack` (1–64 printable characters) and nullable `rack_u` (integer 1–1000). |
| `port_labels` | Up to 512 records: unique occupied `(instance_id, port_group_id, port_number)` and `label` (1–64 printable characters). The label does not replace the physical cage ordinal used for validation. |
| `cables` | Up to 264 records: unique project `entry_id`, nullable `cable_id` using the asset-ID syntax, and up to 16 `progress` records. |
| `progress` | Unique `branch_id` (null for a point-to-point connection), `installed`, `checked`, nullable `definition`, and printable `notes` up to 512 characters. |

References outside the project are rejected. Effective cable IDs are the custom value or `C-<entry-id>` and must be unique case-insensitively, including generated/custom collisions. Each cable gets `/A` and `/B` labels; a cable breakout gets one `/H` and a `/BR-<branch-id>` for each branch. An optical fanout has `/H<number>` for each physical head connector. Each branch contributes one plan row. Declared but unassigned optical connectors stay visible in a provisional plan. Module ordering PNs are endpoint data; cable/fiber/harness ordering PNs identify the labeled assembly.

`POST /api/project/cabling` validates against one snapshot and returns `rows`, `labels`, `issues`, `summary`, `status`, `provisional`, `revision`, `application_version` and `evaluated_at`. Rows include source/destination rack, device, physical cage, native marking and module PN; branch termination, logical links and optical lane mappings; cable PN and length; and effective installation states. The actual length is the requested value or the documented exact SKU length when omitted. Missing rack, native marking, ordering PN or length creates an issue. The plan is provisional whenever an issue remains or whole-project compatibility is not `compatible`.

To record a declaration, first generate the plan and copy the row's 64-character SHA-256 `definition` into the matching `progress` record. `checked` requires `installed`, and either true state requires a fingerprint. It binds the declaration to the entry configuration, normalized branch order, cable ID, endpoint locations/markings, PN and effective length. Physical/configuration changes invalidate the declaration: the report returns `progress_stale: true` and effective false states while the original JSON declaration remains available. Unrelated catalog revision changes alone, reordered branches and edited notes do not invalidate it. A changed derived SKU length does. These are user declarations, not authentication, audit signatures, measured link tests or qualification evidence.

`POST /api/project/cabling.pdf`, `/api/project/labels.pdf` and `/api/project/cabling.xlsx` accept the same project and revalidate it at export time. They return attachments with the document MIME type, `X-Catalog-Revision` and `Cache-Control: no-store`. All four routes enforce the same 1 MiB body limit and stale top-level/nested revision checks. PDF/XLSX generation is limited to two simultaneous exports per worker; a busy exporter returns `503` with `Retry-After: 2`.

Plan PDFs use A4 landscape with repeated table headers. Label PDFs use A4 portrait and variable-size cut-out cards, including an embedded DejaVu Sans font. XLSX contains `Cabling plan` and `End labels` sheets with numeric lengths, boolean installation states, filters, frozen headers and wrapped text. User strings remain literal cells even if they start with `=`. These files are report snapshots; only JSON preserves editable installation metadata and fingerprints. No server-side project persistence or XLSX reimport is provided.

## Project CSV

`GET /api/project/template.csv` provides the column header; [connections.csv](examples/connections.csv) supplies a real point-to-point example. `POST /api/project/import-csv` takes `{name, csv, revision}` and returns a project draft. It accepts comma, semicolon or tab separators, optionally a UTF-8 BOM, at most 200 rows, and at most 750,000 characters inside the JSON body limit. Invalid headers, duplicate columns, wrong row widths, invalid values and ambiguous device/PN lookups reject the entire import with row details.

| Columns | Meaning |
| --- | --- |
| `id`, `fabric` | Unique connection ID and protocol; required. |
| `a_instance`, `b_instance` | Physical device identities; required. |
| `a_device`, `b_device` | Exact catalog ID or unique exact model; required. |
| `a_port`, `b_port` | Positive physical cage ordinals; required. |
| `a_group`, `b_group` | Physical group ID; optional only when the device has one group. |
| `a_product`, `b_product`, `a_pn`, `b_pn` | Product and ordering PN; a unique known PN may resolve an omitted product ID. |
| `a_mode`, `b_mode`, `a_end`, `b_end`, `a_profile`, `b_profile` | Optional operating mode, cable end and exact hardware profile. |
| `a_` / `b_` + `sku`, `opn`, `adapter_variant`, `psid`, `firmware`, `os_name`, `os_version` | Optional observed runtime values. |
| `length_m`, `fiber_pn`, `fiber_type`, `connector_a`, `connector_b`, `pinout_verified` | Actual path/cable length and optical assembly data; confirmation accepts `true`/`false` or `1`/`0`. |

`POST /api/project/connections.csv` exports point-to-point selections from a project request. Projects containing breakouts or nonempty cabling metadata must use JSON to preserve that context; CSV export rejects them. `POST /api/project/bom.csv` revalidates the complete project and exports quantities, entry references, project result and provisional status. CSV fields that could execute spreadsheet formulas are escaped. Keep JSON as the authoritative format when exact free-text round trips or full project context are needed.

## Updating data

1. Verify primary NVIDIA specifications and ordering information for the exact SKU and mechanical variant. Preserve contradictory source facts in `conditions` instead of selecting an unsupported value.
2. Update canonical rows and explicit profiles together. Keep IDs stable unless product identity changes.
3. Leave fields unknown when the source does not identify per-cage mode, FEC, optics or exact length. Add a new profile only with an explicit source and scope.
4. Run the backend suite against the actual input files, then browser tests. Hardware regressions should cover both supported and rejected cases; fully passing synthetic fixtures must be clearly labeled as fixtures.
5. Replace input files atomically. Directory mounts permit rename-based updates. The live loader keeps the last valid pair if it encounters an intermediate inconsistent state.
6. Check `/api/meta` for `ready` and the new revision. Revalidate saved configurations; report exports retain their original revision and freshness state.

The validator does not convert missing firmware qualifications into a guarantee. Use structured qualification only when the source identifies its scope; retain additional prerequisites as unresolved conditions.
