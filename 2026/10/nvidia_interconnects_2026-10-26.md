# NVIDIA Networking Inventory Change Report — 2026-10-26

Compared with repository snapshot: **2026-10-25** (schema v10, unchanged).
HTML/layout-only differences were ignored. Only substantive differences are listed.

## Added

None (no new product rows). One new ordering SKU was added to an existing row, see Changed.

## Removed

None.

## Changed

### SN2201 (Spectrum SN2000, 1U, 48x RJ45 + 4x QSFP28 100GbE)
- `part_numbers`: `['920-9N110-00F1-0C0', '920-9N110-00R1-0C0']` -> `['920-9N110-00F1-0C0', '920-9N110-00R1-0C0', '920-9N110-00R1-NC0']`
- `legacy_opn`: `MSN2201-CB2FC / MSN2201-CB2RC` -> `MSN2201-CB2FC / MSN2201-CB2RC / MSN2201-CSMRC`
  (new SKU `920-9N110-00R1-NC0` / `MSN2201-CSMRC`, 1GbE/100GbE, Mass Production)
  Source: https://networking-docs.nvidia.com/sn2201hw/ordering-information

### SN6600-LD (Spectrum-6, 2U liquid-cooled, 64x OSFP 2x800 Gb/s)
- `part_numbers`: `[]` -> `['920-9N62F-00LI-GC1']`
  Source: https://networking-docs.nvidia.com/sn6000hw/ordering-information

### SN6600 (Spectrum-6, 3U air-cooled, 64x OSFP 2x800 Gb/s)
- `part_numbers`: `[]` -> `['920-9N63F-00RI-3C0']`
  (64 OSFP, 1 QSFP112, 2 SFP28, 4 AC PSU, connector-to-power airflow)
  Source: https://networking-docs.nvidia.com/sn6000hw/ordering-information

### SN6810-LD (Spectrum-6 CPO, 128x MMC-12, 102.4 Tb/s)
- `part_numbers`: `[]` -> `['920-9N64K-00LI-GC0']`
  Source: https://networking-docs.nvidia.com/sn6000hw/ordering-information

### SN6800-LD (quad Spectrum-6 CPO, 512x MMC-12, 409.6 Tb/s)
- `part_numbers`: `[]` -> `['920-9N67K-00LA-GC0']`
  Source: https://networking-docs.nvidia.com/sn6000hw/ordering-information

## Schema / validator

No schema change (schema v10); `compatibility-validator` needs no change.

## Limitations

- Two PDF manuals (`docs.nvidia.com` SN5000 and BlueField-3) returned 403 and were not compared.
- Index pages are JavaScript-rendered; new products were checked via product pages' ordering tables and stored URLs only.
- SN3700 and SN4600 200GbE (EoL) SKUs listed on the SN3000/SN4000 ordering pages are not part of the inventory scope and were not added.
