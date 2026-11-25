# NVIDIA Networking Inventory Change Report — 2026-11-25

Compared with repository snapshot: **2026-11-16** (schema v10, unchanged).
HTML/layout-only differences were ignored. Only substantive differences are listed.

## Added

### InfiniBand switch `Q3300-LD` (Quantum-X800)
- NVIDIA OPN: `920-9B36F-00NX-GS0` (no legacy OPN published)
- Description: NVIDIA Quantum-3 based XDR InfiniBand Switch, Q3300-LD, 3U, 144 XDR ports over
  72 OSFP cages, 48VDC, standard depth, managed, 100% liquid-cooled, rail kit
- Cages: 72x OSFP **flat-top (RHS)** data cages (144x 800Gb/s XDR, twin-port), plus 1x OSFP
  FNM (fabric management, 400Gb/s) port
- Speeds: 400/800Gb/s per port (NDR not supported); throughput 115.2 Tb/s; 4x Quantum-3 ASICs
- Mechanical/power: 3U, MGX 1.2 rack, 48VDC bus bar (OCP Barklip BK150), open-loop liquid
  cooling via 2x UQD08, no fans, no replaceable PSUs
- Source: https://networking-docs.nvidia.com/xdrswitcheshw (manual v1.6, November 2026:
  "Added the Q3300-LD systems"; OPN on the
  [Accessory and Replacement Parts](https://networking-docs.nvidia.com/xdrswitcheshw/1.6/accessory-and-replacement-parts)
  page, specifications on the
  [Specifications](https://networking-docs.nvidia.com/xdrswitcheshw/1.6/specifications) page)

## Removed

None.

## Changed

None.

## Schema / validator

No schema change (v10). The Q3300-LD row stores `OSFP-flattop` as the cage type in
`module_interfaces` and `port_interface_compatibility`. A `compatibility-validator` device
profile for Q3300-LD (72x twin-port OSFP, flat-top only, 2x800G XDR) was added.

## Checks performed

- Index pages: LinkX 72 manual links, switches, DPU/DOCA, adapters and management software:
  every in-scope link is already in the inventory.
- 96 product manuals crawled (ordering, introduction, specification, interface and revision
  pages). Pages updated since the last snapshot were reviewed:
  - SN4000 ordering information (2026-11-21): only the EoL SN4600 200GbE SKUs (out of scope)
    are listed beyond the tracked OPNs.
  - SN6000 specifications (2026-11-24): port counts, MMC-16/OSFP and throughput match.
  - ConnectX-8 revision history (2026-11-17): C8220 removal was already recorded on 2026-10-24;
    other changes concern port configurations and brackets.
  - ConnectX-9 and BlueField-3 introduction/specifications (2026-11-17): ordering tables are
    unchanged.
  - MMS1X00-NS400 (2026-11-20): receiver sensitivity corrected (not stored in the inventory).
- Silicon Photonics page: Q3450-LD (144x 800Gb/s) and Spectrum-X Ethernet Photonics (up to
  409.6 Tb/s, full production) are unchanged.

## Limitations

- Out of scope as before: EoL switch SKUs, Quantum-2/EDR/HDR switch SKUs, legacy and OCP
  adapter variants, accessory/cable kits (`930-*`) and the Q3450 CPO topology parts.
- Attribute-level LinkX data (reach, connector, speed) were not fully machine-compared.
