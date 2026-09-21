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

A mode uses `id`, `links`, `speed_gbps`, and optional `electrical_lanes`, `lane_rate_gbps`, `fec`. `2 × 400G` and `1 × 800G` are distinct. Electrical lanes are per cage; lane rate is nominal data rate, not encoded signaling rate. When present, lanes × nominal lane rate must equal links × link rate. No mode may exceed cage capacity.

Mode IDs are stable within the port or endpoint. Use the canonical `1x400`, `2x400`, etc. convention for matching profiles. FEC names must represent the same documented configuration to intersect; do not equate unrelated schemes by a vague label such as “FEC enabled”.

## Cable and optical details

`interconnect_details` is keyed by `category|model|variant` with `-` for an absent variant. Each record includes:

- `endpoints`: one `module` termination for a transceiver, or two termination types A/B for a cable assembly. Each has family, exact mechanical type, explicit modes and role (`module`, `peer`, `head`, `branch`). `count` represents identical ends of that type; a breakout branch has at least two.
- `skus`: exact canonical PNs with `length_m` when verified and a source. A transceiver has no cable SKU length; its fiber is selected separately. A family maximum reach is not an individual PN's cable length.
- `cable_type`: `Transceiver`, `AOC`, `DAC`, `ACC`, `LACC`, `Copper` or `Unknown`. Use generic `Copper` when the technology is not documented.
- `optics`: standard, connector including polish, lane count per optical connector, nominal optical lane rate, wavelengths and FEC. Missing values stay unknown.
- `source_url` and `conditions`: primary documentation and scope/conflicts that still need verification.

Both ends must have the same aggregate bandwidth after multiplying by endpoint count. An endpoint's mode cannot exceed the canonical assembly rate. Canonical connector declarations, termination counts and PN sets must match the overlay. A branch's compatibility uses its own modes, not the whole assembly's speed.

Connection validation requires one common electrical operating configuration, evaluates both orientations and reports the selected ends. It covers one breakout leg or one optical link. An optical module's host electrical lane count may differ from its optical lane count due to an internal gearbox; these are separate fields and checks.

## Updating data

1. Verify primary NVIDIA specifications and ordering information for the exact SKU and mechanical variant. Preserve contradictory source facts in `conditions` instead of selecting an unsupported value.
2. Update canonical rows and explicit profiles together. Keep IDs stable unless product identity changes.
3. Leave fields unknown when the source does not identify per-cage mode, FEC, optics or exact length. Add a new profile only with an explicit source and scope.
4. Run the backend suite against the actual input files, then browser tests. Hardware regressions should cover both supported and rejected cases; fully passing synthetic fixtures must be clearly labeled as fixtures.
5. Replace input files atomically. Directory mounts permit rename-based updates. The live loader keeps the last valid pair if it encounters an intermediate inconsistent state.
6. Check `/api/meta` for `ready` and the new revision. Revalidate saved configurations; report exports retain their original revision and freshness state.

The validator does not convert missing firmware qualifications into a guarantee. Add documented platform/firmware prerequisites as conditions until there is enough structured information to check them directly.
