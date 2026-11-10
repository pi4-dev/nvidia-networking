# NVIDIA Networking Inventory Change Report — 2026-11-10

Compared with repository snapshot: **2026-11-04** (schema v10, unchanged).
HTML/layout-only differences were ignored. Only substantive differences are listed.

## Added

### Transceiver `MMA4Z00-NS` (finned OSFP)
- `category`: Transceiver
- `variant`: finned
- `status`: active
- `legacy_opn`: `MMA4Z00-NS`
- `nvidia_opn`: `980-9I510-00NS00`
- `speed`: 800G, twin-port OSFP-finned, 2x 400Gb/s (2xSR4), MPO-12/APC
- `medium`: MM (850nm); reach OM3 30 m, OM4 50 m, max 50 m
- `fabric_compatibility`: IB, ETH (the product page states both protocols; the active protocol depends on the switch; Quantum-2 NDR and Spectrum-4 400GbE)
- `description`: MMA4Z00-NS 800Gb/s Twin-port OSFP, 2x400Gb/s Multimode 2xSR4, 50m
- Source: https://networking-docs.nvidia.com/800gmma4z00ns

### Transceiver `MMA4Z00-NS-FLT` (flat-top OSFP)
- `category`: Transceiver
- `variant`: flat-top
- `status`: active
- `legacy_opn`: `MMA4Z00-NS-FLT`
- `nvidia_opn`: `980-9I51A-00NS00`
- `speed`: 800G, twin-port OSFP-flattop, 2x 400Gb/s (2xSR4), MPO-12/APC
- `medium`: MM (850nm); reach OM3 30 m, OM4 50 m, max 50 m
- `fabric_compatibility`: IB, ETH
- Source: https://networking-docs.nvidia.com/800gmma4z00ns

Note: the product is linked from the LinkX index (https://networking-docs.nvidia.com/interconnect) and its ordering table (last updated 2025-10-01) lists both OPNs; neither was present in the inventory, which only held the `-T` variant (`MMA4Z00-NS-T`, `980-9I510-F4NS00`).

## Removed

None.

## Changed

None.

## Schema / validator

No schema change (v10). `compatibility-validator` device profiles gain the two transceiver entries above.

## Limitations

- The five Spectrum SN2201/SN3000/SN4000/SN5000/SN6000 hardware pages and their PDF manuals expose no machine-readable ordering tables, so switch OPNs could not be re-verified this run (retained as stored). OPNs on all other in-scope product pages were checked and match.
- Legacy (ConnectX-4/5/6, BlueField-2), OCP variants and EoL switch SKUs remain out of scope. Attribute-level (non-OPN) LinkX and Silicon Photonics changes were not machine-compared.
