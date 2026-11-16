# NVIDIA Networking Inventory Change Report — 2026-11-16

Compared with repository snapshot: **2026-11-12** (schema v10, unchanged).
HTML/layout-only differences were ignored. Only substantive differences are listed.

## Added

None.

## Removed

None.

## Changed

### LinkX transceiver `MMS4X90-NR` (800G twin-port 2xLR4, finned OSFP, 2x duplex LC, SMF, 10 km)
- `part_numbers` (NVIDIA OPN): `[]` -> `['980-9IB70-00YL00']`
- `legacy_opn`: `null` -> `MMS4X90-NR`
- Applies to both the LinkX `active` summary row and the detailed `transceivers` row.
- Source: https://networking-docs.nvidia.com/mms4x90nr800g/ordering-information-v1-0
  ("Legacy PN MMS4X90-NR, Ordering PN 980-9IB70-00YL00, NVIDIA twin port transceiver, 800Gbps,
  2xLR4, OSFP, 2xLC-LC, 1310nm SMF, up to 10km, finned")

The OPN was previously left empty because the main
[Ordering Information](https://networking-docs.nvidia.com/mms4x90nr800g/ordering-information)
page lists the MMS4X50-NM OPN (`980-9I30L-00N000`). That page still does. The product's
"Ordering Information v1.0" page gives an OPN and description that match MMS4X90-NR. Both pages
were last updated 2026-04-13, so this fills a gap in the data rather than reflecting a new
change on the source.

## Schema / validator

No schema change (v10). The `compatibility-validator` device profile for MMS4X90-NR does not
store OPNs, so it is unchanged.

## Checks performed

- LinkX index: 74 product links (43 active, 31 no longer for sale). The status split matches
  the inventory.
- 110 product manuals / 419 pages crawled (ordering, introduction, specification and interconnect
  pages, including versioned sub-pages). No in-scope OPN was added or removed apart from the
  item above.
- Silicon Photonics page: Q3450-LD (144x 800Gb/s) and Spectrum-X Ethernet Photonics (up to
  409.6 Tb/s, full production) are unchanged.
- Pages updated since the last snapshot (ConnectX-8/9, BlueField-3, SN6000 and Quantum-X800
  manuals, 2026-11-04 to 2026-11-11): the OPNs, lifecycle values and port configurations
  checked match the inventory.

## Limitations

- Out of scope as before: EoL switch SKUs (SN3700, SN3420, SN4600 200GbE), Quantum-2/EDR/HDR switch
  SKUs (QM97x0, QM87xx, SB77x0), legacy and OCP adapter variants, accessory/cable kits (`930-*`,
  SN6000 cable OPNs) and the Q3450 CPO topology parts listed in the XDR cable-installation page.
- Attribute-level LinkX data (reach, connector, speed) were not fully machine-compared.
