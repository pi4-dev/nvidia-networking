# NVIDIA networking portfolio changes — 2026-09-17

## Latest run: schema v8 / accepted pluggable form factors

Detected a material inventory enrichment: every switch, DPU, SuperNIC and relevant appliance that accepts network modules now has an explicit normalized `accepted_pluggables` record. CPO systems are marked as non-pluggable with their fixed optical interface.

### DODANE

- **SN6810-LD** (ethernet_switching) — `accepted_pluggables`: `—`; fixed interface: `MMC-12 CPO`; source: https://www.nvidia.com/en-us/networking/ethernet-switching/
- **SN6800-LD** (ethernet_switching) — `accepted_pluggables`: `—`; fixed interface: `MMC-12 CPO`; source: https://www.nvidia.com/en-us/networking/ethernet-switching/
- **SN6600-LD** (ethernet_switching) — `accepted_pluggables`: `OSFP`; fixed interface: `—`; source: https://www.nvidia.com/en-us/networking/ethernet-switching/
- **SN6600** (ethernet_switching) — `accepted_pluggables`: `OSFP`; fixed interface: `—`; source: https://www.nvidia.com/en-us/networking/ethernet-switching/
- **SN6200-LD** (ethernet_switching) — `accepted_pluggables`: `OSFP`; fixed interface: `—`; source: https://www.nvidia.com/en-us/networking/ethernet-switching/
- **SN5610** (ethernet_switching) — `accepted_pluggables`: `OSFP, SFP28`; fixed interface: `—`; source: https://www.nvidia.com/en-us/networking/ethernet-switching/
- **SN5600** (ethernet_switching) — `accepted_pluggables`: `OSFP, SFP28`; fixed interface: `—`; source: https://www.nvidia.com/en-us/networking/ethernet-switching/
- **SN5600D** (ethernet_switching) — `accepted_pluggables`: `OSFP, SFP28`; fixed interface: `—`; source: https://www.nvidia.com/en-us/networking/ethernet-switching/
- **SN5400** (ethernet_switching) — `accepted_pluggables`: `QSFP-DD, QSFP56, QSFP28, SFP28`; fixed interface: `—`; source: https://docs.nvidia.com/networking/display/nvidia-spectrum-4-sn5000-2u-switch-systems-hardware-user-manual.pdf
- **SN4600C** (ethernet_switching) — `accepted_pluggables`: `QSFP28`; fixed interface: `—`; source: https://www.nvidia.com/en-us/networking/ethernet-switching/
- **SN4700** (ethernet_switching) — `accepted_pluggables`: `QSFP-DD, QSFP56, QSFP28`; fixed interface: `—`; source: https://www.nvidia.com/en-us/networking/ethernet-switching/
- **SN3420** (ethernet_switching) — `accepted_pluggables`: `QSFP28, SFP28`; fixed interface: `—`; source: https://www.nvidia.com/en-us/networking/ethernet-switching/
- **SN2201** (ethernet_switching) — `accepted_pluggables`: `QSFP28`; fixed interface: `RJ45`; source: https://www.nvidia.com/en-us/networking/ethernet-switching/
- **Q3200-RA** (infiniband_and_appliances) — `accepted_pluggables`: `OSFP`; fixed interface: `—`; source: https://networking-docs.nvidia.com/xdrswitcheshw/introduction
- **Q3400-RA** (infiniband_and_appliances) — `accepted_pluggables`: `OSFP`; fixed interface: `—`; source: https://networking-docs.nvidia.com/xdrswitcheshw/introduction
- **Q3401-RD** (infiniband_and_appliances) — `accepted_pluggables`: `OSFP`; fixed interface: `—`; source: https://networking-docs.nvidia.com/xdrswitcheshw/introduction
- **Q3450-LD** (infiniband_and_appliances) — `accepted_pluggables`: `—`; fixed interface: `MPO-12 CPO`; source: https://networking-docs.nvidia.com/xdrswitcheshw/introduction
- **QM9700 family** (infiniband_and_appliances) — `accepted_pluggables`: `OSFP`; fixed interface: `—`; source: https://www.nvidia.com/en-us/networking/infiniband-switching/
- **Skyway** (infiniband_and_appliances) — `accepted_pluggables`: `QSFP56`; fixed interface: `—`; source: https://www.nvidia.com/en-au/networking/infiniband/skyway/
- **MetroX-3 XC** (infiniband_and_appliances) — `accepted_pluggables`: `OSFP, QSFP112`; fixed interface: `—`; source: https://networking-docs.nvidia.com/metrox3xc
- **BlueField-3 DPU** (dpu) — `accepted_pluggables`: `QSFP112, QSFP56, QSFP28`; fixed interface: `—`; source: https://networking-docs.nvidia.com/bf3dpu/supported-interfaces
- **BlueField-4 DPU** (dpu) — `accepted_pluggables`: `QSFP112`; fixed interface: `—`; source: https://www.nvidia.com/en-eu/data-center/dgx-rubin-nvl8/
- **BlueField-4 STX Storage Processor** (dpu) — `accepted_pluggables`: `—`; fixed interface: `—`; source: https://www.nvidia.com/en-us/networking/products/data-processing-unit/
- **ConnectX-9 SuperNIC** (supernic) — `accepted_pluggables`: `OSFP (RHS cage), QSFP112`; fixed interface: `—`; source: https://networking-docs.nvidia.com/connectx9hw/specifications
- **ConnectX-8 SuperNIC** (supernic) — `accepted_pluggables`: `OSFP (RHS cage), QSFP112`; fixed interface: `—`; source: https://networking-docs.nvidia.com/connectx8hw/specifications
- **BlueField-3 SuperNIC** (supernic) — `accepted_pluggables`: `QSFP112, QSFP56, QSFP28`; fixed interface: `—`; source: https://docs.nvidia.com/networking/display/nvidia-bluefield-3-networking-platform-user-guide.pdf

### USUNIĘTE

- Brak.

### ZMIENIONE

- `schema_version`: `7 -> 8`
- dodano `port_interface_compatibility` z **26** rekordami
- CPO: SN6810-LD, SN6800-LD oraz Q3450-LD są oznaczone jako `pluggable=false` z odpowiednio MMC-12 CPO / MPO-12 CPO.
- ConnectX-8 i ConnectX-9 SuperNIC są rozbite logicznie na warianty OSFP (RHS cage) oraz QSFP112 zależnie od SKU.
- BlueField-3 DPU/SuperNIC: QSFP112 z kompatybilnością wsteczną QSFP56/QSFP28.
- BlueField-4 DPU: zapisano QSFP112 dla publicznie udokumentowanej konfiguracji DGX Rubin NVL8; nie uogólniono tego poza udokumentowany zakres.
- BlueField-4 STX: typ zewnętrznego cage pozostawiony jako niepotwierdzony w dostępnej dokumentacji publicznej, zamiast go zgadywać.

## Source URLs

- Ethernet switching: https://www.nvidia.com/en-us/networking/ethernet-switching/
- InfiniBand switching: https://www.nvidia.com/en-us/networking/infiniband-switching/
- XDR switch manual: https://networking-docs.nvidia.com/xdrswitcheshw/introduction
- ConnectX-9 SuperNIC: https://networking-docs.nvidia.com/connectx9hw/specifications
- ConnectX-8 SuperNIC: https://networking-docs.nvidia.com/connectx8hw/specifications
- BlueField-3: https://networking-docs.nvidia.com/bf3dpu/supported-interfaces
- BlueField platform: https://www.nvidia.com/en-us/networking/products/data-processing-unit/
- DGX Rubin NVL8: https://www.nvidia.com/en-eu/data-center/dgx-rubin-nvl8/
- Skyway: https://www.nvidia.com/en-au/networking/infiniband/skyway/
- MetroX-3 XC: https://networking-docs.nvidia.com/metrox3xc

## Portfolio status

No new or removed Ethernet switch, InfiniBand switch, Silicon Photonics, DPU or SuperNIC family was detected in this run. The material change is inventory precision for module/cage compatibility.
