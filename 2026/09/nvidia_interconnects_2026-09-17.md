# NVIDIA networking portfolio changes — 2026-09-17

## Latest run: schema v7 / AOC + Copper detail and fabric compatibility

Rozszerzono inwentaryzację LinkX tak, aby aktywne **Transceivers, AOC i Copper** miały dane techniczne wymagane do walidacji połączeń: liczba interfejsów, przepustowość, typ złącza/form-factor, medium, reach oraz kompatybilność fabricową (`IB`, `ETH`, `NVL`). Warianty OSFP finned/flat-top są rozdzielane, gdy NVIDIA publikuje osobne OPN-y.

### DODANE

Dodano 14 szczegółowych rekordów aktywnych AOC/Copper:

- **AOC**: `MFA7U10-H00x` finned, `MFA7U10-H00x-FLT` flat-top, `MFS1S00-HxxxV`.
- **Copper 1600G**: `MCA4K00`, `MCA4K50`, `MCA7K10`.
- **Copper 800G**: `MCA4J80-Nxxx` finned, `MCA4J80-Nxxx-FLT`, `MCA4J80-Nxxx-FTF`, `MCP4Y10-Nxxx` finned, `MCP4Y10-Nxxx-FLT`, `MCP7Y00-Nxxx` finned-head, `MCP7Y00-Nxxx-FLT` flat-top-head.
- **Copper 100G**: `MCP1600-E0xxEyy`.

Przykładowe OPN-y i warianty:

- `MFA7U10-H00x`: finned OPN `980-9I41X-00H003`…`980-9I117-00H030`; flat-top OPN `980-9I41Y-00H003`…`980-9I118-00H030`.
- `MCA4K00`: `980-9IAM1-00X001`, `980-9IAM2-00X001`, `980-9IAM4-00X001`; RHS/RHS, kompatybilność IB/ETH/NVL.
- `MCA4K50`: `980-9IAM5-00X001`…`980-9IAM3-00X003`; IHS/IHS, InfiniBand XDR.
- `MCA4J80-Nxxx`: standard/finned `980-9I60Z-00N003`, `980-9I601-00N004`, `980-9I602-00N005`; flat-top `980-9I600-00N003`; flat-to-finned `980-9I601-00N003`.
- `MCP4Y10-Nxxx`: osobne OPN-y finned i flat-top.
- `MCP7Y00-Nxxx`: osobne warianty finned-head i flat-top-head.

### ZMIENIONE

- schema: `6 -> 7`
- dodano sekcje szczegółowe `linkx.aoc` i `linkx.copper` wraz z jednolitym zestawem pól technicznych.
- dodano mapę `linkx.transceiver_fabric_compatibility` dla aktywnych transceiverów.
- transceivery zachowują wcześniejszy podział OSFP finned vs flat-top; nie zmieniono ich parametrów fizycznych w tym przebiegu.

### USUNIĘTE

- brak zmian merytorycznych / brak usuniętych aktywnych produktów.

## Przykłady kompatybilności

- `MCA4K00`: firmware wspiera InfiniBand, Ethernet i NVL5.
- `MCA4K50`: InfiniBand XDR / Quantum-3.
- `MCA7K10`: InfiniBand i Ethernet; zastosowanie Quantum-3 → ConnectX-8.
- `MFA7U10-H00x`: IB i Ethernet, z ograniczeniem do ConnectX-6 po stronie opisanej przez NVIDIA.
- `MCP4Y10-Nxxx`, `MCP7Y00-Nxxx`: InfiniBand i Ethernet.
- `MFS1S00-HxxxV`: InfiniBand HDR i 200GbE.

## Pozostałe sekcje portfolio

Nie wykryto zmian merytorycznych w aktualnych listach Ethernet Switching, InfiniBand Switching, Silicon Photonics, DPU ani SuperNIC.

## Source URLs

- LinkX / Interconnect: https://networking-docs.nvidia.com/interconnect
- MCA4K00: https://networking-docs.nvidia.com/mca4k00hw
- MCA4K50: https://networking-docs.nvidia.com/mca4k50osfp1600
- MCA7K10: https://networking-docs.nvidia.com/9809iao500xxxxrhs2x800
- MFA7U10-H00x: https://networking-docs.nvidia.com/mfa7u10h00x10
- MCA4J80-Nxxx: https://networking-docs.nvidia.com/mca4j80nxxx800pub
- MCP4Y10-Nxxx: https://networking-docs.nvidia.com/mcp4y10nxxx2x400pub
- MCP7Y00-Nxxx: https://networking-docs.nvidia.com/mcp7y00nxxx800pub
- MFS1S00-HxxxV: https://networking-docs.nvidia.com/mfs1s00hxxxv10
- MCP1600-E0xxEyy: https://networking-docs.nvidia.com/mcp1600e0xxxeyyspec
- Ethernet switching: https://www.nvidia.com/en-us/networking/ethernet-switching/
- InfiniBand switching: https://www.nvidia.com/en-us/networking/infiniband-switching/
- Silicon Photonics: https://www.nvidia.com/en-us/networking/products/silicon-photonics/
- DPU: https://www.nvidia.com/en-us/networking/products/data-processing-unit/
- SuperNIC: https://www.nvidia.com/en-us/networking/products/ethernet/supernic/
