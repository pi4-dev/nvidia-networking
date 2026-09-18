# NVIDIA Networking Reference

A compact technical reference for current NVIDIA networking products used in AI, HPC, data center, and accelerated computing environments.

The repository contains a human-readable equipment catalog together with the normalized JSON dataset used as its source of truth.

## Repository contents

```text
.
├── README.md
├── network_equipment.md
├── data/
│   └── nvidia-interconnects.json
└── compatibility-validator/
    ├── README.md
    ├── Dockerfile
    ├── docker-compose.yml
    ├── requirements.in
    ├── requirements.txt
    ├── app/
    └── data/
        └── device-profiles.json
```

### `network_equipment.md`

Generated catalog of active NVIDIA networking products, including:

- Spectrum Ethernet switches
- Quantum / Quantum-X InfiniBand switches and appliances
- Silicon Photonics platforms
- BlueField DPUs
- Ethernet SuperNICs
- UFM management products
- NVIDIA LinkX transceivers
- NVIDIA LinkX copper, optical, and adapter interconnects

The file is intended for quick technical lookup and comparison.

### `compatibility-validator/`

Interactive web application for validating NVIDIA LinkX transceivers, AOCs and copper cable assemblies against NVIDIA switches, DPUs, SuperNICs and DGX port profiles.

The validator uses the repository's live `data/nvidia-interconnects.json` dataset and checks, where applicable:

- active product status
- fabric compatibility (`ETH`, `IB`, `NVL`)
- connector and module/cage compatibility
- OSFP mechanical variant (finned vs. flat-top)
- supported module speed and port mode
- aggregate cage capacity for multi-lane interfaces

The GUI exposes only products accepted for the selected device and physical port group and shows the reasons and confidence level for each compatibility decision.

Dependency installation is hash-locked with exact versions and SHA-256 verification; see the application README for regeneration and runtime hardening details.

Run from the repository root:

```bash
docker compose -f compatibility-validator/docker-compose.yml up -d --build
```

Then open `http://localhost:8080/`. See [`compatibility-validator/README.md`](compatibility-validator/README.md) for implementation details and API endpoints.

### `data/nvidia-interconnects.json`

Normalized machine-readable source dataset used to build the catalog.

It contains structured information such as:

- product family and model
- interface speed and protocol
- connector and port configuration
- throughput
- optical medium and wavelength
- supported reach
- cable-side interface layout
- NVIDIA part numbers
- compatibility information
- source URLs
- product status

The dataset also preserves selected inconsistencies found in NVIDIA source documentation instead of silently normalizing conflicting values.

## Data model

The JSON dataset is versioned using the `schema_version` field.

Current schema highlights include normalized transceiver attributes for:

```text
interface_count
interface_speed
interface_type
medium_SM_MM
reach
part_numbers
```

Products are primarily identified by:

```text
scope + model
```

Formatting and ordering changes are not intended to be treated as product changes.

## Product status

The generated catalog focuses on products considered active/current at the time of the snapshot.

Products marked as no longer for sale remain available in the JSON dataset where useful for change tracking, but are intentionally excluded from the main equipment catalog.

## Source of truth

The canonical dataset in this repository is:

[`data/nvidia-interconnects.json`](data/nvidia-interconnects.json)

The Markdown catalog is derived from that dataset:

[`network_equipment.md`](network_equipment.md)

When updating the repository, changes should normally be made to the normalized dataset first and then reflected in the generated catalog.

## Primary upstream sources

The dataset is built from public NVIDIA networking documentation, including:

- NVIDIA Ethernet Switching
- NVIDIA InfiniBand Switching
- NVIDIA LinkX Interconnect documentation
- NVIDIA Silicon Photonics
- NVIDIA BlueField DPU documentation
- NVIDIA Ethernet SuperNIC documentation

Exact source URLs are stored in the JSON dataset and referenced from the generated Markdown catalog.

## Typical use cases

This repository can be used for:

- quick comparison of NVIDIA networking hardware
- AI factory and HPC fabric design work
- Ethernet vs. InfiniBand equipment selection
- LinkX transceiver and cable compatibility analysis
- automation and inventory tooling
- detecting portfolio and specification changes over time
- feeding structured product data into scripts, dashboards, or documentation pipelines

## Update principles

When refreshing the dataset:

1. Prefer NVIDIA primary documentation.
2. Preserve model identity across formatting changes.
3. Do not treat record ordering as a semantic change.
4. Keep conflicting upstream specifications visible in notes when they cannot be resolved reliably.
5. Update the snapshot metadata.
6. Regenerate `network_equipment.md` from the normalized JSON source.

## Disclaimer

This is an independent technical reference and is not an official NVIDIA repository.

Product specifications can change. For procurement, deployment, or compatibility decisions, verify the relevant NVIDIA product documentation and ordering information.