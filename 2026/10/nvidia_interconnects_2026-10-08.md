# NVIDIA Networking Inventory Change Report — 2026-10-08

Compared with repository snapshot: **2026-10-06**

## Added

### MMS4C1X FRO Gen2 1600G transceiver variants

The product family was already present in the LinkX product summary and fabric compatibility map, but its normalized detailed transceiver records were missing.

- **MMS4C10 / RHS / XDR** — OPN `980-9IAU0-00XM00`; OSFP flattop; 1600Gb/s 2xDR4; 2×MPO-12/APC; SMF; 500 m; InfiniBand XDR.
- **MMS4C10 / IHS / XDR** — OPN `980-9IAU0-00XM01`; OSFP finned; 1600Gb/s 2xDR4; 2×MPO-12/APC; SMF; 500 m; InfiniBand XDR.
- **MMS4C11 / RHS / Ethernet** — OPN `980-9IAU1-00XM00`; OSFP flattop; 1600Gb/s 2xDR4; 2×MPO-12/APC; SMF; 500 m; Ethernet.
- **MMS4C11 / IHS / Ethernet** — OPN `980-9IAU1-00XM01`; OSFP finned; 1600Gb/s 2xDR4; 2×MPO-12/APC; SMF; 500 m; Ethernet.

Source: https://networking-docs.nvidia.com/9iau000xmosfptcvr1600

## Removed

None.

## Changed

### MCA7K10 1600G-to-2×800G active copper splitter

- `part_numbers`: `[]` -> `["980-9IAO5-00X001", "980-9IAO5-00X01A", "980-9IAO5-00X002"]`
- Reach variants represented by these OPNs: 1 m, 1.5 m, 2 m.
- Source: https://networking-docs.nvidia.com/9809iao500xxxxrhs2x800/ordering-information

## Schema / validator

No schema change. Inventory remains **schema v9**; no compatibility-validator migration is required.

## Validation notes

HTML/layout-only differences were ignored. These changes repair normalization completeness against NVIDIA's published product/ordering data; they are not inferred from cosmetic documentation changes.
