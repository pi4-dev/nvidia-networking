# NVIDIA Networking Inventory Change Report — 2026-11-12

Compared with repository snapshot: **2026-11-10** (schema v10, unchanged).
HTML/layout-only differences were ignored. Only substantive differences are listed.

## Added

None.

## Removed

None.

## Changed

### Ethernet switch `SN6810-LD` (Spectrum-6 CPO, OPN `920-9N64K-00LI-GC0`)
- `connectors`: `128x MMC-12 (co-packaged optics)` -> `128x MMC-16 (co-packaged optics)`
- `module_interfaces[0].interface_type`: `MMC-12` -> `MMC-16` (count 128, 800GbE, non-pluggable; unchanged)
- `description`: `... 128x MMC-12 (co-packaged optics)` -> `... 128x MMC-16 (co-packaged optics)`
- `port_interface_compatibility.fixed_interfaces`: `MMC-12 CPO` -> `MMC-16 CPO`
- Source: https://networking-docs.nvidia.com/sn6000hw/ordering-information ("Co-Packaged Optics, 128 MMC-16")

### Ethernet switch `SN6800-LD` (quad Spectrum-6 CPO, OPN `920-9N67K-00LA-GC0`)
- `connectors`: `512x MMC-12 (co-packaged optics)` -> `512x MMC-16 (co-packaged optics)`
- `module_interfaces[0].interface_type`: `MMC-12` -> `MMC-16` (count 512, 200GbE, non-pluggable; unchanged)
- `description`: `... 512x MMC-12 (co-packaged optics)` -> `... 512x MMC-16 (co-packaged optics)`
- `port_interface_compatibility.fixed_interfaces`: `MMC-12 CPO` -> `MMC-16 CPO`
- Source: https://networking-docs.nvidia.com/sn6000hw/ordering-information ("Co-Packaged Optics, 512 MMC-16")

The SN6000 manual (last updated 2026-11-04) states MMC-16 consistently in the ordering table,
introduction and specifications ("Ports Form-Factor: MMC-16", "Lanes per OSFP/MMC-16: 4x 200G PAM4").
Port counts, speeds and throughput (102.4 / 409.6 Tb/s) are unchanged.

## Schema / validator

No schema change (v10). `compatibility-validator` accepts the `MMC-16` connector family and its
SN6810-LD / SN6800-LD device profiles now use it.

## Checks performed

- LinkX index: 73 product links, active / no-longer-for-sale split matches the inventory.
- OPNs crawled from 101 product pages and sub-pages (including the SN2201/SN3000/SN4000/SN5000/SN6000
  ordering tables, now available as HTML): no in-scope OPN added or removed.

## Limitations

- Out of scope as before: EoL switch SKUs (SN3700, SN3420 ONIE/Onyx, SN4600 200GbE), legacy and OCP
  adapter variants, and accessory/cable kits (`930-*`, SN6000 cable OPNs).
- Attribute-level LinkX and Silicon Photonics data were not fully machine-compared.
