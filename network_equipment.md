# NVIDIA Network Equipment

_Snapshot **2026-10-23**, schema **v10**, Europe/Warsaw. Generated from `data/nvidia-interconnects.json`; active products only (no-longer-for-sale LinkX items are excluded)._

`IB` = InfiniBand, `ETH` = Ethernet, `NVL` = NVLink/NVL. OSFP finned/flat-top variants are separate rows. Empty `NVIDIA OPN` means the product page publishes no NVIDIA OPN; `—` means not stated by the source.

## Transceivers

Finned and flat-top OSFP are separate rows.

| Model | Variant | Status | Legacy OPN | NVIDIA OPN | Speed | Form factor | Interfaces | Medium | Reach | Fabric | Description | Link |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MMS4B10-XM | RHS/TRO | active | — | 980-9IAJ0-00XM00 | 1600G | OSFP-flattop | 2x 800Gb/s MPO-12/APC | SM | max 500 m | ETH | MMS4B10-XM TRO 1600Gbps OSFP Twin-Port 2xDR4, 2xMPO (APC) 1310nm SMF Transceiver (up to 500m) | [NVIDIA](https://networking-docs.nvidia.com/mms4b10xmtro1600g) |
| MMS4B10-XM | IHS/TRO | active | — | 980-9IAJ0-00XM01 | 1600G | OSFP-finned | 2x 800Gb/s MPO-12/APC | SM | max 500 m | ETH | MMS4B10-XM TRO 1600Gbps OSFP Twin-Port 2xDR4, 2xMPO (APC) 1310nm SMF Transceiver (up to 500m) | [NVIDIA](https://networking-docs.nvidia.com/mms4b10xmtro1600g) |
| MMS4C10 | RHS/FRO Gen2 (XDR) | active | — | 980-9IAU0-00XM00 | 1600G | OSFP-flattop | 2x 800Gb/s MPO-12/APC | SM | max 500 m | IB | NVIDIA MMS4C1X FRO 1600Gbps, 2xDR4, Twin-port OSFP, 2xMPO (APC), 1310nm Single Mode Transceiver (up to 500m) | [NVIDIA](https://networking-docs.nvidia.com/9iau000xmosfptcvr1600) |
| MMS4C10 | IHS/FRO Gen2 (XDR) | active | — | 980-9IAU0-00XM01 | 1600G | OSFP-finned | 2x 800Gb/s MPO-12/APC | SM | max 500 m | IB | NVIDIA MMS4C1X FRO 1600Gbps, 2xDR4, Twin-port OSFP, 2xMPO (APC), 1310nm Single Mode Transceiver (up to 500m) | [NVIDIA](https://networking-docs.nvidia.com/9iau000xmosfptcvr1600) |
| MMS4C11 | RHS/FRO Gen2 (Ethernet) | active | — | 980-9IAU1-00XM00 | 1600G | OSFP-flattop | 2x 800Gb/s MPO-12/APC | SM | max 500 m | ETH | NVIDIA MMS4C1X FRO 1600Gbps, 2xDR4, Twin-port OSFP, 2xMPO (APC), 1310nm Single Mode Transceiver (up to 500m) | [NVIDIA](https://networking-docs.nvidia.com/9iau000xmosfptcvr1600) |
| MMS4C11 | IHS/FRO Gen2 (Ethernet) | active | — | 980-9IAU1-00XM01 | 1600G | OSFP-finned | 2x 800Gb/s MPO-12/APC | SM | max 500 m | ETH | NVIDIA MMS4C1X FRO 1600Gbps, 2xDR4, Twin-port OSFP, 2xMPO (APC), 1310nm Single Mode Transceiver (up to 500m) | [NVIDIA](https://networking-docs.nvidia.com/9iau000xmosfptcvr1600) |
| MMS4A00 | IHS | active | MMS4A00 | 980-9IAH1-00XM00 | 1600G | OSFP-finned | 2x 800Gb/s MPO-12/APC | SM | max 500 m | IB | NVIDIA MMS4A00 1600Gbps, 2xDR4, Twin-port OSFP, 2xMPO, 1310nm Single Mode Transceiver (up to 500m) | [NVIDIA](https://networking-docs.nvidia.com/9iahx00xmosfptcvr1600) |
| MMS4A00 | RHS | planned | — | 980-9IAH0-00XM00 | 1600G | OSFP-flattop | 2x 800Gb/s MPO-12/APC | SM | max 500 m | IB | NVIDIA MMS4A00 1600Gbps, 2xDR4, Twin-port OSFP, 2xMPO, 1310nm Single Mode Transceiver (up to 500m) | [NVIDIA](https://networking-docs.nvidia.com/9iahx00xmosfptcvr1600) |
| MMS4A50 | RHS | active | — | 980-9IAS1-00XM00 | 1600G | OSFP-flattop | 2x 800Gb/s Dual LC Duplex | SM | max 2000 m | IB/ETH | NVIDIA MMS4A50 1600Gbps, OSFP, 2xLC-LC, 1310nm SMF, 2xFR4 Twin-port Transceiver (up to 2km) | [NVIDIA](https://networking-docs.nvidia.com/mms4a501600gosfp) |
| MMS4A50 | IHS | active | — | 980-9IAS0-00XM00 | 1600G | OSFP-finned | 2x 800Gb/s Dual LC Duplex | SM | max 2000 m | IB/ETH | NVIDIA MMS4A50 1600Gbps, OSFP, 2xLC-LC, 1310nm SMF, 2xFR4 Twin-port Transceiver (up to 2km) | [NVIDIA](https://networking-docs.nvidia.com/mms4a501600gosfp) |
| MMA1Z00-NS400 | — | active | MMA1Z00-NS400 | 980-9I693-00NS00 | 400G | QSFP112 | 1x 400Gb/s MPO-12/APC | MM | OM3 30 m, OM4 50 m, max 50 m | IB/ETH | MMA1Z00-NS400 400Gb/s, Single-port, QSFP112 Multimode SR4 Transceivers Product Specifications | [NVIDIA](https://networking-docs.nvidia.com/mms1z00ns400sr4) |
| MMS1V00-WM | — | active | MMS1V00-WM | 980-9I16Y-00W000 | 400G | QSFP-DD | 1x 400Gb/s MPO-12/APC | SM | max 500 m | ETH | MMS1V00-WM 400GbE QSFP-DD DR4 Transceiver Product Specifications | [NVIDIA](https://networking-docs.nvidia.com/mms1v00wm10) |
| MMS4X00-NS400 | — | active | MMS4X00-NS400 | 980-9I31N-00NM00 | 400G | OSFP-flattop | 1x 400Gb/s MPO-12/APC | SM | max 100 m | IB/ETH | MMS4X00-NS400 400Gb/s Single-port OSFP Single Mode DR4 Transceivers Product Specifications | [NVIDIA](https://networking-docs.nvidia.com/mms4x00ns400) |
| MMA4Z00-NS400 | — | active | MMA4Z00-NS400 | 980-9I51S-00NS00 | 400G | OSFP-flattop | 1x 400Gb/s MPO-12/APC | MM | OM3 30 m, OM4 50 m, max 50 m | IB/ETH | MMA4Z00-NS400 400Gb/s Single-port OSFP 400Gb/s Multimode SR4 50m | [NVIDIA](https://networking-docs.nvidia.com/mma4z00ns400) |
| MMA4Z00-NS400-T | — | active | MMA4Z00-NS400-T | 980-9I51S-F4NS00 | 400G | OSFP-flattop | 1x 400Gb/s MPO-12/APC | MM | max 50 m | ETH | MMA4Z00-NS400-T 400Gb/s Single-port OSFP 400Gb/s Multimode 50m | [NVIDIA](https://networking-docs.nvidia.com/mma4z00ns400t) |
| MMA1Z00-NS400-T | — | active | MMA1Z00-NS400-T | 980-9I693-F4NS00 | 400G | QSFP112 | 1x 400Gb/s MPO-12/APC | MM | max 50 m | ETH | NVIDIA MMA1Z00-NS400-T 400Gb/s, Single-port, QSFP112 Multimode Transceivers Product Specifications | [NVIDIA](https://networking-docs.nvidia.com/mma1z00ns400t) |
| MMS1X00-NS400 | — | active | MMS1X00-NS400 | 980-9I068-00NM00 | 400G | QSFP112 | 1x 400Gb/s MPO-12/APC | SM | max 500 m, ordering_descriptionax 100 m | IB/ETH | NVIDIA MMS1X00-NS400 400Gb/s Single-port QSFP112 Single Mode Transceivers Product Specifications | [NVIDIA](https://networking-docs.nvidia.com/mms1x00ns400) |
| MMS1V70-CM | — | active | MMS1V70-CM | 980-9I042-00C000 | 100G | QSFP28 | 1x 100Gb/s LC duplex | SM | max 500 m | ETH | MMS1V70-CM 100GbE QSFP28 DR1 | [NVIDIA](https://networking-docs.nvidia.com/mms1v70cm10) |
| MMA1B00-C100D | — | active | MMA1B00-C100D | 980-9I149-00CS00 | 100G | QSFP28 | 1x 100Gb/s MPO-12/UPC | MM | OM3 70 m, OM4 100 m, max 100 m | ETH | MMA1B00-C100D 100GbE QSFP28 MMF SR4 | [NVIDIA](https://networking-docs.nvidia.com/mma1b00c100dspec) |
| MMS4C10-XM800 | RHS/FRO Gen2 | prototype | — | 980-9IAY0-00XM00 | 800G | OSFP-flattop | 1x 800Gb/s MPO-12/APC | SM | max 500 m | IB/ETH | NVIDIA MMS4C10-XM800 800Gbps, 2xDR4, Twin-port OSFP, 2xMPO (APC), 1310nm Single Mode Transceiver | [NVIDIA](https://networking-docs.nvidia.com/mms4c1x800) |
| MMS4X00-NM-T | — | active | MMS4X00-NM-T | 980-9I30G-F4NM00 | 800G | OSFP-finned | 2x 400Gb/s MPO-12/APC | SM | max 500 m | ETH | MMS4X00-NM-T 800Gbps Twin-port OSFP 2x400Gb/s Single Mode 500m | [NVIDIA](https://networking-docs.nvidia.com/mms4x00nmt800g) |
| MMS4X00-NM | finned | active | MMS4X00-NM | 980-9I30G-00NM00 | 800G | OSFP-finned | 2x 400Gb/s MPO-12/APC | SM | max 500 m | IB/ETH | MMS4X00-NM 800Gbps Twin-port OSFP 2x400Gb/s InfiniBand and Ethernet Single Mode 2xDR4 500m | [NVIDIA](https://networking-docs.nvidia.com/mms4x00nm800g500m) |
| MMS4X00-NM-FLT | flat-top | active | MMS4X00-NM-FLT | 980-9I301-00NM00 | 800G | OSFP-flattop | 2x 400Gb/s MPO-12/APC | SM | max 500 m | IB/ETH | MMS4X00-NM 800Gbps Twin-port OSFP 2x400Gb/s InfiniBand and Ethernet Single Mode 2xDR4 500m | [NVIDIA](https://networking-docs.nvidia.com/mms4x00nm800g500m) |
| MMS4X50-NM | — | active | — | 980-9I30L-00N000 | 800G | OSFP-finned | 2x 400Gb/s Duplex LC | SM | max 2000 m | IB/ETH | MMS4X50-NM 800Gbps Twin-port OSFP 2xFR4, 2x400Gb/s Single Mode, 2km | [NVIDIA](https://networking-docs.nvidia.com/mms4x50nm800g2kmpub) |
| MMS4X00-NS | finned | active | MMS4X00-NS | 980-9I30H-00NM00 | 800G | OSFP-finned | 2x 400Gb/s MPO-12/APC | SM | max 100 m | IB/ETH | MMS4X00-NS 800Gbps Twin-port OSFP 2x400Gb/s Single Mode 2xDR4 100m | [NVIDIA](https://networking-docs.nvidia.com/800gmms4x00ns) |
| MMS4X00-NS-FLT | flat-top | active | MMS4X00-NS-FLT | 980-9I30I-00NM00 | 800G | OSFP-flattop | 2x 400Gb/s MPO-12/APC | SM | max 100 m | IB/ETH | MMS4X00-NS 800Gbps Twin-port OSFP 2x400Gb/s Single Mode 2xDR4 100m | [NVIDIA](https://networking-docs.nvidia.com/800gmms4x00ns) |
| MMA4Z00-NS-T | — | active | MMA4Z00-NS-T | 980-9I510-F4NS00 | 800G | OSFP-finned | 2x 400Gb/s MPO-12/APC | MM | OM3 30 m, OM4 50 m, max 50 m | ETH | MMA4Z00-NS-T 800Gb/s Twin-port OSFP, 2x400Gb/s Multimode, 50m | [NVIDIA](https://networking-docs.nvidia.com/800gmma4z00nst) |
| MMS4X00-NS-T | — | active | MMS4X00-NS-T | 980-9I30H-F4NM00 | 800G | OSFP-finned | 2x 400Gb/s MPO-12/APC | SM | max 100 m | ETH | MMS4X00-NS-T 800Gbps Twin-port OSFP 2x400Gb/s Single Mode 100m | [NVIDIA](https://networking-docs.nvidia.com/800gmms4x00nst) |
| MMS4A20 | RHS | active | — | 980-9IAT0-00XM00 | 800G | OSFP-flattop | 1x 800Gb/s MPO-12/APC | SM | max 500 m | IB | NVIDIA MMS4A20 800Gbps, DR4 Single-port OSFP, MPO, 1310nm Single Mode, RHS (500m) Transceiver | [NVIDIA](https://networking-docs.nvidia.com/9iat0mosfp800sprhs) |
| MMS4X00-NM16 | — | active | MMS4X00-NM16 | 980-9I30J-F4NM00 | 800G | OSFP-finned | 1x 800Gb/s MPO-16/APC | SM | max 500 m | ETH | MMS4X00-NM16 NVIDIA Ethernet 800Gbps OSFP Twin-port Finned Transceiver OSFP 1xMPO16 1310nm SMF up to 500m | [NVIDIA](https://networking-docs.nvidia.com/mms4x00nm16) |
| MMS4X00-NM-HGX | HGX Rubin NVL8 | active | MMS4X00-NM-HGX | 980-9I302-00NM00 | 800G | OSFP-flattop | 2x 400Gb/s MPO-12/APC | SM | max 500 m | IB/ETH/NVL | MMS4X00-NM-HGX 800Gbps Twin-port OSFP 2x400Gb/s InfiniBand and Ethernet Single Mode 2xDR4 500m | [NVIDIA](https://networking-docs.nvidia.com/mms4x00nmhgx500) |
| MMS4X90-NR | — | active | — | — | 800G | OSFP-finned | 2x 400Gb/s Duplex LC | SM | max 10000 m | IB/ETH | MMS4X90-NR 800Gbps, 2xLR4, OSFP, 2xLC-LC, 1310nm SMF, Finned Twin-port Transceiver (up to 10km) | [NVIDIA](https://networking-docs.nvidia.com/mms4x90nr800g) |
| MMS1W50-HM | — | active | — | MMS1W50-HM | 200G | QSFP56 | 1x 200Gb/s Duplex LC/UPC | SM | max 2000 m | IB | MMS1W50-HM 200Gb/s QSFP56 FR4 | [NVIDIA](https://networking-docs.nvidia.com/mms1w50hmspec) |
| MMA2P00-AS | — | active | — | MMA2P00-AS | 25G | SFP28 | 1x 25Gb/s Duplex LC/UPC | MM | OM3 70 m, OM4 100 m, max 100 m | ETH | MMA2P00-AS 25GbE SFP28 MMF Transceiver Product Specifications | [NVIDIA](https://networking-docs.nvidia.com/mma2p00asspec) |

## AOC

| Model | Variant | Status | Legacy OPN | NVIDIA OPN | Speed | Form factor | Interfaces | Medium | Reach | Fabric | Description | Link |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MFA7U10-H00x | finned OSFP head | active | MFA7U10-H003 / MFA7U10-H005 / MFA7U10-H010 / MFA7U10-H015 / MFA7U10-H020 / MFA7U10-H030 | 980-9I41X-00H003, 980-9I11Z-00H005, 980-9I111-00H010, 980-9I113-00H015, 980-9I115-00H020, 980-9I117-00H030 | 400G | OSFP-finned -> 2xQSFP56 | 2x 2x200Gb/s OSFP to 2xQSFP56 | MM | max 30 m | IB/ETH | MFA7U10-H00x 400Gb/s OSFP to 2x200Gb/s QSFP56 HDR Active Optical Splitter Cable | [NVIDIA](https://networking-docs.nvidia.com/mfa7u10h00x10) |
| MFA7U10-H00x-FLT | flat-top OSFP head | active | MFA7U10-H003-FLT / MFA7U10-H005-FLT / MFA7U10-H010-FLT / MFA7U10-H015-FLT / MFA7U10-H020-FLT / MFA7U10-H030-FLT | 980-9I41Y-00H003, 980-9I110-00H005, 980-9I112-00H010, 980-9I114-00H015, 980-9I116-00H020, 980-9I118-00H030 | 400G | OSFP-flattop -> 2xQSFP56 | 2x 2x200Gb/s OSFP to 2xQSFP56 | MM | max 30 m | IB/ETH | MFA7U10-H00x 400Gb/s OSFP to 2x200Gb/s QSFP56 HDR Active Optical Splitter Cable | [NVIDIA](https://networking-docs.nvidia.com/mfa7u10h00x10) |
| MFS1S00-HxxxV | — | active | MFS1S00-H003V / MFS1S00-H005V / MFS1S00-H010V / MFS1S00-H015V / MFS1S00-H020V / MFS1S00-H030V / MFS1S00-H050V / MFS1S00-H100V | 980-9I457-00H003, 980-9I45D-00H005, 980-9I45J-00H010, 980-9I45O-00H015, 980-9I45T-00H020, 980-9I440-00H030, 980-9I447-00H050, 980-9I44H-00H100 | 200G | QSFP56 | 1x 200Gb/s QSFP56 to QSFP56 | MM | max 100 m | IB/ETH | MFS1S00-HxxxV 200Gb/s QSFP56 MMF AOC Product Specifications | [NVIDIA](https://networking-docs.nvidia.com/mfs1s00hxxxv10) |

## Copper / DAC / ACC

| Model | Variant | Status | Legacy OPN | NVIDIA OPN | Speed | Form factor | Interfaces | Medium | Reach | Fabric | Description | Link |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MCA4K00 | RHS-to-RHS | active | MCA4K00 | 980-9IAM1-00X001, 980-9IAM2-00X001, 980-9IAM4-00X001 | 1600G | OSFP-flattop -> OSFP-flattop | 1x 1600Gb/s OSFP to OSFP | Copper | max 1.1 m | IB/ETH/NVL | MCA4K00 1600Gbps to 1600Gbps OSFP Active Copper Cable Product Specifications | [NVIDIA](https://networking-docs.nvidia.com/mca4k00hw) |
| MCA4K50 | IHS-to-IHS | active | MCA4K50 | 980-9IAM5-00X001, 980-9IAM5-00X01A, 980-9IAM3-00X002, 980-9IAM3-00X02A, 980-9IAM3-00X003 | 1600G | OSFP-finned -> OSFP-finned | 1x 1600Gb/s OSFP to OSFP | Copper | max 3 m | IB | MCA4K50 1600Gbps to 1600Gbps OSFP Active Copper Cable | [NVIDIA](https://networking-docs.nvidia.com/mca4k50osfp1600) |
| MCA7K10 | IHS-to-2xRHS | active | MCA7K10 | 980-9IAO5-00X001, 980-9IAO5-00X01A, 980-9IAO5-00X002 | 1600G | OSFP-finned -> 2xOSFP-flattop | 2x 2x800Gb/s OSFP to 2xOSFP | Copper | max 2 m | IB/ETH | MCA7K10 1600Gb/s to 2x800Gb/s, OSFP to 2xOSFP, IHS to RHS Active Copper Splitter Cable | [NVIDIA](https://networking-docs.nvidia.com/9809iao500xxxxrhs2x800) |
| MCA4J80-Nxxx | finned | active | MCA4J80-N003 / MCA4J80-N004 / MCA4J80-N005 | 980-9I60Z-00N003, 980-9I601-00N004, 980-9I602-00N005 | 800G | OSFP-finned -> OSFP-finned | 2x 2x400Gb/s OSFP to OSFP | Copper | max 5 m | IB | MCA4J80-Nxxx 800Gb/s Twin-port OSFP to 2x400Gb/s OSFP InfiniBand ACC Product Specifications | [NVIDIA](https://networking-docs.nvidia.com/mca4j80nxxx800pub) |
| MCA4J80-Nxxx-FLT | flat-top | active | MCA4J80-N003-FLT | 980-9I600-00N003 | 800G | OSFP-flattop -> OSFP-flattop | 2x 2x400Gb/s OSFP to OSFP | Copper | max 3 m | IB | MCA4J80-Nxxx 800Gbps Twin-port 2x400Gbps OSFP to 2x400Gbps OSFP InfiniBand LACC | [NVIDIA](https://networking-docs.nvidia.com/mca4j80nxxx800pub) |
| MCA4J80-Nxxx-FTF | flat-to-finned | active | MCA4J80-N003-FTF | 980-9I601-00N003 | 800G | OSFP-flattop -> OSFP-finned | 2x 2x400Gb/s OSFP to OSFP | Copper | max 3 m | IB | MCA4J80-Nxxx 800Gbps Twin-port 2x400Gbps OSFP to 2x400Gbps OSFP InfiniBand LACC | [NVIDIA](https://networking-docs.nvidia.com/mca4j80nxxx800pub) |
| MCP4Y10-Nxxx | finned | active | MCP4Y10-N00A / MCP4Y10-N001 / MCP4Y10-N01A / MCP4Y10-N002 | 980-9IA0K-00N00A, 980-9IA0F-00N001, 980-9IA0Q-00N01A, 980-9IA0I-00N002 | 800G | OSFP-finned -> OSFP-finned | 2x 2x400Gb/s OSFP to OSFP | Copper | max 2 m | IB/ETH | MCP4Y10-Nxxx Twin-port 2x400Gb/s OSFP to 2x400Gb/s OSFP Passive DAC Product Specifications | [NVIDIA](https://networking-docs.nvidia.com/mcp4y10nxxx2x400pub) |
| MCP4Y10-Nxxx-FLT | flat-top | active | MCP4Y10-N00A-FLT / MCP4Y10-N001-FLT / MCP4Y10-N002-FLT | 980-9IA0L-00N00A, 980-9IA0G-00N001, 980-9IA0J-00N002 | 800G | OSFP-flattop -> OSFP-flattop | 2x 2x400Gb/s OSFP to OSFP | Copper | max 2 m | IB/ETH | MCP4Y10-Nxxx Twin-port 2x400Gb/s OSFP to 2x400Gb/s OSFP Passive DAC Product Specifications | [NVIDIA](https://networking-docs.nvidia.com/mcp4y10nxxx2x400pub) |
| MCP7Y00-Nxxx | finned head | active | — | MCP7Y00-N001, MCP7Y00-N01A, MCP7Y00-N002, MCP7Y00-N02A, MCP7Y00-N003 | 800G | OSFP-finned -> 2xOSFP-flattop | 2x 2x400Gb/s OSFP to 2xOSFP | Copper | max 3 m | IB/ETH | MCP7Y00-Nxxx 800Gb/s Twin-port 2x400G OSFP to 2x400G OSFP Passive DAC Splitter Product Specifications | [NVIDIA](https://networking-docs.nvidia.com/mcp7y00nxxx800pub) |
| MCP7Y00-Nxxx-FLT | flat-top head | active | — | MCP7Y00-N001-FLT1, MCP7Y00-N01A-FLT, MCP7Y00-N002-FLT | 800G | OSFP-flattop -> 2xOSFP-flattop | 2x 2x400Gb/s OSFP to 2xOSFP | Copper | max 2 m | IB/ETH | MCP7Y00-Nxxx 800Gbps Twin-port 2x400G OSFP to 2x400G OSFP Passive DAC Splitter | [NVIDIA](https://networking-docs.nvidia.com/mcp7y00nxxx800pub) |
| MCP1600-E0xxEyy | — | active | — | MCP1600-E00AE30, MCP1600-E001E30, MCP1600-E01AE30, MCP1600-E002E30, MCP1600-E02AE26, MCP1600-E003E26, MCP1600-E004E26, MCP1600-E005E26 | 100G | QSFP28 | 1x 100Gb/s QSFP28 to QSFP28 | Copper | max 5 m | IB | MCP1600-E0xxEyy 100Gb/s QSFP28 DAC Cable Product Specifications | [NVIDIA](https://networking-docs.nvidia.com/mcp1600e0xxxeyyspec) |

## Other active LinkX products

Accessories (QSA adapters, fiber cables) and family entries without a detailed row.

| Category | Model | Status | Legacy OPN | NVIDIA OPN | Speed | Description | Link |
|---|---|---|---|---|---|---|---|
| Transceiver | MMS4C1X | active | — | 980-9IAU0-00XM00, 980-9IAU0-00XM01, 980-9IAU1-00XM00, 980-9IAU1-00XM01 | 1600G | NVIDIA MMS4C1X FRO 1600Gbps, 2xDR4, Twin-port OSFP, 2xMPO (APC), 1310nm Single Mode Transceiver (up to 500m) | [NVIDIA](https://networking-docs.nvidia.com/9iau000xmosfptcvr1600) |
| Adapter | MAM1Q00A-QSA | active | — | — | Accessories | MAM1Q00A-QSA NVIDIA DynamiX QSA™, QSFP+ to SFP+ Adapter Product Specifications | [NVIDIA](https://networking-docs.nvidia.com/mam1q00aqsadnmx) |
| Adapter | MAM1Q00A-QSA28 | active | — | — | Accessories | MAM1Q00A-QSA28 NVIDIA DynamiX QSA™ QSA28, QSFP28 to SFP28 Adapter Product Specifications | [NVIDIA](https://networking-docs.nvidia.com/mam1q00aqsa28dnmx) |
| Fiber | MFP7E10-Nxxx | active | — | — | Accessories | MFP7E10-Nxxx Optical Multimode Fiber Cable Product Specifications | [NVIDIA](https://networking-docs.nvidia.com/mfp7e10nxxx) |
| Fiber | MFP7E20-Nxxx | active | — | — | Accessories | MFP7E20-Nxxx Optical Multimode Splitter Fiber Cable Product Specifications | [NVIDIA](https://networking-docs.nvidia.com/mfp7e20nxxx) |
| Fiber | MFP7E30-Nxxx | active | — | — | Accessories | MFP7E30-Nxxx MPO-to-MPO Single-mode Fiber Cable Product Specifications | [NVIDIA](https://networking-docs.nvidia.com/mfp7e30nxxxpub) |
| Fiber | MFP7E40-Nxxx | active | MFP7E40-N003 / MFP7E40-N005 / MFP7E40-N007 / MFP7E40-N010 / MFP7E40-N015 / MFP7E40-N020 / MFP7E40-N030 / MFP7E40-N050 | 980-9I58K-00N003, 980-9I58L-00N005, 980-9I58M-00N007, 980-9I58N-00N010, 980-9I56O-00N015, 980-9I56P-00N020, 980-9I56Q-00N030, 980-9I56R-000050 | Accessories | MFP7E40-Nxxx Single mode 1:2 Fiber Splitter Cable Product Specifications | [NVIDIA](https://networking-docs.nvidia.com/mfp7e40nxxxpub) |

## Ethernet switching

| Model | Family | Status | Legacy OPN | NVIDIA OPN | Speed | Cages / interfaces | Description | Link |
|---|---|---|---|---|---|---|---|---|
| SN6810-LD | Spectrum-6 SN6000 | documented | — | — | 800GbE | 128x MMC-12 800GbE fixed | Spectrum-6 SN6000 2U 800GbE Ethernet switch: 128x MMC-12 (co-packaged optics) | [NVIDIA](https://networking-docs.nvidia.com/sn6000hw) |
| SN6800-LD | Spectrum-6 SN6000 | documented | — | — | 200GbE | 512x MMC-12 200GbE fixed | Spectrum-6 SN6000 5U 200GbE Ethernet switch: 512x MMC-12 (co-packaged optics) | [NVIDIA](https://networking-docs.nvidia.com/sn6000hw) |
| SN6600-LD | Spectrum-6 SN6000 | documented | — | — | 800GbE | 64x OSFP 2x800 Gb/s | Spectrum-6 SN6000 2U 800GbE Ethernet switch: 64x OSFP 2x800 Gb/s | [NVIDIA](https://networking-docs.nvidia.com/sn6000hw) |
| SN6600 | Spectrum-6 SN6000 | documented | — | — | 800GbE | 64x OSFP 2x800 Gb/s | Spectrum-6 SN6000 3U 800GbE Ethernet switch: 64x OSFP 2x800 Gb/s | [NVIDIA](https://networking-docs.nvidia.com/sn6000hw) |
| SN6200-LD | Spectrum-6 SN6000 | documented | — | — | 200GbE | 32x OSFP 2x800GbE front; 256x backplane 200G | Spectrum-6 SN6000 1U 200GbE Ethernet switch: 32x OSFP 2x800GbE front + 256x200G backplane | [NVIDIA](https://networking-docs.nvidia.com/sn6000hw) |
| SN5610 | Spectrum-4 SN5000 | documented | — | 920-9N42F-00RI-3C1 | 800GbE | 64x OSFP 800GbE; 2x SFP28 25GbE | Spectrum-4 SN5000 2U 800GbE Ethernet switch: 64x OSFP 800GbE + 2x SFP28 25GbE | [NVIDIA](https://networking-docs.nvidia.com/sn5000hw) |
| SN5600 | Spectrum-4 SN5000 | end_of_life | — | 920-9N42F-00RI-7C0 | 800GbE | 64x OSFP 800GbE; 1x SFP28 25GbE | Spectrum-4 SN5000 2U 800GbE Ethernet switch: 64x OSFP 800GbE + 1x SFP28 25GbE | [NVIDIA](https://networking-docs.nvidia.com/sn5000hw) |
| SN5600D | Spectrum-4 SN5000 | documented | — | 920-9N42F-00RI-KC0 | 800GbE | 64x OSFP 800GbE; 1x SFP28 25GbE | Spectrum-4 SN5000 2U 800GbE Ethernet switch: 64x OSFP 800GbE + 1x SFP28 25GbE | [NVIDIA](https://networking-docs.nvidia.com/sn5000hw) |
| SN5400 | Spectrum-4 SN5000 | documented | — | 920-9N42C-00RB-7C0, 920-9N42C-00FB-7C0 | 400GbE | 64x QSFP-DD 400GbE; 2x SFP28 25GbE | Spectrum-4 SN5000 2U 400GbE Ethernet switch: 64x QSFP-DD 400GbE + 2x SFP28 25GbE | [NVIDIA](https://networking-docs.nvidia.com/sn5000hw) |
| SN4600C | Spectrum-3 SN4000 | documented | MSN4600-CS2FC / MSN4600-CS2RC | 920-9N302-00F7-0C2, 920-9N302-00R7-0C0 | 100GbE | 64x QSFP28 100GbE | Spectrum-3 SN4000 2U 100GbE Ethernet switch: 64x QSFP28 100GbE | [NVIDIA](https://networking-docs.nvidia.com/sn4000hw) |
| SN4700 | Spectrum-3 SN4000 | documented | MSN4700-WS2FC / MSN4700-WS2RC | 920-9N301-00FB-0C0, 920-9N301-00RB-0C0 | 400GbE | 32x QSFP-DD 400GbE | Spectrum-3 SN4000 1U 400GbE Ethernet switch: 32x QSFP-DD 400GbE | [NVIDIA](https://networking-docs.nvidia.com/sn4000hw) |
| SN3420 | Spectrum-2 SN3000 | documented | MSN3420-CB2FC / MSN3420-CB2RC | 920-9N213-00F7-0C0, 920-9N213-00R7-0C0 | 100GbE | 12x QSFP28 100GbE; 48x SFP28 25GbE | Spectrum-2 SN3000 1U 100GbE Ethernet switch: 12x QSFP28 100GbE + 48x SFP28 25GbE | [NVIDIA](https://networking-docs.nvidia.com/sn3000hw) |
| SN2201 | Spectrum SN2000 | documented | MSN2201-CB2FC / MSN2201-CB2RC | 920-9N110-00F1-0C0, 920-9N110-00R1-0C0 | 100GbE | 48x RJ45 fixed; 4x QSFP28 100GbE | Spectrum SN2000 1U 100GbE Ethernet switch: 48x RJ45 + 4x QSFP28 100GbE | [NVIDIA](https://networking-docs.nvidia.com/sn2201hw) |
| SN4600 | Spectrum-3 SN4000 | documented | MSN4600-CS2FC / MSN4600-CS2RC | 920-9N302-00F7-0C2, 920-9N302-00R7-0C0 | 100GbE | 64x QSFP28 100GbE | Spectrum-3 SN4000 2U 100GbE Ethernet switch: 64x QSFP28 100GbE | [NVIDIA](https://networking-docs.nvidia.com/sn4000hw) |
| SN4700D | Spectrum-3 SN4000 | documented | MSN4700-WSARC | 920-9N301-00RB-NC0 | 400GbE | 32x QSFP-DD 400GbE | Spectrum-3 SN4000 1U 400GbE Ethernet switch: 32x QSFP-DD 400GbE | [NVIDIA](https://networking-docs.nvidia.com/sn4000hw) |

## InfiniBand switching / appliances / gateways

| Model | Family | Status | Legacy OPN | NVIDIA OPN | Speed | Cages / interfaces | Description | Link |
|---|---|---|---|---|---|---|---|---|
| Q3200-RA | Quantum-X800 | documented | — | 920-9B34F-00RX-FS0 | 800Gb/s XDR | 36x OSFP 800Gb/s XDR (twin-port, 72 ports) | Quantum-X800 800Gb/s XDR: 2x18 OSFP | [NVIDIA](https://networking-docs.nvidia.com/switches#nvidiatab-hw-documentation) |
| Q3400-RA | Quantum-X800 | documented | — | 920-9B36F-00RX-8S0 | 800Gb/s XDR | 72x OSFP 800Gb/s XDR (twin-port, 144 ports) | Quantum-X800 800Gb/s XDR: 72x OSFP | [NVIDIA](https://networking-docs.nvidia.com/switches#nvidiatab-hw-documentation) |
| Q3401-RD | Quantum-X800 | documented | — | 920-9B36P-00RX-8S0 | 800Gb/s XDR | 72x OSFP 800Gb/s XDR (twin-port, 144 ports) | Quantum-X800 800Gb/s XDR: 72x OSFP | [NVIDIA](https://networking-docs.nvidia.com/switches#nvidiatab-hw-documentation) |
| Q3450-LD | Quantum-X Photonics / Quantum-X800 | documented | — | 920-9B36M-00MX-8ES | 800Gb/s XDR | 144x MPO-12 CPO 800Gb/s XDR fixed | Quantum-X Photonics / Quantum-X800 800Gb/s XDR: 144x MPO12 CPO | [NVIDIA](https://networking-docs.nvidia.com/switches#nvidiatab-hw-documentation) |
| QM9700 family | Quantum-2 | documented | — | — | 400Gb/s NDR | OSFP 400Gb/s NDR | Quantum-2 400Gb/s NDR: OSFP | [NVIDIA](https://networking-docs.nvidia.com/switches#nvidiatab-hw-documentation) |
| Skyway | InfiniBand-to-Ethernet Gateway | documented | — | — | 100/200 Gb/s per port | 8x QSFP56 100/200 Gb/s [InfiniBand]; 8x QSFP56 100/200 Gb/s [Ethernet] | InfiniBand-to-Ethernet Gateway 100/200 Gb/s per port: 8 ports per InfiniBand and Ethernet side | [NVIDIA](https://networking-docs.nvidia.com/skyway) |
| MetroX-3 XC | Long-haul InfiniBand | end_of_life | MTQ8400-HS2R / MTQ8400-HS2RC | 920-9B020-00FA-0DZ, 920-9B020-00FA-6DZ | InfiniBand extension | OSFP; 2x QSFP112 100Gb/s long-haul (DWDM-ready) | Long-haul InfiniBand InfiniBand extension | [NVIDIA](https://networking-docs.nvidia.com/metrox3xc) |
| UFM Telemetry | UFM platform | documented | — | — | — | — | UFM platform | [NVIDIA](https://networking-docs.nvidia.com/switches#nvidiatab-hw-documentation) |
| UFM Enterprise | UFM platform | documented | — | — | — | — | UFM platform | [NVIDIA](https://networking-docs.nvidia.com/switches#nvidiatab-hw-documentation) |
| UFM Cyber-AI | UFM platform | documented | — | — | — | — | UFM platform | [NVIDIA](https://networking-docs.nvidia.com/switches#nvidiatab-hw-documentation) |
| Skyway-3 | InfiniBand-to-Ethernet Gateway | active | — | 920-9B02D-00RG-CF0, MGA400-XS2 | XDR/Ethernet gateway | 8x QSFP112 [InfiniBand]; 8x QSFP112 [Ethernet] | InfiniBand-to-Ethernet Gateway XDR/Ethernet gateway: 8x IB + 8x Ethernet QSFP112 | [NVIDIA](https://networking-docs.nvidia.com/skyway3hw) |

## Silicon Photonics

| Model | Family | Status | Legacy OPN | NVIDIA OPN | Speed | Cages / interfaces | Description | Link |
|---|---|---|---|---|---|---|---|---|
| Q3450-LD | Quantum-X InfiniBand Photonics | documented | — | 920-9B36M-00MX-8ES | 800Gb/s XDR | 144x MPO-12 CPO 800Gb/s XDR fixed | Quantum-X InfiniBand Photonics: co-packaged optics, 800Gb/s XDR, 115.2 Tb/s | [NVIDIA](https://networking-docs.nvidia.com/xdrswitcheshw) |
| Spectrum-X Ethernet Photonics Switches | Spectrum-X Ethernet Photonics | active | — | — | 200G SerDes CPO architecture | — | Spectrum-X Ethernet Photonics: co-packaged optics, 200G SerDes CPO architecture, up to 409.6 Tb/s | [NVIDIA](https://www.nvidia.com/en-us/networking/products/silicon-photonics/) |

## DPU

| Model | Family | Status | Legacy OPN | NVIDIA OPN | Speed | Cages / interfaces | Description | Link |
|---|---|---|---|---|---|---|---|---|
| BlueField-4 DPU | — | documented | — | — | 800Gb/s | QSFP112 800Gb/s | BlueField-4 DPU, 800Gb/s: networking, storage, cybersecurity, secure multi-tenancy | [NVIDIA](https://www.nvidia.com/en-eu/data-center/dgx-rubin-nvl8/) |
| BlueField-4 STX Storage Processor | — | documented | — | — | — | — | BlueField-4 STX Storage Processor: AI-native storage, Vera CPU, in-silicon security | [NVIDIA](https://www.nvidia.com/en-us/networking/products/data-processing-unit/) |
| BlueField-3 DPU | — | documented | — | 900-9D3B6-00CC-AA0, 900-9D3B6-00CC-EA0, 900-9D3B6-00CN-AB0, 900-9D3B6-00CN-PA0, 900-9D3B6-00CV-AA0, 900-9D3B6-00SC-AA0, 900-9D3B6-00SC-EA0, 900-9D3B6-00SN-AB0, 900-9D3B6-00SV-AA0, 900-9D3L6-00CN-AA0 | 400Gb/s | QSFP112 400Gb/s; QSFP56 400Gb/s; QSFP28 400Gb/s | BlueField-3 DPU, 400Gb/s: SDN, storage, cybersecurity, HPC, 5G | [NVIDIA](https://networking-docs.nvidia.com/bf3dpu) |

## SuperNIC

| Model | Family | Status | Legacy OPN | NVIDIA OPN | Speed | Cages / interfaces | Description | Link |
|---|---|---|---|---|---|---|---|---|
| ConnectX-9 SuperNIC | — | documented | — | 900-9X91E-00EB-ST0, 900-9X91Q-00CN-ST0, 900-9X91E-00EB-DT0, 900-9X91E-00QB-ST0, 900-9X91Q-00RN-ST0, 900-9X91Q-00RV-ST0, 900-9X91Q-00RC-ST0 | up to 1.6 Tb/s per GPU | 1x OSFP 800GbE / XDR 800Gb/s (C9180); 2x QSFP112 2x400GbE / 400Gb/s IB (C9240); 2x QSFP112 400GbE (C9220); 2x QSFP112 200GbE (C9210) | ConnectX-9 SuperNIC, up to 1.6 Tb/s per GPU: Spectrum-X Ethernet, AI fabrics | [NVIDIA](https://networking-docs.nvidia.com/connectx9hw) |
| ConnectX-8 SuperNIC | — | documented | — | 900-9X81E-00EX-ST0, 900-9X81Q-00CN-ST0, 900-9X81Q-00CV-ST0, 900-9X81E-00EX-DT0, 900-9X81E-00EX-SL0 | up to 800 Gb/s total network bandwidth | 1x OSFP XDR 800Gb/s / 2x400GbE (C8180); 2x QSFP112 400GbE / 400Gb/s IB (C8240); 2x QSFP112 up to 400Gb/s aggregate (C8220); 1x OSFP XDR 800Gb/s / 2x400GbE (C8180L Partner Cooled) | ConnectX-8 SuperNIC, up to 800 Gb/s total network bandwidth: PCIe Gen6, Spectrum-X Ethernet, AI compute fabrics | [NVIDIA](https://networking-docs.nvidia.com/connectx8hw) |
| BlueField-3 SuperNIC | — | documented | — | 900-9D3B4-00CC-EA0, 900-9D3B4-00CV-EA0, 900-9D3B4-00EN-EA0, 900-9D3B4-00PN-EA0, 900-9D3B4-00SC-EA0, 900-9D3B4-00SV-EA0, 900-9D3D4-00EN-HA0, 900-9D3D4-00NN-HA0 | up to 400 Gb/s | QSFP112 up to 400 Gb/s; QSFP56 up to 400 Gb/s; QSFP28 up to 400 Gb/s | BlueField-3 SuperNIC, up to 400 Gb/s: Spectrum-X Ethernet, secure cloud multi-tenancy, deterministic isolated performance | [NVIDIA](https://networking-docs.nvidia.com/bf3dpu) |

## Network adapters

| Model | Family | Status | Legacy OPN | NVIDIA OPN | Speed | Interface | Cages / interfaces | Link |
|---|---|---|---|---|---|---|---|---|
| C9180 | ConnectX-9 | MP | — | 900-9X91E-00EB-ST0, 900-9X91E-00EB-DT0, 900-9X91E-00QB-ST0 | 800GbE / XDR 800Gb/s | single-cage OSFP | 1x OSFP 800GbE / XDR 800Gb/s (C9180) | [NVIDIA](https://networking-docs.nvidia.com/connectx9hw) |
| C9240 | ConnectX-9 | MP | — | 900-9X91Q-00CN-ST0, 900-9X91Q-00RN-ST0 | 2x400GbE / 400Gb/s IB | dual QSFP112 | 2x QSFP112 2x400GbE / 400Gb/s IB (C9240) | [NVIDIA](https://networking-docs.nvidia.com/connectx9hw) |
| C8180 | ConnectX-8 | MP | — | 900-9X81E-00EX-ST0, 900-9X81E-00EX-DT0 | XDR 800Gb/s / 2x400GbE | single-cage OSFP | 1x OSFP XDR 800Gb/s / 2x400GbE (C8180) | [NVIDIA](https://networking-docs.nvidia.com/connectx8hw) |
| C8240 | ConnectX-8 | active | — | 900-9X81Q-00CN-ST0 | 400GbE / 400Gb/s IB | dual QSFP112 | 2x QSFP112 400GbE / 400Gb/s IB (C8240) | [NVIDIA](https://networking-docs.nvidia.com/connectx8hw) |
| C8220 | ConnectX-8 | prototype | — | 900-9X81Q-00CV-ST0 | up to 400Gb/s aggregate | dual QSFP112 | 2x QSFP112 up to 400Gb/s aggregate (C8220) | [NVIDIA](https://networking-docs.nvidia.com/connectx8hw) |
| ConnectX-7 | ConnectX-7 | documented | MCX713104AC-ADAT, MCX713104AS-ADAT, MCX713105AS-WEAT, MCX713106AC-CEAT, MCX713106AC-VEAT, MCX713106AS-CEAT, MCX713106AS-VEAT, MCX713114GC-GEAT, MCX713114TC-GEAT, MCX715105AS-WEAT, MCX75310AAC-NEAT, MCX75310AAS-HEAT, MCX75310AAS-NEAT, MCX755106AC-HEAT, MCX755106AS-HEAT, MCX75510AAS-HEAT, MCX75510AAS-NEAT | 900-9X721-003N-DT0, 900-9X721-003N-DT1, 900-9X766-003N-SQ0, 900-9X766-003N-SR0, 900-9X766-003N-ST0, 900-9X7AH-0039-ST1, 900-9X7AH-0039-STZ, 900-9X7AH-004N-CT0, 900-9X7AH-004N-GT0, 900-9X7AH-0076-ST0, 900-9X7AH-0078-DTZ, 900-9X7AH-0078-ST0, 900-9X7AH-0079-DTZ, 900-9X7AH-0086-SQ0, 900-9X7AH-0088-ST0, 900-9X7AO-0003-ST0, 900-9X7AO-00C3-STZ | up to 400Gb/s IB/Ethernet | OSFP / QSFP112 by SKU | OSFP up to 400Gb/s IB/Ethernet (ConnectX-7); QSFP112 up to 400Gb/s IB/Ethernet (ConnectX-7) | [NVIDIA](https://networking-docs.nvidia.com/connectx7hw) |
| ConnectX-6 | ConnectX-6 | documented | — | — | up to 200Gb/s IB/Ethernet | QSFP56 / QSFP28 by SKU | QSFP56 up to 200Gb/s IB/Ethernet (ConnectX-6); QSFP28 up to 200Gb/s IB/Ethernet (ConnectX-6) | [NVIDIA](https://networking-docs.nvidia.com/adapters) |
| ConnectX-6 Dx | ConnectX-6 Dx | documented | — | — | up to 200GbE | QSFP56 / QSFP28 / SFP56 by SKU | QSFP56 up to 200GbE (ConnectX-6 Dx); QSFP28 up to 200GbE (ConnectX-6 Dx); SFP56 up to 200GbE (ConnectX-6 Dx) | [NVIDIA](https://networking-docs.nvidia.com/adapters) |
| ConnectX-6 Lx | ConnectX-6 Lx | documented | — | — | up to 50GbE | SFP56 / SFP28 by SKU | SFP56 up to 50GbE (ConnectX-6 Lx); SFP28 up to 50GbE (ConnectX-6 Lx) | [NVIDIA](https://networking-docs.nvidia.com/adapters) |

## UFM appliances

| Model | Family | Status | Legacy OPN | NVIDIA OPN | Network interface | Description | Link |
|---|---|---|---|---|---|---|---|
| UFM XDR Appliance | UFM Enterprise Gen 3.5 | documented | — | — | XDR InfiniBand | UFM Enterprise Gen 3.5 UFM appliance, XDR InfiniBand | [NVIDIA](https://networking-docs.nvidia.com/software/management-software/ufm-appliances) |
| MUA970D | UFM XDR-DC Gen 3.5 | active | MUA9702H-2SFS-DC | 920-9B020-10RI-0D0 | ConnectX-8 400Gb/s InfiniBand | UFM XDR-DC Gen 3.5 UFM appliance, ConnectX-8 400Gb/s InfiniBand | [NVIDIA](https://networking-docs.nvidia.com/ufmenterprisexdrdchw/) |
| MUA9652H-2SF | UFM Cyber-AI 4.0 | documented | MUA9652H-2SF | 920-9B020-00FH-0D0 | 2x ConnectX-6 HDR 200Gb/s InfiniBand | UFM Cyber-AI 4.0 UFM appliance, 2x ConnectX-6 HDR 200Gb/s InfiniBand | [NVIDIA](https://networking-docs.nvidia.com/ufm40cyberaiapphw) |
| MUA960 | UFM Enterprise Gen 3.0 HDR | documented | MUA9602H-2SR | 920-9B020-00FA-0D3 | HDR InfiniBand | UFM Enterprise Gen 3.0 HDR UFM appliance, HDR InfiniBand | [NVIDIA](https://networking-docs.nvidia.com/ufmenterprisehdrhwum) |
| MUA960B | UFM Enterprise Gen 3.0 NDR | documented | MUA9602H-2SRS | 920-9B020-00RA-0D0 | NDR InfiniBand | UFM Enterprise Gen 3.0 NDR UFM appliance, NDR InfiniBand | [NVIDIA](https://networking-docs.nvidia.com/ufmenterprisendrhwum) |
| MUA950 | UFM-SDN 2.5 | documented | MUA9502H-2SF / MUA9502H-2SF-40K | 920-9B020-00FA-0D5, 920-9B020-09FA-0D0 | InfiniBand | UFM-SDN 2.5 UFM appliance, InfiniBand | [NVIDIA](https://networking-docs.nvidia.com/ufmsdn25apphw) |
| MUA975 | UFM Cyber-AI Gen 4.5 | documented | MUA9752H-2SFS-AC | 920-9B020-00RI-0D5 | 2x ConnectX-8 single-port 400Gb/s InfiniBand | UFM Cyber-AI Gen 4.5 UFM appliance, 2x ConnectX-8 single-port 400Gb/s InfiniBand | [NVIDIA](https://networking-docs.nvidia.com/ufm45cyberaiapphw) |

## Legacy network adapters

These NVIDIA-documented adapters are retained for compatibility/reference and are **not active portfolio products**.

| Model | Family | Status | Speed | Interface | Link |
|---|---|---|---|---|---|
| MCX516A-CCAT | ConnectX-5 | legacy | up to 100GbE per port / EDR InfiniBand | dual QSFP28 | [NVIDIA](https://networking-docs.nvidia.com/connectx5en) |
| MCX455A-ECAT | ConnectX-4 | legacy | 100GbE / EDR InfiniBand class | QSFP28 | [NVIDIA](https://networking-docs.nvidia.com/connectx4) |
| MCX4121A-ACAT | ConnectX-4 Lx | legacy | up to 25GbE per port | dual SFP28 | [NVIDIA](https://networking-docs.nvidia.com/connectx4lx) |
