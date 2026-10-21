# NVIDIA Networking Inventory Change Report — 2026-10-21

Compared with repository snapshot: **2026-10-20** (schema v10, unchanged).

## Added

### ConnectX-8 SuperNIC
- **C8180L Partner Cooled** — OPN `900-9X81E-00EX-SL0`; single-cage OSFP, XDR 800Gb/s IB / 2x400GbE, HHHL PCIe 6 x16; Mass Production.
  Source: https://networking-docs.nvidia.com/connectx8hw

### ConnectX-9 SuperNIC
- **C9220** — OPN `900-9X91Q-00RV-ST0`; dual-port QSFP112, 400Gb/s Ethernet, PCIe 5 x16; Prototype.
- **C9210** — OPN `900-9X91Q-00RC-ST0`; dual-port QSFP112, 200Gb/s Ethernet, PCIe 4 x16; Prototype.
  Source: https://networking-docs.nvidia.com/connectx9hw

## Removed

None.

## Changed

### InfiniBand XDR switches — NVIDIA SKUs now published (`part_numbers`)
- **Q3200-RA**: `part_numbers` `[]` -> `['920-9B34F-00RX-FS0']` (lifecycle P-Rel)
- **Q3400-RA**: `part_numbers` `[]` -> `['920-9B36F-00RX-8S0']` (lifecycle P-Rel)
- **Q3401-RD**: `part_numbers` `[]` -> `['920-9B36P-00RX-8S0']` (lifecycle P-Rel)
- **Q3450-LD** (silicon photonics, CPO): `part_numbers` `[]` -> `['920-9B36M-00MX-8ES']` (lifecycle Prototype)
  Source: https://networking-docs.nvidia.com/xdrswitcheshw

### ConnectX-8 (adapter `C8180`, SuperNIC)
- **C8180**: `part_numbers` `['900-9X81E-00EX-ST0']` -> `['900-9X81E-00EX-ST0', '900-9X81E-00EX-DT0']` (DT0 = PCIe Down Stream Port variant, Mass Production)
- **ConnectX-8 SuperNIC**: `part_numbers` + `900-9X81E-00EX-DT0`, `900-9X81E-00EX-SL0`; `module_interfaces` + OSFP x1 (C8180L Partner Cooled)
  Source: https://networking-docs.nvidia.com/connectx8hw

### ConnectX-9 (adapters `C9180`, `C9240`, SuperNIC)
- **C9180**: `part_numbers` `['900-9X91E-00EB-ST0']` -> `['900-9X91E-00EB-ST0', '900-9X91E-00EB-DT0', '900-9X91E-00QB-ST0']` (DT0, QB-ST0: Prototype)
- **C9240**: `part_numbers` `['900-9X91Q-00CN-ST0']` -> `['900-9X91Q-00CN-ST0', '900-9X91Q-00RN-ST0']` (RN-ST0: Prototype)
- **ConnectX-9 SuperNIC**: `part_numbers` + `900-9X91E-00EB-DT0`, `900-9X91E-00QB-ST0`, `900-9X91Q-00RN-ST0`, `900-9X91Q-00RV-ST0`, `900-9X91Q-00RC-ST0`; `module_interfaces` + QSFP112 x2 (C9220), QSFP112 x2 (C9210)
  Source: https://networking-docs.nvidia.com/connectx9hw

### ConnectX-7 adapter — NVIDIA OPN / legacy OPN table now captured
- **ConnectX-7**: `part_numbers` `[]` -> `['900-9X721-003N-DT0', '900-9X721-003N-DT1', '900-9X766-003N-SQ0', '900-9X766-003N-SR0', '900-9X766-003N-ST0', '900-9X7AH-0039-ST1', '900-9X7AH-0039-STZ', '900-9X7AH-004N-CT0', '900-9X7AH-004N-GT0', '900-9X7AH-0076-ST0', '900-9X7AH-0078-DTZ', '900-9X7AH-0078-ST0', '900-9X7AH-0079-DTZ', '900-9X7AH-0086-SQ0', '900-9X7AH-0088-ST0', '900-9X7AO-0003-ST0', '900-9X7AO-00C3-STZ']`
- **ConnectX-7**: `legacy_opn` `null` -> `MCX713104AC-ADAT, MCX713104AS-ADAT, MCX713105AS-WEAT, MCX713106AC-CEAT, MCX713106AC-VEAT, MCX713106AS-CEAT, MCX713106AS-VEAT, MCX713114GC-GEAT, MCX713114TC-GEAT, MCX715105AS-WEAT, MCX75310AAC-NEAT, MCX75310AAS-HEAT, MCX75310AAS-NEAT, MCX755106AC-HEAT, MCX755106AS-HEAT, MCX75510AAS-HEAT, MCX75510AAS-NEAT`
  Source: https://networking-docs.nvidia.com/connectx7hw

## Schema / validator

No schema change (schema v10). No compatibility-validator migration is required.

## Validation notes

HTML/layout-only differences were ignored. All 112 product URLs in the snapshot were re-fetched (including sub-pages of each product); every stored LinkX and UFM OPN is still published, and no LinkX models were added or withdrawn on the Interconnect landing page. Switch/DPU/adapter landing pages list no new tracked product pages.
Limitations: some entries above (XDR switch SKUs, ConnectX-7 OPNs) were empty in the stored snapshot because the earlier extraction did not capture them; they are reported as differences against the stored state, not as confirmed page edits since 2026-10-20. SN2201/SN3000/SN4000 pages list additional ONIE/Onyx/Cumulus ordering variants and untracked models (e.g. SN3700); these remain outside the tracked scope and were not added.
