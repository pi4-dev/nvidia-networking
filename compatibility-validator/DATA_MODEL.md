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

The assistant uses exact SKU lengths at least as long as the requested minimum, then validates actual length against both endpoints. Unresolved fiber PNs remain explicit incomplete specifications. Components and inventory counts describe one link, not a full breakout tree or a project-wide BOM.

## Updating data

1. Verify primary NVIDIA specifications and ordering information for the exact SKU and mechanical variant. Preserve contradictory source facts in `conditions` instead of selecting an unsupported value.
2. Update canonical rows and explicit profiles together. Keep IDs stable unless product identity changes.
3. Leave fields unknown when the source does not identify per-cage mode, FEC, optics or exact length. Add a new profile only with an explicit source and scope.
4. Run the backend suite against the actual input files, then browser tests. Hardware regressions should cover both supported and rejected cases; fully passing synthetic fixtures must be clearly labeled as fixtures.
5. Replace input files atomically. Directory mounts permit rename-based updates. The live loader keeps the last valid pair if it encounters an intermediate inconsistent state.
6. Check `/api/meta` for `ready` and the new revision. Revalidate saved configurations; report exports retain their original revision and freshness state.

The validator does not convert missing firmware qualifications into a guarantee. Use structured qualification only when the source identifies its scope; retain additional prerequisites as unresolved conditions.
