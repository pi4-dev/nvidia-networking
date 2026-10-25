# NVIDIA Networking Inventory Change Report — 2026-10-25

Compared with repository snapshot: **2026-10-24** (schema v10, unchanged).
HTML/layout-only differences were ignored. Only substantive differences are listed.

## Added

None.

## Removed

None.

## Changed

### Skyway (InfiniBand-to-Ethernet gateway)
- `part_numbers`: `[]` -> `['920-9B020-00FA-0D2']`
- `legacy_opn`: `null` -> `MGA100-HS2`
  (ordering table: 8x IB + 8x Ethernet ports, 2U, 8x ConnectX-6 VPI dual-port HDR/200GbE, 2 PSU AC)
  Source: https://networking-docs.nvidia.com/skywayhw

### MCX455A-ECAT (ConnectX-4 InfiniBand/Ethernet, legacy)
- `part_numbers`: `['MCX455A-ECAT']` -> `['900-9X4AC-0016-ST0']`
- `legacy_opn`: `null` -> `MCX455A-ECAT`
  Source: https://networking-docs.nvidia.com/connectx4vpihw

### MCX4121A-ACAT (ConnectX-4 Lx Ethernet, legacy)
- `part_numbers`: `['MCX4121A-ACAT']` -> `['900-9X4B0-0053-0T1']`
- `legacy_opn`: `null` -> `MCX4121A-ACAT`
  Source: https://networking-docs.nvidia.com/connectx4lxhw

### MCX516A-CCAT (ConnectX-5 Ethernet, legacy)
- `part_numbers`: `['MCX516A-CCAT']` -> `['900-9X5AD-0056-ST1']`
- `legacy_opn`: `null` -> `MCX516A-CCAT`
  Source: https://networking-docs.nvidia.com/connectx5enhw

## Schema / validator

No schema change (schema v10); `compatibility-validator` needs no change.

## Validation notes

Landing pages (Interconnect, Switches, Adapters, DPU/DOCA, UFM/management software, Silicon Photonics) list no new or removed tracked products; the LinkX product URLs are unchanged. OPNs were compared for every stored source URL whose ordering table is present in static HTML; LinkX and several switch ordering tables are not machine-readable in HTML and were not compared. The OPN differences above are ordering-table data newly captured in the inventory, not confirmed new NVIDIA publications.
