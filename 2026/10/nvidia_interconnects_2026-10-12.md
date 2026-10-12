# NVIDIA Networking Inventory Change Report — 2026-10-12

Compared with repository snapshot: **2026-10-08**

## Added

### MMS4B10-XM TRO 1600G transceiver — IHS (finned) variant

The RHS (flattop) variant was already tracked; the finned IHS variant published in the ordering table was missing.

- **MMS4B10-XM / IHS / TRO** — OPN `980-9IAJ0-00XM01`; OSFP finned; 1600Gb/s 2xDR4; 2×MPO-12/APC; SMF; 500 m; Ethernet only (used in SP-6 air-cooled).
- Source: https://networking-docs.nvidia.com/mms4b10xmtro1600g

### UFM Enterprise Appliance Gen 3.0 (NDR)

- **MUA960B** — SKU/OPN `920-9B020-00RA-0D0`; legacy OPN `MUA9602H-2SRS`; NDR InfiniBand; status: documented.
- Source: https://networking-docs.nvidia.com/ufmenterprisendrhwum

## Removed

None.

## Changed

None.

## Schema / validator

No schema change. Inventory remains **schema v9**; no compatibility-validator migration is required.

## Validation notes

HTML/layout-only differences were ignored. The LinkX model list (72 products), all other OPNs, and the switch, adapter, DPU and silicon photonics landing pages showed no other substantive differences against the stored snapshot. The UFM-SDN Gen 2.0 hardware manual page is empty and was not recorded.
