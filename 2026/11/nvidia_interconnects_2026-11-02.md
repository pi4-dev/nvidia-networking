# NVIDIA Networking Inventory Change Report — 2026-11-02

Compared with repository snapshot: **2026-10-26** (schema v10, unchanged).
HTML/layout-only differences were ignored. Only substantive differences are listed.

## Added

### UFM appliance `MUA970` (UFM Enterprise Gen 3.5, XDR)
- `category`: UFM appliance
- `status`: active
- `legacy_opn`: `MUA9702H-2SFS`
- `part_numbers`: `['920-9B020-00RI-0D0']`
- `description`: UFM Appliance 3.5 for UFM Telemetry or UFM Enterprise, 1U, 2x ConnectX-8 single-port 400Gb/s InfiniBand adapters (UFM license sold separately, UFM SW installed)
- Source: https://networking-docs.nvidia.com/ufmenterprisexdrhw
- Note: the page was already published; the AC-powered `MUA970` was missing from the inventory (only the DC variant `MUA970D` was tracked).

## Removed

None.

## Changed

None.

## Schema / validator

No schema change (v10). `compatibility-validator` unchanged.

## Limitations

- Ordering tables of the SN2000/SN3000/SN4000/SN5000/SN6000 pages, ConnectX-7/8/9, BlueField-3, Skyway, MetroX-3 and XDR UFM pages were compared by OPN; all other OPNs already in the inventory were found.
- Legacy (ConnectX-4/5/6, BlueField-2), OCP variants, EoL SN3000/SN4600 SKUs and Quantum-2/EDR/HDR switch SKUs remain outside the inventory scope and were not added.
- Attribute-level (non-OPN) changes on LinkX pages and Silicon Photonics page were not machine-compared; no differences were noticed.
