# NVIDIA Networking Inventory Change Report — 2026-10-24

Compared with repository snapshot: **2026-10-23** (schema v10, unchanged).
HTML/layout-only differences were ignored. Only substantive differences are listed.

## Added

None.

## Removed

### SN6200-LD (Spectrum-6 SN6000, Ethernet switch)
- The SN6000 hardware manual now lists only SN6600-LD, SN6600, SN6810-LD and SN6800-LD (page last updated 2026-10-12); SN6200-LD (1U, 32x OSFP 2x800GbE front + 256x200G backplane) is no longer documented.
  Source: https://networking-docs.nvidia.com/sn6000hw

### C8220 (ConnectX-8 network adapter, prototype)
- OPN `900-9X81Q-00CV-ST0` (dual QSFP112, up to 400Gb/s aggregate) no longer appears in the ConnectX-8 ordering table (only C8240, C8180 and variants remain).
  Source: https://networking-docs.nvidia.com/connectx8hw

## Changed

### ConnectX-8 SuperNIC
- `part_numbers`: `900-9X81Q-00CV-ST0` removed (`['900-9X81E-00EX-ST0', '900-9X81Q-00CN-ST0', '900-9X81Q-00CV-ST0', '900-9X81E-00EX-DT0', '900-9X81E-00EX-SL0']` -> `['900-9X81E-00EX-ST0', '900-9X81Q-00CN-ST0', '900-9X81E-00EX-DT0', '900-9X81E-00EX-SL0']`)
  Source: https://networking-docs.nvidia.com/connectx8hw

### Skyway (InfiniBand-to-Ethernet gateway)
- `source_url`: `https://networking-docs.nvidia.com/skyway` -> `https://networking-docs.nvidia.com/skywayhw` (old URL returns HTTP 404)
  Source: https://networking-docs.nvidia.com/skywayhw

### Legacy ConnectX adapters (old URLs return HTTP 404)
- **MCX516A-CCAT**: `source_url` `.../connectx5en` -> `https://networking-docs.nvidia.com/connectx5enhw`
- **MCX4121A-ACAT**: `source_url` `.../connectx4lx` -> `https://networking-docs.nvidia.com/connectx4lxhw`
- **MCX455A-ECAT**: `source_url` `.../connectx4` -> `https://networking-docs.nvidia.com/connectx4vpihw`

## Schema / validator

No schema change (schema v10). The validator device profile `ethernet:SN6200-LD` is removed to match the inventory.

## Validation notes

Landing pages (Interconnect, Switches, DPU/DOCA, Adapters, UFM, Silicon Photonics) list no new tracked products; the 72 LinkX product URLs are unchanged. Ordering-table OPNs were compared for pages that publish them in HTML; LinkX and some switch ordering tables are not machine-readable in HTML and were not compared. Two nvidia.com pages (DGX Rubin NVL8, Data Processing Unit) were not re-fetched.
