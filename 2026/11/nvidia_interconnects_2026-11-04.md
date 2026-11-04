# NVIDIA Networking Inventory Change Report — 2026-11-04

Compared with repository snapshot: **2026-11-02** (schema v10, unchanged).
HTML/layout-only differences were ignored. Only substantive differences are listed.

## Added

### DPU `BlueField-3 DPU Controller (B3220SH E-Series)`
- `category`: DPU
- `status`: documented (lifecycle on source page: Mass Production)
- `legacy_opn`: none published
- `part_numbers`: `900-9D3C6-00CV-GA0` (no heatsink), `900-9D3C6-00CV-DA0` (crypto enabled), `900-9D3C6-00SV-DA0` (crypto disabled, tall bracket)
- `speed`: 200GbE (default) / NDR200 IB
- `module_interfaces`: 2x QSFP112, 200Gb/s per port
- `description`: BlueField-3 B3220SH E-Series FHHL storage controller, PCIe Gen5.0 x16, 16 Arm cores, 48GB DDR, integrated BMC
- Source: https://networking-docs.nvidia.com/bf3controllerhw
- Note: the page is linked from the BlueField DPU Controllers section of the DPU/DOCA index; the product was missing from the inventory (not a new vendor publication).

## Removed

None.

## Changed

None.

## Schema / validator

No schema change (v10). `compatibility-validator` unchanged.

## Limitations

- All in-scope index and product pages were fetched and checked by OPN; no other missing or removed OPNs were found. Legacy (ConnectX-4/5/6, BlueField-2), OCP variants, EoL switch SKUs remain out of scope.
- Attribute-level (non-OPN) changes on LinkX and Silicon Photonics pages were not machine-compared.
