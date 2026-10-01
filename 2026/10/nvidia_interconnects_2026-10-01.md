# NVIDIA Networking Inventory Change Report — 2026-10-01

Compared with repository snapshot: **2026-09-30**

## Added

### Ethernet switching
- **SN4600** — active / MP; 100GbE Spectrum-3 switch, 64× QSFP28. NVIDIA SKUs: `920-9N302-00F7-0C2`, `920-9N302-00R7-0C0`. Accepted pluggables: QSFP28. Source: https://networking-docs.nvidia.com/sn4000hw/ordering-information
- **SN4700D** — active; 400GbE Spectrum-3 DC-powered switch, 32× QSFP-DD. NVIDIA SKU: `920-9N301-00RB-NC0`; legacy OPN `MSN4700-WSARC`. Accepted pluggables: QSFP-DD/QSFP56/QSFP28. Source: https://networking-docs.nvidia.com/sn4000hw/ordering-information

### Network adapters
The inventory scope now follows NVIDIA's dedicated adapter catalog. Added a normalized **network_adapters** category covering the currently documented ConnectX families: **ConnectX-9, ConnectX-8, ConnectX-7, ConnectX-6, ConnectX-6 Dx and ConnectX-6 Lx**, including known current model/OPN and cage data where NVIDIA exposes it. Source: https://networking-docs.nvidia.com/adapters

Notable current records include:
- ConnectX-9 **C9180** — `900-9X91E-00EB-ST0` (MP), single-cage OSFP, 800GbE/XDR 800Gb/s.
- ConnectX-9 **C9240** — `900-9X91Q-00CN-ST0` (MP), dual QSFP112, 2×400GbE / 400Gb/s IB.
- ConnectX-8 **C8180** — `900-9X81E-00EX-ST0` (MP), single-cage OSFP, XDR 800Gb/s / 2×400GbE.
- ConnectX-8 **C8240** — `900-9X81Q-00CN-ST0`, dual QSFP112, 400GbE/IB.
- ConnectX-8 **C8220** — `900-9X81Q-00CV-ST0` (prototype), dual QSFP112, up to 400Gb/s aggregate.
- ConnectX-7 — current documentation retained as an adapter family; detailed OPN lifecycle is tracked from the product manuals rather than inferred.

### UFM appliances
Added a dedicated **ufm_appliances** hardware category from NVIDIA's UFM appliance catalog:
- **UFM XDR Appliance** — Gen 3.5 family.
- **UFM XDR-DC Appliance / MUA970D** — `920-9B020-10RI-0D0`, legacy `MUA9702H-2SFS-DC`.
- **UFM Cyber-AI Appliance / MUA9652H-2SF** — `920-9B020-00FH-0D0`.
- **UFM Enterprise Appliance / MUA960** — `920-9B020-00FA-0D3`, legacy `MUA9602H-2SR`.
- **UFM-SDN Appliance / MUA950** — `920-9B020-00FA-0D5`, `920-9B020-09FA-0D0`.
Source: https://networking-docs.nvidia.com/software/management-software/ufm-appliances

## Removed
None confirmed.

## Changed
- Inventory source URLs for Ethernet switches, InfiniBand switches/appliances, DPU/SuperNIC were migrated to the NVIDIA Networking Documentation catalog URLs specified for this run.
- Inventory scope expanded to include **Network adapters** and physical **UFM appliances**.
- Existing Spectrum-X Ethernet Photonics availability remains normalized as **full production**. The NVIDIA page currently contains both “Ramps to Full Production” and “Available in the second half of 2026”; this wording conflict is not treated as a product-status regression.

## Validation notes
HTML/layout-only differences were ignored. Additions above are based on product/manual presence, ordering tables and lifecycle fields, not page formatting.
