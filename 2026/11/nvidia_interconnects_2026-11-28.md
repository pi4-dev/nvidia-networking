# NVIDIA Networking Inventory Change Report — 2026-11-28

Compared with repository snapshot: **2026-11-25** (schema v10, unchanged).
HTML/layout-only differences were ignored. Only substantive differences are listed.

## Added

None.

## Removed

None.

## Changed

### DPU `BlueField-4 DPU`
NVIDIA has published a BlueField-4 hardware user guide (first public release Nov. 2026, last
updated 2026-11-27). The DPU/DOCA index now links to it.

| Field | Old | New |
|---|---|---|
| `part_numbers` (NVIDIA OPN) | *(empty)* | `900-9D4B4-00CW-AA0` (B4240, dual-slot FH3/4L, air-cooled), `900-9D4B4-00CW-SA0` (B4240L, single-slot FHFL, liquid-cooled) |
| `module_interfaces` | QSFP112, count *null*, 800Gb/s | QSFP112, count **2**, **400Gb/s** per port |
| `source_url` | https://www.nvidia.com/en-eu/data-center/dgx-rubin-nvl8/ | https://networking-docs.nvidia.com/bf4dpu |
| `description` | BlueField-4 DPU, 800Gb/s: networking, storage, cybersecurity, secure multi-tenancy | adds B4240/B4240L: 2x QSFP112, 400GbE (default) / NDR IB, PCIe Gen6 x16, 64 Arm cores, 128GB LPDDR5x, integrated BMC, lifecycle Prototype |
| `port_interface_compatibility.dpu["BlueField-4 DPU"].supported_speeds` | `[]` | `400GbE`, `400Gb/s NDR` |
| `port_interface_compatibility.dpu["BlueField-4 DPU"].source_url` | DGX Rubin NVL8 page | https://networking-docs.nvidia.com/bf4dpu/supported-interfaces |
| `port_interface_compatibility.dpu["BlueField-4 DPU"].scope_note` | publicly documented DGX Rubin NVL8 configuration; family may expose additional SKUs | *(removed)* |

- No legacy OPN is published. Lifecycle for both OPNs is **Prototype**. Status stays `documented`.
- Discrepancy: the [Specifications](https://networking-docs.nvidia.com/bf4dpu/specifications)
  page lists the B4240L OPN as `900-9D4C4-00CW-SA0`. The ordering table and
  [Supported Interfaces](https://networking-docs.nvidia.com/bf4dpu/supported-interfaces) page
  use `900-9D4B4-00CW-SA0`, which is the OPN recorded.
- Sources: https://networking-docs.nvidia.com/bf4dpu (ordering part numbers),
  [Specifications](https://networking-docs.nvidia.com/bf4dpu/specifications),
  [Document Revision History](https://networking-docs.nvidia.com/bf4dpu/document-revision-history)

## Schema / validator

No schema change (v10). The `compatibility-validator` profile `dpu:BlueField-4 DPU` now states 2
QSFP112 cages and cites the bf4dpu Supported Interfaces page. The DGX Rubin scope note is removed.

## Checks performed

- Index pages (LinkX, switches, DPU/DOCA, adapters, management software): the only new in-scope link
  is `bf4dpu`. All other unlisted links are out of scope as before.
- 97 product manuals crawled (702 pages, including the new bf4dpu manual). Only bf4dpu pages were updated on or after 2026-11-25.
- Silicon Photonics page: Q3450-LD (144x 800Gb/s) and Spectrum-X Ethernet Photonics (up to
  409.6 Tb/s, full production) are unchanged.

## Limitations

- Out of scope as before: EoL switch SKUs, Quantum-2/EDR/HDR switch SKUs, legacy and OCP
  adapter variants, BlueField-2 products, accessory/cable kits (`930-*`).
- Attribute-level LinkX data (reach, connector, speed) were not fully machine-compared.
