# NVIDIA Networking Inventory Change Report — 2026-10-02

Compared with repository snapshot: **2026-10-01**

## Added

### Legacy network adapters

The NVIDIA Networking Documentation adapter catalog explicitly includes legacy adapter families that were not represented in the normalized inventory.

- **ConnectX-5 / MCX516A-CCAT** — legacy adapter; dual-port QSFP28; up to 100GbE per port / EDR InfiniBand; source: https://networking-docs.nvidia.com/connectx5en
- **ConnectX-4 / MCX455A-ECAT** — legacy adapter; QSFP28; 100GbE / EDR InfiniBand class; source: https://networking-docs.nvidia.com/connectx4
- **ConnectX-4 Lx / MCX4121A-ACAT** — legacy Ethernet adapter; dual-port SFP28; up to 25GbE per port; source: https://networking-docs.nvidia.com/connectx4lx

These are classified as **legacy**, not active/current products.

## Removed

None confirmed.

## Changed

None confirmed in the previously inventoried active portfolio.

## Validation notes

HTML/layout-only differences were ignored. This change closes a catalog coverage gap: the products are added because NVIDIA's adapter catalog exposes them as legacy hardware families, not because of a page-formatting change.

Schema structure remains **v8**; therefore no compatibility-validator schema migration is required.
