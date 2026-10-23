# NVIDIA Networking Inventory Change Report — 2026-10-23

Compared with repository snapshot: **2026-10-20** (schema v10, unchanged).

Note: the stored state file was not advanced after the 2026-10-21 report, so that report's changes (items 1–4 under *Changed* and *Added*) are still differences against the stored state. They are repeated here for completeness and are marked "(carried over from 2026-10-21)". New in this run: MetroX-3 XC and the Skyway-3 URL.

## Added

### ConnectX-8 SuperNIC (carried over from 2026-10-21)
- **C8180L Partner Cooled** — OPN `900-9X81E-00EX-SL0`; OSFP x1, XDR 800Gb/s IB / 2x400GbE; Mass Production.
  Source: https://networking-docs.nvidia.com/connectx8hw

### ConnectX-9 SuperNIC (carried over from 2026-10-21)
- **C9220** — OPN `900-9X91Q-00RV-ST0`; QSFP112 x2, 400GbE; Prototype.
- **C9210** — OPN `900-9X91Q-00RC-ST0`; QSFP112 x2, 200GbE; Prototype.
  Source: https://networking-docs.nvidia.com/connectx9hw

## Removed

None.

## Changed

### MetroX-3 XC (new in this run)
- **MetroX-3 XC TQ8400**: `part_numbers` `[]` -> `['920-9B020-00FA-0DZ', '920-9B020-00FA-6DZ']`
- `legacy_opn` `null` -> `MTQ8400-HS2R / MTQ8400-HS2RC`
- `status` `documented` -> `end_of_life` (both OPNs list lifecycle "EOL")
- `module_interfaces` QSFP112: `count` `null` -> `2`, `speed` `null` -> `100Gb/s long-haul (DWDM-ready)`
- `source_url` `https://networking-docs.nvidia.com/switches#nvidiatab-hw-documentation` -> `https://networking-docs.nvidia.com/metrox3xc`
  Source: https://networking-docs.nvidia.com/metrox3xc

### Skyway-3 (new in this run)
- `source_url` `https://networking-docs.nvidia.com/skyway3` -> `https://networking-docs.nvidia.com/skyway3hw` (old URL now returns HTTP 404; OPNs `920-9B02D-00RG-CF0` / `MGA400-XS2` unchanged).
  Source: https://networking-docs.nvidia.com/skyway3hw

### InfiniBand XDR switches (carried over from 2026-10-21)
- **Q3200-RA**: `part_numbers` `[]` -> `['920-9B34F-00RX-FS0']`
- **Q3400-RA**: `part_numbers` `[]` -> `['920-9B36F-00RX-8S0']`
- **Q3401-RD**: `part_numbers` `[]` -> `['920-9B36P-00RX-8S0']`
- **Q3450-LD** (silicon photonics, CPO): `part_numbers` `[]` -> `['920-9B36M-00MX-8ES']`
  Source: https://networking-docs.nvidia.com/xdrswitcheshw

### ConnectX-8 (carried over from 2026-10-21)
- **C8180**: `part_numbers` `['900-9X81E-00EX-ST0']` -> `['900-9X81E-00EX-ST0', '900-9X81E-00EX-DT0']`
- **ConnectX-8 SuperNIC**: `part_numbers` + `900-9X81E-00EX-DT0`, `900-9X81E-00EX-SL0`; `module_interfaces` + OSFP x1 (C8180L Partner Cooled)
  Source: https://networking-docs.nvidia.com/connectx8hw

### ConnectX-9 (carried over from 2026-10-21)
- **C9180**: `part_numbers` `['900-9X91E-00EB-ST0']` -> `['900-9X91E-00EB-ST0', '900-9X91E-00EB-DT0', '900-9X91E-00QB-ST0']`
- **C9240**: `part_numbers` `['900-9X91Q-00CN-ST0']` -> `['900-9X91Q-00CN-ST0', '900-9X91Q-00RN-ST0']`
- **ConnectX-9 SuperNIC**: `part_numbers` + `900-9X91E-00EB-DT0`, `900-9X91E-00QB-ST0`, `900-9X91Q-00RN-ST0`, `900-9X91Q-00RV-ST0`, `900-9X91Q-00RC-ST0`; `module_interfaces` + QSFP112 x2 (C9220), QSFP112 x2 (C9210)
  Source: https://networking-docs.nvidia.com/connectx9hw

### ConnectX-7 (carried over from 2026-10-21)
- `part_numbers` `[]` -> 17 OPNs (`900-9X721-003N-DT0` ... `900-9X7AO-00C3-STZ`)
- `legacy_opn` `null` -> `MCX713104AC-ADAT, ... MCX75510AAS-NEAT` (17 legacy OPNs)
  Source: https://networking-docs.nvidia.com/connectx7hw

## Schema / validator

No schema change (schema v10). No compatibility-validator migration is required.

## Validation notes

HTML/layout-only differences were ignored. Landing pages (Interconnect, Switches, DPU/DOCA, Adapters, UFM, Silicon Photonics) list no new or withdrawn tracked products. SN4000 ordering page additionally lists EOL SN4600 SKUs (untracked legacy variants); not added. Two PDF manual URLs were unreachable from the runner (network error) and were not compared.
