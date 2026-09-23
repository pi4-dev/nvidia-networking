# NVIDIA Network Equipment

_Snapshot **2026-09-23**, schema **v8**, Europe/Warsaw._

`IB` = InfiniBand, `ETH` = Ethernet, `NVL` = NVLink/NVL. OSFP finned/flat-top variants are separate where NVIDIA publishes distinct OPNs.

## Module / cage compatibility

| Category | Model | Pluggable | Accepted pluggables | Fixed | Notes | Source |
|---|---|:---:|---|---|---|---|
| ethernet_switching | SN6810-LD | no | — | MMC-12 CPO | — | [NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/) |
| ethernet_switching | SN6800-LD | no | — | MMC-12 CPO | — | [NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/) |
| ethernet_switching | SN6600-LD | yes | OSFP | — | — | [NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/) |
| ethernet_switching | SN6600 | yes | OSFP | — | — | [NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/) |
| ethernet_switching | SN6200-LD | yes | OSFP | — | — | [NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/) |
| ethernet_switching | SN5610 | yes | OSFP, SFP28 | — | — | [NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/) |
| ethernet_switching | SN5600 | yes | OSFP, SFP28 | — | — | [NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/) |
| ethernet_switching | SN5600D | yes | OSFP, SFP28 | — | — | [NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/) |
| ethernet_switching | SN5400 | yes | QSFP-DD, QSFP56, QSFP28, SFP28 | — | — | [NVIDIA](https://docs.nvidia.com/networking/display/nvidia-spectrum-4-sn5000-2u-switch-systems-hardware-user-manual.pdf) |
| ethernet_switching | SN4600C | yes | QSFP28 | — | — | [NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/) |
| ethernet_switching | SN4700 | yes | QSFP-DD, QSFP56, QSFP28 | — | — | [NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/) |
| ethernet_switching | SN3420 | yes | QSFP28, SFP28 | — | — | [NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/) |
| ethernet_switching | SN2201 | yes | QSFP28 | RJ45 | — | [NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/) |
| infiniband_and_appliances | Q3200-RA | yes | OSFP | — | — | [NVIDIA](https://networking-docs.nvidia.com/xdrswitcheshw/introduction) |
| infiniband_and_appliances | Q3400-RA | yes | OSFP | — | — | [NVIDIA](https://networking-docs.nvidia.com/xdrswitcheshw/introduction) |
| infiniband_and_appliances | Q3401-RD | yes | OSFP | — | — | [NVIDIA](https://networking-docs.nvidia.com/xdrswitcheshw/introduction) |
| infiniband_and_appliances | Q3450-LD | no | — | MPO-12 CPO | — | [NVIDIA](https://networking-docs.nvidia.com/xdrswitcheshw/introduction) |
| infiniband_and_appliances | QM9700 family | yes | OSFP | — | — | [NVIDIA](https://www.nvidia.com/en-us/networking/infiniband-switching/) |
| infiniband_and_appliances | Skyway | yes | QSFP56 | — | — | [NVIDIA](https://www.nvidia.com/en-au/networking/infiniband/skyway/) |
| infiniband_and_appliances | MetroX-3 XC | yes | OSFP, QSFP112 | — | OSFP on ConnectX-7 IB-facing ports; 2x QSFP112 long-haul ports | [NVIDIA](https://networking-docs.nvidia.com/metrox3xc) |
| dpu | BlueField-3 DPU | yes | QSFP112, QSFP56, QSFP28 | — | — | [NVIDIA](https://networking-docs.nvidia.com/bf3dpu/supported-interfaces) |
| dpu | BlueField-4 DPU | yes | QSFP112 | — | publicly documented DGX Rubin NVL8 configuration; family may expose additional SKUs | [NVIDIA](https://www.nvidia.com/en-eu/data-center/dgx-rubin-nvl8/) |
| dpu | BlueField-4 STX Storage Processor | unknown | — | — | public portfolio confirms ConnectX-9 networking but accessible public source does not expose external cage type | [NVIDIA](https://www.nvidia.com/en-us/networking/products/data-processing-unit/) |
| supernic | ConnectX-9 SuperNIC | yes | OSFP (RHS cage), QSFP112 | — | — | [NVIDIA](https://networking-docs.nvidia.com/connectx9hw/specifications) |
| supernic | ConnectX-8 SuperNIC | yes | OSFP (RHS cage), QSFP112 | — | — | [NVIDIA](https://networking-docs.nvidia.com/connectx8hw/specifications) |
| supernic | BlueField-3 SuperNIC | yes | QSFP112, QSFP56, QSFP28 | — | — | [NVIDIA](https://docs.nvidia.com/networking/display/nvidia-bluefield-3-networking-platform-user-guide.pdf) |

## Transceivers

| Model | Variant | Status | Part numbers | Speed | Form factor | Medium | Interfaces | Reach | Fabric | Source |
|---|---|---|---|---:|---|---|---|---|---|---|
| MMS4B10-XM | RHS/TRO | active | 980-9IAJ0-00XM00 | 1600G | OSFP-flattop | SM | 2× 800Gb/s MPO-12/APC | {"max_m":500} | ETH | [NVIDIA](https://networking-docs.nvidia.com/mms4b10xmtro1600g) |
| MMS4C10 | RHS/FRO Gen2 (XDR) | active | 980-9IAU0-00XM00 | 1600G | OSFP-flattop | SM | 2× 800Gb/s MPO-12/APC | {"max_m":500} | IB | [NVIDIA](https://networking-docs.nvidia.com/9iau000xmosfptcvr1600) |
| MMS4C10 | IHS/FRO Gen2 (XDR) | active | 980-9IAU0-00XM01 | 1600G | OSFP-finned | SM | 2× 800Gb/s MPO-12/APC | {"max_m":500} | IB | [NVIDIA](https://networking-docs.nvidia.com/9iau000xmosfptcvr1600) |
| MMS4C11 | RHS/FRO Gen2 (Ethernet) | active | 980-9IAU1-00XM00 | 1600G | OSFP-flattop | SM | 2× 800Gb/s MPO-12/APC | {"max_m":500} | ETH | [NVIDIA](https://networking-docs.nvidia.com/9iau000xmosfptcvr1600) |
| MMS4C11 | IHS/FRO Gen2 (Ethernet) | active | 980-9IAU1-00XM01 | 1600G | OSFP-finned | SM | 2× 800Gb/s MPO-12/APC | {"max_m":500} | ETH | [NVIDIA](https://networking-docs.nvidia.com/9iau000xmosfptcvr1600) |
| MMS4A00 | IHS | active | 980-9IAH1-00XM00 | 1600G | OSFP-finned | SM | 2× 800Gb/s MPO-12/APC | {"max_m":500} | IB | [NVIDIA](https://networking-docs.nvidia.com/9iahx00xmosfptcvr1600) |
| MMA1Z00-NS400 | — | active | 980-9I693-00NS00 | 400G | QSFP112 | MM | 1× 400Gb/s MPO-12/APC | {"OM3_m":30,"OM4_m":50,"max_m":50} | IB,ETH | [NVIDIA](https://networking-docs.nvidia.com/mms1z00ns400sr4) |
| MMS1V00-WM | — | active | 980-9I16Y-00W000 | 400G | QSFP-DD | SM | 1× 400Gb/s MPO-12/APC | {"max_m":500} | ETH | [NVIDIA](https://networking-docs.nvidia.com/mms1v00wm10) |
| MMS4X00-NS400 | — | active | 980-9I31N-00NM00 | 400G | OSFP-flattop | SM | 1× 400Gb/s MPO-12/APC | {"max_m":100} | IB,ETH | [NVIDIA](https://networking-docs.nvidia.com/mms4x00ns400) |
| MMA4Z00-NS400 | — | active | 980-9I51S-00NS00 | 400G | OSFP-flattop | MM | 1× 400Gb/s MPO-12/APC | {"OM3_m":30,"OM4_m":50,"max_m":50} | IB,ETH | [NVIDIA](https://networking-docs.nvidia.com/mma4z00ns400) |
| MMA4Z00-NS400-T | — | active | 980-9I51S-F4NS00 | 400G | OSFP-flattop | MM | 1× 400Gb/s MPO-12/APC | {"max_m":50} | ETH | [NVIDIA](https://networking-docs.nvidia.com/mma4z00ns400t) |
| MMA1Z00-NS400-T | — | active | 980-9I693-F4NS00 | 400G | QSFP112 | MM | 1× 400Gb/s MPO-12/APC | {"max_m":50} | ETH | [NVIDIA](https://networking-docs.nvidia.com/mma1z00ns400t) |
| MMS1X00-NS400 | — | active | 980-9I068-00NM00 | 400G | QSFP112 | SM | 1× 400Gb/s MPO-12/APC | {"max_m":500,"ordering_description_max_m":100} | IB,ETH | [NVIDIA](https://networking-docs.nvidia.com/mms1x00ns400) |
| MMS1V70-CM | — | active | 980-9I042-00C000 | 100G | QSFP28 | SM | 1× 100Gb/s LC duplex | {"max_m":500} | ETH | [NVIDIA](https://networking-docs.nvidia.com/mms1v70cm10) |
| MMA1B00-C100D | — | active | 980-9I149-00CS00 | 100G | QSFP28 | MM | 1× 100Gb/s MPO-12/UPC | {"OM3_m":70,"OM4_m":100,"max_m":100} | ETH | [NVIDIA](https://networking-docs.nvidia.com/mma1b00c100dspec) |
| MMS4C10-XM800 | RHS/FRO Gen2 | prototype | 980-9IAY0-00XM00 | 800G | OSFP-flattop | SM | 1× 800Gb/s MPO-12/APC | {"max_m":500} | IB,ETH | [NVIDIA](https://networking-docs.nvidia.com/mms4c1x800) |
| MMS4X00-NM-T | — | active | 980-9I30G-F4NM00 | 800G | OSFP-finned | SM | 2× 400Gb/s MPO-12/APC | {"max_m":500} | ETH | [NVIDIA](https://networking-docs.nvidia.com/mms4x00nmt800g) |
| MMS4X00-NM | finned | active | 980-9I30G-00NM00 | 800G | OSFP-finned | SM | 2× 400Gb/s MPO-12/APC | {"max_m":500} | IB,ETH | [NVIDIA](https://networking-docs.nvidia.com/mms4x00nm800g500m) |
| MMS4X00-NM-FLT | flat-top | active | 980-9I301-00NM00 | 800G | OSFP-flattop | SM | 2× 400Gb/s MPO-12/APC | {"max_m":500} | IB,ETH | [NVIDIA](https://networking-docs.nvidia.com/mms4x00nm800g500m) |
| MMS4X50-NM | — | active | 980-9I30L-00N000 | 800G | OSFP-finned | SM | 2× 400Gb/s Duplex LC | {"max_m":2000} | IB,ETH | [NVIDIA](https://networking-docs.nvidia.com/mms4x50nm800g2kmpub) |
| MMS4X00-NS | finned | active | 980-9I30H-00NM00 | 800G | OSFP-finned | SM | 2× 400Gb/s MPO-12/APC | {"max_m":100} | IB,ETH | [NVIDIA](https://networking-docs.nvidia.com/800gmms4x00ns) |
| MMS4X00-NS-FLT | flat-top | active | 980-9I30I-00NM00 | 800G | OSFP-flattop | SM | 2× 400Gb/s MPO-12/APC | {"max_m":100} | IB,ETH | [NVIDIA](https://networking-docs.nvidia.com/800gmms4x00ns) |
| MMA4Z00-NS-T | — | active | 980-9I510-F4NS00 | 800G | OSFP-finned | MM | 2× 400Gb/s MPO-12/APC | {"OM3_m":30,"OM4_m":50,"max_m":50} | ETH | [NVIDIA](https://networking-docs.nvidia.com/800gmma4z00nst) |
| MMS4X00-NS-T | — | active | 980-9I30H-F4NM00 | 800G | OSFP-finned | SM | 2× 400Gb/s MPO-12/APC | {"max_m":100} | ETH | [NVIDIA](https://networking-docs.nvidia.com/800gmms4x00nst) |
| MMS4A20 | RHS | active | 980-9IAT0-00XM00 | 800G | OSFP-flattop | SM | 1× 800Gb/s MPO-12/APC | {"max_m":500} | IB | [NVIDIA](https://networking-docs.nvidia.com/9iat0mosfp800sprhs) |
| MMS4X00-NM16 | — | active | 980-9I30J-F4NM00 | 800G | OSFP-finned | SM | 1× 800Gb/s MPO-16/APC | {"max_m":500} | ETH | [NVIDIA](https://networking-docs.nvidia.com/mms4x00nm16) |
| MMS4X00-NM-HGX | HGX Rubin NVL8 | active | 980-9I302-00NM00 | 800G | OSFP-flattop | SM | 2× 400Gb/s MPO-12/APC | {"max_m":500} | IB,ETH,NVL | [NVIDIA](https://networking-docs.nvidia.com/mms4x00nmhgx500) |
| MMS4X90-NR | — | active | — | 800G | OSFP-finned | SM | 2× 400Gb/s Duplex LC | {"max_m":10000} | IB,ETH | [NVIDIA](https://networking-docs.nvidia.com/mms4x90nr800g) |
| MMS1W50-HM | — | active | MMS1W50-HM | 200G | QSFP56 | SM | 1× 200Gb/s Duplex LC/UPC | {"max_m":2000} | IB | [NVIDIA](https://networking-docs.nvidia.com/mms1w50hmspec) |
| MMA2P00-AS | — | active | MMA2P00-AS | 25G | SFP28 | MM | 1× 25Gb/s Duplex LC/UPC | {"OM3_m":70,"OM4_m":100,"max_m":100} | ETH | [NVIDIA](https://networking-docs.nvidia.com/mma2p00asspec) |

## AOC

| Model | Variant | Status | Part numbers | Speed | Interfaces | Medium | Reach | Fabric | Source |
|---|---|---|---|---:|---|---|---|---|---|
| MFA7U10-H00x | finned OSFP head | active | 980-9I41X-00H003, 980-9I11Z-00H005, 980-9I111-00H010, 980-9I113-00H015, 980-9I115-00H020, 980-9I117-00H030 | 400G | OSFP-finned -> 2xQSFP56; 2× 2x200Gb/s OSFP to 2xQSFP56 | MM | {"max_m":30} | IB,ETH | [NVIDIA](https://networking-docs.nvidia.com/mfa7u10h00x10) |
| MFA7U10-H00x-FLT | flat-top OSFP head | active | 980-9I41Y-00H003, 980-9I110-00H005, 980-9I112-00H010, 980-9I114-00H015, 980-9I116-00H020, 980-9I118-00H030 | 400G | OSFP-flattop -> 2xQSFP56; 2× 2x200Gb/s OSFP to 2xQSFP56 | MM | {"max_m":30} | IB,ETH | [NVIDIA](https://networking-docs.nvidia.com/mfa7u10h00x10) |
| MFS1S00-HxxxV | — | active | 980-9I457-00H003, 980-9I45D-00H005, 980-9I45J-00H010, 980-9I45O-00H015, 980-9I45T-00H020, 980-9I440-00H030, 980-9I447-00H050, 980-9I44H-00H100 | 200G | QSFP56; 1× 200Gb/s QSFP56 to QSFP56 | MM | {"max_m":100} | IB,ETH | [NVIDIA](https://networking-docs.nvidia.com/mfs1s00hxxxv10) |

## Copper / DAC / ACC

| Model | Variant | Status | Part numbers | Speed | Interfaces | Medium | Reach | Fabric | Source |
|---|---|---|---|---:|---|---|---|---|---|
| MCA4K00 | RHS-to-RHS | active | 980-9IAM1-00X001, 980-9IAM2-00X001, 980-9IAM4-00X001 | 1600G | OSFP-flattop -> OSFP-flattop; 1× 1600Gb/s OSFP to OSFP | Copper | {"max_m":1.1} | IB,ETH,NVL | [NVIDIA](https://networking-docs.nvidia.com/mca4k00hw) |
| MCA4K50 | IHS-to-IHS | active | 980-9IAM5-00X001, 980-9IAM5-00X01A, 980-9IAM3-00X002, 980-9IAM3-00X02A, 980-9IAM3-00X003 | 1600G | OSFP-finned -> OSFP-finned; 1× 1600Gb/s OSFP to OSFP | Copper | {"max_m":3} | IB | [NVIDIA](https://networking-docs.nvidia.com/mca4k50osfp1600) |
| MCA7K10 | IHS-to-2xRHS | active | — | 1600G | OSFP-finned -> 2xOSFP-flattop; 2× 2x800Gb/s OSFP to 2xOSFP | Copper | {"max_m":2} | IB,ETH | [NVIDIA](https://networking-docs.nvidia.com/9809iao500xxxxrhs2x800) |
| MCA4J80-Nxxx | finned | active | 980-9I60Z-00N003, 980-9I601-00N004, 980-9I602-00N005 | 800G | OSFP-finned -> OSFP-finned; 2× 2x400Gb/s OSFP to OSFP | Copper | {"max_m":5} | IB | [NVIDIA](https://networking-docs.nvidia.com/mca4j80nxxx800pub) |
| MCA4J80-Nxxx-FLT | flat-top | active | 980-9I600-00N003 | 800G | OSFP-flattop -> OSFP-flattop; 2× 2x400Gb/s OSFP to OSFP | Copper | {"max_m":3} | IB | [NVIDIA](https://networking-docs.nvidia.com/mca4j80nxxx800pub) |
| MCA4J80-Nxxx-FTF | flat-to-finned | active | 980-9I601-00N003 | 800G | OSFP-flattop -> OSFP-finned; 2× 2x400Gb/s OSFP to OSFP | Copper | {"max_m":3} | IB | [NVIDIA](https://networking-docs.nvidia.com/mca4j80nxxx800pub) |
| MCP4Y10-Nxxx | finned | active | 980-9IA0K-00N00A, 980-9IA0F-00N001, 980-9IA0Q-00N01A, 980-9IA0I-00N002 | 800G | OSFP-finned -> OSFP-finned; 2× 2x400Gb/s OSFP to OSFP | Copper | {"max_m":2} | IB,ETH | [NVIDIA](https://networking-docs.nvidia.com/mcp4y10nxxx2x400pub) |
| MCP4Y10-Nxxx-FLT | flat-top | active | 980-9IA0L-00N00A, 980-9IA0G-00N001, 980-9IA0J-00N002 | 800G | OSFP-flattop -> OSFP-flattop; 2× 2x400Gb/s OSFP to OSFP | Copper | {"max_m":2} | IB,ETH | [NVIDIA](https://networking-docs.nvidia.com/mcp4y10nxxx2x400pub) |
| MCP7Y00-Nxxx | finned head | active | MCP7Y00-N001, MCP7Y00-N01A, MCP7Y00-N002, MCP7Y00-N02A, MCP7Y00-N003 | 800G | OSFP-finned -> 2xOSFP-flattop; 2× 2x400Gb/s OSFP to 2xOSFP | Copper | {"max_m":3} | IB,ETH | [NVIDIA](https://networking-docs.nvidia.com/mcp7y00nxxx800pub) |
| MCP7Y00-Nxxx-FLT | flat-top head | active | MCP7Y00-N001-FLT1, MCP7Y00-N01A-FLT, MCP7Y00-N002-FLT | 800G | OSFP-flattop -> 2xOSFP-flattop; 2× 2x400Gb/s OSFP to 2xOSFP | Copper | {"max_m":2} | IB,ETH | [NVIDIA](https://networking-docs.nvidia.com/mcp7y00nxxx800pub) |
| MCP1600-E0xxEyy | — | active | MCP1600-E00AE30, MCP1600-E001E30, MCP1600-E01AE30, MCP1600-E002E30, MCP1600-E02AE26, MCP1600-E003E26, MCP1600-E004E26, MCP1600-E005E26 | 100G | QSFP28; 1× 100Gb/s QSFP28 to QSFP28 | Copper | {"max_m":5} | IB | [NVIDIA](https://networking-docs.nvidia.com/mcp1600e0xxxeyyspec) |

## Ethernet switching

| Model | Collected fields | Accepted pluggables | Source |
|---|---|---|---|
| SN6810-LD | family="Spectrum-6 SN6000"; speed="800GbE"; connectors="128x MMC-12 (co-packaged optics)"; port_counts={"800G":128,"400G":256,"200G":512,"100G":514}; throughput="102.4 Tb/s"; height="2U"; cooling="liquid-cooled/CPO family" | MMC-12 CPO | [NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/) |
| SN6800-LD | family="Spectrum-6 SN6000"; speed="200GbE"; connectors="512x MMC-12 (co-packaged optics)"; port_counts={"200G":2048,"100G":2056}; throughput="409.6 Tb/s (4x 102.4 Tb/s)"; height="5U"; cooling="liquid-cooled/CPO family" | MMC-12 CPO | [NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/) |
| SN6600-LD | family="Spectrum-6 SN6000"; speed="800GbE"; connectors="64x OSFP 2x800 Gb/s"; port_counts={"800G":128,"400G":256,"200G":512,"100G":514}; throughput="102.4 Tb/s"; height="2U"; cooling="liquid-cooled" | OSFP | [NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/) |
| SN6600 | family="Spectrum-6 SN6000"; speed="800GbE"; connectors="64x OSFP 2x800 Gb/s"; port_counts={"800G":128,"400G":256,"200G":512,"100G":514}; throughput="102.4 Tb/s"; height="3U"; cooling="air-cooled" | OSFP | [NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/) |
| SN6200-LD | family="Spectrum-6 SN6000"; speed="200GbE"; connectors="32x OSFP 2x800GbE front + 256x200G backplane"; port_counts={"200G":256,"100G":258}; throughput="102.4 Tb/s"; height="1U"; cooling="liquid-cooled" | OSFP | [NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/) |
| SN5610 | family="Spectrum-4 SN5000"; speed="800GbE"; connectors="64x OSFP 800GbE + 2x SFP28 25GbE"; port_counts={"800G":64,"400G":128,"200G":256,"100G":256,"25G":258}; throughput="51.2 Tb/s; 33.3 Bpps"; height="2U"; cooling=null | OSFP, SFP28 | [NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/) |
| SN5600 | family="Spectrum-4 SN5000"; speed="800GbE"; connectors="64x OSFP 800GbE + 1x SFP28 25GbE"; port_counts={"800G":64,"400G":128,"200G":256,"100G":256,"25G":257}; throughput="51.2 Tb/s; 33.3 Bpps"; height="2U"; cooling=null | OSFP, SFP28 | [NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/) |
| SN5600D | family="Spectrum-4 SN5000"; speed="800GbE"; connectors="64x OSFP 800GbE + 1x SFP28 25GbE"; port_counts={"800G":64,"400G":128,"200G":256,"100G":256,"25G":257}; throughput="51.2 Tb/s; 33.3 Bpps"; height="2U"; cooling=null | OSFP, SFP28 | [NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/) |
| SN5400 | family="Spectrum-4 SN5000"; speed="400GbE"; connectors="64x QSFP-DD 400GbE + 2x SFP28 25GbE"; port_counts={"400G":64,"200G":128,"100G":256,"25G":258}; throughput="25.6 Tb/s; 33.3 Bpps"; height="2U"; cooling=null | QSFP-DD, QSFP56, QSFP28, SFP28 | [NVIDIA](https://docs.nvidia.com/networking/display/nvidia-spectrum-4-sn5000-2u-switch-systems-hardware-user-manual.pdf) |
| SN4600C | family="Spectrum-3 SN4000"; speed="100GbE"; connectors="64x QSFP28 100GbE"; port_counts={"100G":64,"50G":128,"40G":64,"25G":128}; throughput="6.4 Tb/s; 8.4 Bpps"; height="2U"; cooling=null | QSFP28 | [NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/) |
| SN4700 | family="Spectrum-3 SN4000"; speed="400GbE"; connectors="32x QSFP-DD 400GbE"; port_counts={"400G":32,"200G":64,"100G":128,"50G":128,"40G":64,"25G":128}; throughput="12.8 Tb/s; 8.4 Bpps"; height="1U"; cooling=null | QSFP-DD, QSFP56, QSFP28 | [NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/) |
| SN3420 | family="Spectrum-2 SN3000"; speed="100GbE"; connectors="12x QSFP28 100GbE + 48x SFP28 25GbE"; port_counts={"100G":12,"40G":12,"25G":96}; throughput="2.4 Tb/s; 3.57 Bpps"; height="1U"; cooling=null | QSFP28, SFP28 | [NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/) |
| SN2201 | family="Spectrum SN2000"; speed="100GbE"; connectors="48x RJ45 + 4x QSFP28 100GbE"; port_counts={"100G":4,"50G":8,"40G":4,"25G":16,"1G":48}; throughput="448 Gb/s; 667 Mpps"; height="1U"; cooling=null | QSFP28 | [NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/) |

## InfiniBand switching / appliances

| Model | Collected fields | Accepted pluggables | Source |
|---|---|---|---|
| Q3200-RA | family="Quantum-X800"; speed="800Gb/s XDR"; connectors="2x18 OSFP"; port_counts={"800G":72}; throughput="2x28.8 Tb/s"; height="2U"; cooling="air-cooled"; compatibility=["Quantum-X800","Quantum-2 storage migration"]; reach=null | OSFP | [NVIDIA](https://networking-docs.nvidia.com/xdrswitcheshw/introduction) |
| Q3400-RA | family="Quantum-X800"; speed="800Gb/s XDR"; connectors="72x OSFP"; port_counts={"800G":144}; throughput="115.2 Tb/s"; height="4U"; cooling="air-cooled"; compatibility=null; reach=null | OSFP | [NVIDIA](https://networking-docs.nvidia.com/xdrswitcheshw/introduction) |
| Q3401-RD | family="Quantum-X800"; speed="800Gb/s XDR"; connectors="72x OSFP"; port_counts={"800G":144}; throughput="115.2 Tb/s"; height="4U"; cooling="air-cooled; DC power"; compatibility=null; reach=null | OSFP | [NVIDIA](https://networking-docs.nvidia.com/xdrswitcheshw/introduction) |
| Q3450-LD | family="Quantum-X Photonics / Quantum-X800"; speed="800Gb/s XDR"; connectors="144x MPO12 CPO"; port_counts={"800G":144}; throughput="115.2 Tb/s"; height="4U"; cooling="liquid-cooled (CPO)"; compatibility=null; reach=null | MPO-12 CPO | [NVIDIA](https://networking-docs.nvidia.com/xdrswitcheshw/introduction) |
| QM9700 family | family="Quantum-2"; speed="400Gb/s NDR"; connectors="OSFP"; port_counts=null; throughput="51.2 Tb/s class"; height=null; cooling=null; compatibility=["ConnectX-7","NDR/HDR"]; reach=null | OSFP | [NVIDIA](https://www.nvidia.com/en-us/networking/infiniband-switching/) |
| Skyway | family="InfiniBand-to-Ethernet Gateway"; speed="100/200 Gb/s per port"; connectors="8 ports per InfiniBand and Ethernet side"; port_counts=null; throughput="1.6 Tb/s"; height=null; cooling=null; compatibility=["InfiniBand","Ethernet"]; reach=null | QSFP56 | [NVIDIA](https://www.nvidia.com/en-au/networking/infiniband/skyway/) |
| MetroX-3 XC | family="Long-haul InfiniBand"; speed="InfiniBand extension"; connectors=null; port_counts=null; throughput=null; height=null; cooling=null; compatibility=["DWDM","encrypted long-haul"]; reach={"max_km":40} | OSFP, QSFP112 | [NVIDIA](https://networking-docs.nvidia.com/metrox3xc) |
| UFM Telemetry | family="UFM platform"; speed=null; connectors=null; port_counts=null; throughput=null; height=null; cooling=null; compatibility=["switch/adapters/cables telemetry","on-prem/cloud database"]; reach=null | — | [NVIDIA](https://www.nvidia.com/en-us/networking/infiniband-switching/) |
| UFM Enterprise | family="UFM platform"; speed=null; connectors=null; port_counts=null; throughput=null; height=null; cooling=null; compatibility=["Slurm","IBM Spectrum LSF","REST API"]; reach=null | — | [NVIDIA](https://www.nvidia.com/en-us/networking/infiniband-switching/) |
| UFM Cyber-AI | family="UFM platform"; speed=null; connectors=null; port_counts=null; throughput=null; height=null; cooling=null; compatibility=["UFM Telemetry","UFM Enterprise"]; reach=null | — | [NVIDIA](https://www.nvidia.com/en-us/networking/infiniband-switching/) |

## Silicon Photonics

| Model | Collected fields | Accepted pluggables | Source |
|---|---|---|---|
| Q3450-LD | family="Quantum-X InfiniBand Photonics"; speed="800Gb/s XDR"; throughput="115.2 Tb/s"; availability=null; compatibility=["Quantum-X800","200G SerDes","co-packaged optics"] | — | [NVIDIA](https://www.nvidia.com/en-us/networking/products/silicon-photonics/) |
| Spectrum-X Ethernet Photonics Switches | family="Spectrum-X Ethernet Photonics"; speed="200G SerDes CPO architecture"; throughput="up to 409.6 Tb/s"; availability="full production"; compatibility=["Spectrum-X Ethernet","co-packaged optics"] | — | [NVIDIA](https://www.nvidia.com/en-us/networking/products/silicon-photonics/) |

## DPU

| Model | Collected fields | Accepted pluggables | Source |
|---|---|---|---|
| BlueField-4 DPU | speed="800Gb/s"; compatibility=["networking","storage","cybersecurity","secure multi-tenancy"] | QSFP112 | [NVIDIA](https://www.nvidia.com/en-eu/data-center/dgx-rubin-nvl8/) |
| BlueField-4 STX Storage Processor | speed=null; compatibility=["AI-native storage","Vera CPU","in-silicon security"] | — | [NVIDIA](https://www.nvidia.com/en-us/networking/products/data-processing-unit/) |
| BlueField-3 DPU | speed="400Gb/s"; compatibility=["SDN","storage","cybersecurity","HPC","5G"] | QSFP112, QSFP56, QSFP28 | [NVIDIA](https://networking-docs.nvidia.com/bf3dpu/supported-interfaces) |

## SuperNIC

| Model | Collected fields | Accepted pluggables | Source |
|---|---|---|---|
| ConnectX-9 SuperNIC | speed="up to 1.6 Tb/s per GPU"; compatibility=["Spectrum-X Ethernet","AI fabrics"] | OSFP (RHS cage), QSFP112 | [NVIDIA](https://networking-docs.nvidia.com/connectx9hw/specifications) |
| ConnectX-8 SuperNIC | speed="up to 800 Gb/s total network bandwidth"; compatibility=["PCIe Gen6","Spectrum-X Ethernet","AI compute fabrics"] | OSFP (RHS cage), QSFP112 | [NVIDIA](https://networking-docs.nvidia.com/connectx8hw/specifications) |
| BlueField-3 SuperNIC | speed="up to 400 Gb/s"; compatibility=["Spectrum-X Ethernet","secure cloud multi-tenancy","deterministic isolated performance"] | QSFP112, QSFP56, QSFP28 | [NVIDIA](https://docs.nvidia.com/networking/display/nvidia-bluefield-3-networking-platform-user-guide.pdf) |
