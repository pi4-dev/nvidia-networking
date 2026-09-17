# NVIDIA Network Equipment

_Snapshot **2026-09-17**, schema **v7**, Europe/Warsaw._

IB=InfiniBand, ETH=Ethernet, NVL=NVLink/NVL. OSFP finned/flat-top variants are separate where NVIDIA publishes separate OPNs.

## Transceivers

|Model|Variant|Status|Speed|Interface|Ports|Medium|Reach|Part numbers|Fabric|Source|
|---|---|---|---|---|---|---|---|---|---|---|
|MMS4B10-XM|RHS/TRO|active|1600G|OSFP-flattop|2x800Gb/s MPO-12/APC|SM|max_m=500|980-9IAJ0-00XM00|ETH|[NVIDIA](https://networking-docs.nvidia.com/mms4b10xmtro1600g)|
|MMS4C10|RHS/FRO Gen2 (XDR)|active|1600G|OSFP-flattop|2x800Gb/s MPO-12/APC|SM|max_m=500|980-9IAU0-00XM00|IB|[NVIDIA](https://networking-docs.nvidia.com/9iau000xmosfptcvr1600)|
|MMS4C10|IHS/FRO Gen2 (XDR)|active|1600G|OSFP-finned|2x800Gb/s MPO-12/APC|SM|max_m=500|980-9IAU0-00XM01|IB|[NVIDIA](https://networking-docs.nvidia.com/9iau000xmosfptcvr1600)|
|MMS4C11|RHS/FRO Gen2 (Ethernet)|active|1600G|OSFP-flattop|2x800Gb/s MPO-12/APC|SM|max_m=500|980-9IAU1-00XM00|ETH|[NVIDIA](https://networking-docs.nvidia.com/9iau000xmosfptcvr1600)|
|MMS4C11|IHS/FRO Gen2 (Ethernet)|active|1600G|OSFP-finned|2x800Gb/s MPO-12/APC|SM|max_m=500|980-9IAU1-00XM01|ETH|[NVIDIA](https://networking-docs.nvidia.com/9iau000xmosfptcvr1600)|
|MMS4A00|IHS|active|1600G|OSFP-finned|2x800Gb/s MPO-12/APC|SM|max_m=500|980-9IAH1-00XM00|IB|[NVIDIA](https://networking-docs.nvidia.com/9iahx00xmosfptcvr1600)|
|MMS4A00|RHS|planned|1600G|OSFP-flattop|2x800Gb/s MPO-12/APC|SM|max_m=500|980-9IAH0-00XM00|IB|[NVIDIA](https://networking-docs.nvidia.com/9iahx00xmosfptcvr1600)|
|MMA1Z00-NS400|—|active|400G|QSFP112|1x400Gb/s MPO-12/APC|MM|OM3_m=30,OM4_m=50,max_m=50|980-9I693-00NS00|IB,ETH|[NVIDIA](https://networking-docs.nvidia.com/mms1z00ns400sr4)|
|MMS1V00-WM|—|active|400G|QSFP-DD|1x400Gb/s MPO-12/APC|SM|max_m=500|980-9I16Y-00W000|ETH|[NVIDIA](https://networking-docs.nvidia.com/mms1v00wm10)|
|MMS4X00-NS400|—|active|400G|OSFP-flattop|1x400Gb/s MPO-12/APC|SM|max_m=100|980-9I31N-00NM00|IB,ETH|[NVIDIA](https://networking-docs.nvidia.com/mms4x00ns400)|
|MMA4Z00-NS400|—|active|400G|OSFP-flattop|1x400Gb/s MPO-12/APC|MM|OM3_m=30,OM4_m=50,max_m=50|980-9I51S-00NS00|IB,ETH|[NVIDIA](https://networking-docs.nvidia.com/mma4z00ns400)|
|MMA4Z00-NS400-T|—|active|400G|OSFP-flattop|1x400Gb/s MPO-12/APC|MM|max_m=50|980-9I51S-F4NS00|ETH|[NVIDIA](https://networking-docs.nvidia.com/mma4z00ns400t)|
|MMA1Z00-NS400-T|—|active|400G|QSFP112|1x400Gb/s MPO-12/APC|MM|max_m=50|980-9I693-F4NS00|ETH|[NVIDIA](https://networking-docs.nvidia.com/mma1z00ns400t)|
|MMS1X00-NS400|—|active|400G|QSFP112|1x400Gb/s MPO-12/APC|SM|max_m=500,ordering_description_max_m=100|980-9I068-00NM00|IB,ETH|[NVIDIA](https://networking-docs.nvidia.com/mms1x00ns400)|
|MMS1V70-CM|—|active|100G|QSFP28|1x100Gb/s LC duplex|SM|max_m=500|980-9I042-00C000|ETH|[NVIDIA](https://networking-docs.nvidia.com/mms1v70cm10)|
|MMA1B00-C100D|—|active|100G|QSFP28|1x100Gb/s MPO-12/UPC|MM|OM3_m=70,OM4_m=100,max_m=100|980-9I149-00CS00|ETH|[NVIDIA](https://networking-docs.nvidia.com/mma1b00c100dspec)|
|MMS4C10-XM800|RHS/FRO Gen2|prototype|800G|OSFP-flattop|1x800Gb/s MPO-12/APC|SM|max_m=500|980-9IAY0-00XM00|IB,ETH|[NVIDIA](https://networking-docs.nvidia.com/mms4c1x800)|
|MMS4X00-NM-T|—|active|800G|OSFP-finned|2x400Gb/s MPO-12/APC|SM|max_m=500|980-9I30G-F4NM00|ETH|[NVIDIA](https://networking-docs.nvidia.com/mms4x00nmt800g)|
|MMS4X00-NM|finned|active|800G|OSFP-finned|2x400Gb/s MPO-12/APC|SM|max_m=500|980-9I30G-00NM00|IB,ETH|[NVIDIA](https://networking-docs.nvidia.com/mms4x00nm800g500m)|
|MMS4X00-NM-FLT|flat-top|active|800G|OSFP-flattop|2x400Gb/s MPO-12/APC|SM|max_m=500|980-9I301-00NM00|IB,ETH|[NVIDIA](https://networking-docs.nvidia.com/mms4x00nm800g500m)|
|MMS4X50-NM|—|active|800G|OSFP-finned|2x400Gb/s Duplex LC|SM|max_m=2000|980-9I30L-00N000|IB,ETH|[NVIDIA](https://networking-docs.nvidia.com/mms4x50nm800g2kmpub)|
|MMS4X00-NS|finned|active|800G|OSFP-finned|2x400Gb/s MPO-12/APC|SM|max_m=100|980-9I30H-00NM00|IB,ETH|[NVIDIA](https://networking-docs.nvidia.com/800gmms4x00ns)|
|MMS4X00-NS-FLT|flat-top|active|800G|OSFP-flattop|2x400Gb/s MPO-12/APC|SM|max_m=100|980-9I30I-00NM00|IB,ETH|[NVIDIA](https://networking-docs.nvidia.com/800gmms4x00ns)|
|MMA4Z00-NS-T|—|active|800G|OSFP-finned|2x400Gb/s MPO-12/APC|MM|OM3_m=30,OM4_m=50,max_m=50|980-9I510-F4NS00|ETH|[NVIDIA](https://networking-docs.nvidia.com/800gmma4z00nst)|
|MMS4X00-NS-T|—|active|800G|OSFP-finned|2x400Gb/s MPO-12/APC|SM|max_m=100|980-9I30H-F4NM00|ETH|[NVIDIA](https://networking-docs.nvidia.com/800gmms4x00nst)|
|MMS4A20|RHS|active|800G|OSFP-flattop|1x800Gb/s MPO-12/APC|SM|max_m=500|980-9IAT0-00XM00|IB|[NVIDIA](https://networking-docs.nvidia.com/9iat0mosfp800sprhs)|
|MMS4X00-NM16|—|active|800G|OSFP-finned|1x800Gb/s MPO-16/APC|SM|max_m=500|980-9I30J-F4NM00|ETH|[NVIDIA](https://networking-docs.nvidia.com/mms4x00nm16)|
|MMS4X00-NM-HGX|HGX Rubin NVL8|active|800G|OSFP-flattop|2x400Gb/s MPO-12/APC|SM|max_m=500|980-9I302-00NM00|IB,ETH,NVL|[NVIDIA](https://networking-docs.nvidia.com/mms4x00nmhgx500)|
|MMS4X90-NR|—|active|800G|OSFP-finned|2x400Gb/s Duplex LC|SM|max_m=10000|—|IB,ETH|[NVIDIA](https://networking-docs.nvidia.com/mms4x90nr800g)|
|MMS1W50-HM|—|active|200G|QSFP56|1x200Gb/s Duplex LC/UPC|SM|max_m=2000|MMS1W50-HM|IB|[NVIDIA](https://networking-docs.nvidia.com/mms1w50hmspec)|
|MMA2P00-AS|—|active|25G|SFP28|1x25Gb/s Duplex LC/UPC|MM|OM3_m=70,OM4_m=100,max_m=100|MMA2P00-AS|ETH|[NVIDIA](https://networking-docs.nvidia.com/mma2p00asspec)|

## AOC

|Model|Variant|Status|Speed|Interface|Ports|Medium|Reach|Part numbers|Fabric|Source|
|---|---|---|---|---|---|---|---|---|---|---|
|MFA7U10-H00x|finned OSFP head|active|400G|OSFP-finned -> 2xQSFP56|2x2x200Gb/s OSFP to 2xQSFP56|MM|max_m=30|980-9I41X-00H003,980-9I11Z-00H005,980-9I111-00H010,980-9I113-00H015,980-9I115-00H020,980-9I117-00H030|IB,ETH|[NVIDIA](https://networking-docs.nvidia.com/mfa7u10h00x10)|
|MFA7U10-H00x-FLT|flat-top OSFP head|active|400G|OSFP-flattop -> 2xQSFP56|2x2x200Gb/s OSFP to 2xQSFP56|MM|max_m=30|980-9I41Y-00H003,980-9I110-00H005,980-9I112-00H010,980-9I114-00H015,980-9I116-00H020,980-9I118-00H030|IB,ETH|[NVIDIA](https://networking-docs.nvidia.com/mfa7u10h00x10)|
|MFS1S00-HxxxV|—|active|200G|QSFP56|1x200Gb/s QSFP56 to QSFP56|MM|max_m=100|980-9I457-00H003,980-9I45D-00H005,980-9I45J-00H010,980-9I45O-00H015,980-9I45T-00H020,980-9I440-00H030,980-9I447-00H050,980-9I44H-00H100|IB,ETH|[NVIDIA](https://networking-docs.nvidia.com/mfs1s00hxxxv10)|

## Copper / DAC / ACC / LACC

|Model|Variant|Status|Speed|Interface|Ports|Medium|Reach|Part numbers|Fabric|Source|
|---|---|---|---|---|---|---|---|---|---|---|
|MCA4K00|RHS-to-RHS|active|1600G|OSFP-flattop -> OSFP-flattop|1x1600Gb/s OSFP to OSFP|Copper|max_m=1.1|980-9IAM1-00X001,980-9IAM2-00X001,980-9IAM4-00X001|IB,ETH,NVL|[NVIDIA](https://networking-docs.nvidia.com/mca4k00hw)|
|MCA4K50|IHS-to-IHS|active|1600G|OSFP-finned -> OSFP-finned|1x1600Gb/s OSFP to OSFP|Copper|max_m=3|980-9IAM5-00X001,980-9IAM5-00X01A,980-9IAM3-00X002,980-9IAM3-00X02A,980-9IAM3-00X003|IB|[NVIDIA](https://networking-docs.nvidia.com/mca4k50osfp1600)|
|MCA7K10|IHS-to-2xRHS|active|1600G|OSFP-finned -> 2xOSFP-flattop|2x2x800Gb/s OSFP to 2xOSFP|Copper|max_m=2|—|IB,ETH|[NVIDIA](https://networking-docs.nvidia.com/9809iao500xxxxrhs2x800)|
|MCA4J80-Nxxx|finned|active|800G|OSFP-finned -> OSFP-finned|2x2x400Gb/s OSFP to OSFP|Copper|max_m=5|980-9I60Z-00N003,980-9I601-00N004,980-9I602-00N005|IB|[NVIDIA](https://networking-docs.nvidia.com/mca4j80nxxx800pub)|
|MCA4J80-Nxxx-FLT|flat-top|active|800G|OSFP-flattop -> OSFP-flattop|2x2x400Gb/s OSFP to OSFP|Copper|max_m=3|980-9I600-00N003|IB|[NVIDIA](https://networking-docs.nvidia.com/mca4j80nxxx800pub)|
|MCA4J80-Nxxx-FTF|flat-to-finned|active|800G|OSFP-flattop -> OSFP-finned|2x2x400Gb/s OSFP to OSFP|Copper|max_m=3|980-9I601-00N003|IB|[NVIDIA](https://networking-docs.nvidia.com/mca4j80nxxx800pub)|
|MCP4Y10-Nxxx|finned|active|800G|OSFP-finned -> OSFP-finned|2x2x400Gb/s OSFP to OSFP|Copper|max_m=2|980-9IA0K-00N00A,980-9IA0F-00N001,980-9IA0Q-00N01A,980-9IA0I-00N002|IB,ETH|[NVIDIA](https://networking-docs.nvidia.com/mcp4y10nxxx2x400pub)|
|MCP4Y10-Nxxx-FLT|flat-top|active|800G|OSFP-flattop -> OSFP-flattop|2x2x400Gb/s OSFP to OSFP|Copper|max_m=2|980-9IA0L-00N00A,980-9IA0G-00N001,980-9IA0J-00N002|IB,ETH|[NVIDIA](https://networking-docs.nvidia.com/mcp4y10nxxx2x400pub)|
|MCP7Y00-Nxxx|finned head|active|800G|OSFP-finned -> 2xOSFP-flattop|2x2x400Gb/s OSFP to 2xOSFP|Copper|max_m=3|MCP7Y00-N001,MCP7Y00-N01A,MCP7Y00-N002,MCP7Y00-N02A,MCP7Y00-N003|IB,ETH|[NVIDIA](https://networking-docs.nvidia.com/mcp7y00nxxx800pub)|
|MCP7Y00-Nxxx-FLT|flat-top head|active|800G|OSFP-flattop -> 2xOSFP-flattop|2x2x400Gb/s OSFP to 2xOSFP|Copper|max_m=2|MCP7Y00-N001-FLT1,MCP7Y00-N01A-FLT,MCP7Y00-N002-FLT|IB,ETH|[NVIDIA](https://networking-docs.nvidia.com/mcp7y00nxxx800pub)|
|MCP1600-E0xxEyy|—|active|100G|QSFP28|1x100Gb/s QSFP28 to QSFP28|Copper|max_m=5|MCP1600-E00AE30,MCP1600-E001E30,MCP1600-E01AE30,MCP1600-E002E30,MCP1600-E02AE26,MCP1600-E003E26,MCP1600-E004E26,MCP1600-E005E26|IB|[NVIDIA](https://networking-docs.nvidia.com/mcp1600e0xxxeyyspec)|

## Ethernet switching

|model|family|speed|connectors|port_counts|throughput|height|cooling|Source|
|---|---|---|---|---|---|---|---|---|
|SN6810-LD|Spectrum-6 SN6000|800GbE|128x MMC-12 (co-packaged optics)|800G=128,400G=256,200G=512,100G=514|102.4 Tb/s|2U|liquid-cooled/CPO family|[NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/)|
|SN6800-LD|Spectrum-6 SN6000|200GbE|512x MMC-12 (co-packaged optics)|200G=2048,100G=2056|409.6 Tb/s (4x 102.4 Tb/s)|5U|liquid-cooled/CPO family|[NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/)|
|SN6600-LD|Spectrum-6 SN6000|800GbE|64x OSFP 2x800 Gb/s|800G=128,400G=256,200G=512,100G=514|102.4 Tb/s|2U|liquid-cooled|[NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/)|
|SN6600|Spectrum-6 SN6000|800GbE|64x OSFP 2x800 Gb/s|800G=128,400G=256,200G=512,100G=514|102.4 Tb/s|3U|air-cooled|[NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/)|
|SN6200-LD|Spectrum-6 SN6000|200GbE|32x OSFP 2x800GbE front + 256x200G backplane|200G=256,100G=258|102.4 Tb/s|1U|liquid-cooled|[NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/)|
|SN5610|Spectrum-4 SN5000|800GbE|64x OSFP 800GbE + 2x SFP28 25GbE|800G=64,400G=128,200G=256,100G=256,25G=258|51.2 Tb/s; 33.3 Bpps|2U|—|[NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/)|
|SN5600|Spectrum-4 SN5000|800GbE|64x OSFP 800GbE + 1x SFP28 25GbE|800G=64,400G=128,200G=256,100G=256,25G=257|51.2 Tb/s; 33.3 Bpps|2U|—|[NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/)|
|SN5600D|Spectrum-4 SN5000|800GbE|64x OSFP 800GbE + 1x SFP28 25GbE|800G=64,400G=128,200G=256,100G=256,25G=257|51.2 Tb/s; 33.3 Bpps|2U|—|[NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/)|
|SN5400|Spectrum-4 SN5000|400GbE|64x QSFP-DD 400GbE + 2x SFP28 25GbE|400G=64,200G=128,100G=256,25G=258|25.6 Tb/s; 33.3 Bpps|2U|—|[NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/)|
|SN4600C|Spectrum-3 SN4000|100GbE|64x QSFP28 100GbE|100G=64,50G=128,40G=64,25G=128|6.4 Tb/s; 8.4 Bpps|2U|—|[NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/)|
|SN4700|Spectrum-3 SN4000|400GbE|32x QSFP-DD 400GbE|400G=32,200G=64,100G=128,50G=128,40G=64,25G=128|12.8 Tb/s; 8.4 Bpps|1U|—|[NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/)|
|SN3420|Spectrum-2 SN3000|100GbE|12x QSFP28 100GbE + 48x SFP28 25GbE|100G=12,40G=12,25G=96|2.4 Tb/s; 3.57 Bpps|1U|—|[NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/)|
|SN2201|Spectrum SN2000|100GbE|48x RJ45 + 4x QSFP28 100GbE|100G=4,50G=8,40G=4,25G=16,1G=48|448 Gb/s; 667 Mpps|1U|—|[NVIDIA](https://www.nvidia.com/en-us/networking/ethernet-switching/)|

## InfiniBand switching and appliances

|model|family|speed|connectors|port_counts|throughput|height|cooling|compatibility|reach|Source|
|---|---|---|---|---|---|---|---|---|---|---|
|Q3200-RA|Quantum-X800|800Gb/s XDR|2x18 OSFP|800G=72|2x28.8 Tb/s|2U|air-cooled|Quantum-X800,Quantum-2 storage migration|—|[NVIDIA](https://www.nvidia.com/en-us/networking/infiniband-switching/)|
|Q3400-RA|Quantum-X800|800Gb/s XDR|72x OSFP|800G=144|115.2 Tb/s|4U|air-cooled|—|—|[NVIDIA](https://www.nvidia.com/en-us/networking/infiniband-switching/)|
|Q3401-RD|Quantum-X800|800Gb/s XDR|72x OSFP|800G=144|115.2 Tb/s|4U|air-cooled; DC power|—|—|[NVIDIA](https://www.nvidia.com/en-us/networking/infiniband-switching/)|
|Q3450-LD|Quantum-X Photonics / Quantum-X800|800Gb/s XDR|144x MPO12 CPO|800G=144|115.2 Tb/s|4U|liquid-cooled (CPO)|—|—|[NVIDIA](https://www.nvidia.com/en-us/networking/infiniband-switching/)|
|QM9700 family|Quantum-2|400Gb/s NDR|OSFP|—|51.2 Tb/s class|—|—|ConnectX-7,NDR/HDR|—|[NVIDIA](https://www.nvidia.com/en-us/networking/infiniband-switching/)|
|Skyway|InfiniBand-to-Ethernet Gateway|100/200 Gb/s per port|8 ports per InfiniBand and Ethernet side|—|1.6 Tb/s|—|—|InfiniBand,Ethernet|—|[NVIDIA](https://www.nvidia.com/en-us/networking/infiniband-switching/)|
|MetroX-3 XC|Long-haul InfiniBand|InfiniBand extension|—|—|—|—|—|DWDM,encrypted long-haul|max_km=40|[NVIDIA](https://www.nvidia.com/en-us/networking/infiniband-switching/)|
|UFM Telemetry|UFM platform|—|—|—|—|—|—|switch/adapters/cables telemetry,on-prem/cloud database|—|[NVIDIA](https://www.nvidia.com/en-us/networking/infiniband-switching/)|
|UFM Enterprise|UFM platform|—|—|—|—|—|—|Slurm,IBM Spectrum LSF,REST API|—|[NVIDIA](https://www.nvidia.com/en-us/networking/infiniband-switching/)|
|UFM Cyber-AI|UFM platform|—|—|—|—|—|—|UFM Telemetry,UFM Enterprise|—|[NVIDIA](https://www.nvidia.com/en-us/networking/infiniband-switching/)|

## Silicon Photonics

|model|family|speed|throughput|availability|compatibility|Source|
|---|---|---|---|---|---|---|
|Q3450-LD|Quantum-X InfiniBand Photonics|800Gb/s XDR|115.2 Tb/s|—|Quantum-X800,200G SerDes,co-packaged optics|[NVIDIA](https://www.nvidia.com/en-us/networking/products/silicon-photonics/)|
|Spectrum-X Ethernet Photonics Switches|Spectrum-X Ethernet Photonics|200G SerDes CPO architecture|up to 409.6 Tb/s|2H 2026|Spectrum-X Ethernet,co-packaged optics|[NVIDIA](https://www.nvidia.com/en-us/networking/products/silicon-photonics/)|

## DPU / BlueField

|model|speed|compatibility|Source|
|---|---|---|---|
|BlueField-4 DPU|800Gb/s|networking,storage,cybersecurity,secure multi-tenancy|[NVIDIA](https://www.nvidia.com/en-us/networking/products/data-processing-unit/)|
|BlueField-4 STX Storage Processor|—|AI-native storage,Vera CPU,in-silicon security|[NVIDIA](https://www.nvidia.com/en-us/networking/products/data-processing-unit/)|
|BlueField-3 DPU|400Gb/s|SDN,storage,cybersecurity,HPC,5G|[NVIDIA](https://www.nvidia.com/en-us/networking/products/data-processing-unit/)|

## SuperNIC

|model|speed|compatibility|Source|
|---|---|---|---|
|ConnectX-9 SuperNIC|up to 1.6 Tb/s per GPU|Spectrum-X Ethernet,AI fabrics|[NVIDIA](https://www.nvidia.com/en-us/networking/products/ethernet/supernic/)|
|ConnectX-8 SuperNIC|up to 800 Gb/s total network bandwidth|PCIe Gen6,Spectrum-X Ethernet,AI compute fabrics|[NVIDIA](https://www.nvidia.com/en-us/networking/products/ethernet/supernic/)|
|BlueField-3 SuperNIC|up to 400 Gb/s|Spectrum-X Ethernet,secure cloud multi-tenancy,deterministic isolated performance|[NVIDIA](https://www.nvidia.com/en-us/networking/products/ethernet/supernic/)|
