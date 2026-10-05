# NVIDIA Networking Inventory Change Report — 2026-10-05

Compared with repository snapshot: **2026-10-02**

## Added

### Skyway-3 InfiniBand-to-Ethernet Gateway

NVIDIA's current switch/appliance hardware documentation includes **Skyway-3**, which is not present in the previous normalized inventory.

- Model: **Skyway-3**
- NVIDIA SKU: `920-9B02D-00RG-CF0`
- Legacy OPN: `MGA400-XS2`
- Networking: 8× ConnectX-8 VPI
- Interfaces: QSFP112; 8× InfiniBand + 8× Ethernet
- Pluggable type: QSFP112
- Source: https://networking-docs.nvidia.com/skyway3

## Removed

None confirmed.

## Changed

### Inventory schema
- `schema_version`: **8 -> 9**
- InfiniBand product records are extended with required general inventory metadata: `status`, `part_numbers`, and `source_url`.
- Pluggable-capable product metadata is extended to retain supported pluggable speeds together with cage/type information.

The compatibility-validator must be updated to accept and validate schema v9 before the new state is considered complete.

## Validation notes

HTML/layout-only changes were ignored. Skyway-3 is treated as a substantive addition because NVIDIA publishes a distinct product model/SKU and hardware documentation.
