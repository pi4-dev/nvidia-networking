# Changelog

Notable changes to this repository and `compatibility-validator`, newest first.
Entries describe implemented behavior and its effect on users. Proposed work belongs
in issues or planning documents.

`Unreleased` tracks changes after the latest recorded milestone, including changes
already on `main`. Dated `-dev` entries identify development milestones, not stable
releases. Historical dates below come from their referenced commits. The `v0.01`,
`v0.02`, `v0.03` and `v0.04` branches preserve earlier repository states.

## [Unreleased]

No changes since the latest milestone.

## [0.05-dev] - 2026-09-22

### Added

- Cabling plans with rack/U locations, native port markings, stable and editable
  cable IDs, per-branch installation rows, and labels for both ends. Complete
  breakouts share one head label per physical connector.
- A4 installation-plan and cut-out label PDFs, plus XLSX with separate plan and
  label worksheets. Exports retain catalog revision, application version,
  provisional status and installation declarations.
- Installed/checked controls in the project GUI and JSON metadata for locations,
  labels, cable IDs, progress and notes. Existing project JSON remains supported.
- Revision-aware cabling API routes, a ready-to-edit installation example, and
  bundled DejaVu Sans with its license for self-contained PDF generation.
- Repository changelog with reconstructed history from the `v0.01` baseline through
  `0.04-dev`, linked from both READMEs.
- Changelog maintenance instructions in `AGENTS.md` so future repository changes
  include their history entry in the same commit.

### Changed

- Installation confirmations are bound to the physical definition, including
  rack/port markings, cable ID, PN and effective length. Changes invalidate stale
  confirmations; installer declarations never upgrade compatibility.
- Missing installation details remain explicit, and unresolved compatibility
  keeps documents provisional. Optical module PNs remain separate from the
  labeled fiber/harness PN; cut-out labels use variable-size cards, not a
  pre-cut adhesive-stock template.
- Project JSON and browser drafts retain installation metadata. Point-to-point
  CSV export rejects nonempty cabling metadata to prevent silent data loss;
  PDF/XLSX files are snapshots and XLSX edits cannot be reimported.
- ReportLab/openpyxl and their dependencies are pinned with hashes. Export
  concurrency is bounded; spreadsheet strings remain literal and PDF text is
  escaped. Exports generate in memory without runtime network requests.
- Regression coverage increased to 97 backend and 32 frontend tests, verified
  with a clean runtime dependency installation. The HTTP smoke test now checks
  the cabling plan and all PDF/XLSX downloads. PDF and worksheet previews were
  visually reviewed, including Polish text and long paginated PDF rows.

Previous state: branch [`v0.04`](https://github.com/pi4-dev/nvidia-networking/tree/v0.04),
commit [`231c96f`](https://github.com/pi4-dev/nvidia-networking/commit/231c96fe07230279edfe8817da89528c754ee4e5).

## [0.04-dev] - 2026-09-22

### Added

- Complete cable and optical breakout validation for one shared head and up to
  16 branches: explicit operating modes, termination and logical-link coverage,
  aggregate bandwidth, common FEC, and optical Tx/Rx lane mapping.
- Project validation for connections and complete breakouts, with physical device
  identities, cage allocation and detection of duplicate ports or conflicting
  hardware/runtime declarations.
- Consolidated BOM and project-wide inventory allocation, counting each physical
  assembly and shared head module once and reporting required, reused, to-buy and
  unused quantities.
- Breakout and project GUI workflows, saved browser drafts, complete JSON
  interchange, point-to-point CSV import/export, and BOM CSV export.
- Breakout/project APIs, documented limits and ready-to-edit JSON/CSV examples.

### Changed

- Incomplete single-leg or multi-connector selections remain required unknowns in
  projects. A valid individual branch does not approve the entire breakout.
- Scoped harness/interoperability evidence stays with the project; manufacturer
  and lab evidence remain distinct from hardware/firmware/OS qualification.
- Invalid or unresolved entries remain visible in a provisional BOM.
- Catalog refresh preserves unapplied JSON edits. Draft changes invalidate reports,
  and stale or unversioned imports require renewed physical mapping confirmation.
- Regression coverage increased to 83 backend and 27 frontend tests; the HTTP smoke
  test also exercises a complete breakout and project BOM.

Reference: commit [`674fad8`](https://github.com/pi4-dev/nvidia-networking/commit/674fad8f5d87413f81a02bfd342a0c2d14a67041).

## [0.03-dev] - 2026-09-21

### Added

- Exact board profiles with OPN/SKU/variant identity, observed PSID, firmware and OS
  context, dated manufacturer/lab sources, and actionable evidence gaps.
- Product-specific qualification results kept separate from technical compatibility.
- Connection assistant comparing cables and module–fiber–module assemblies by
  fabric, per-link bandwidth, minimum length, exact PNs and inventory reuse.
- Four sourced ConnectX-8 hardware profiles and 21 fiber ordering assemblies,
  without inventing missing PSIDs, firmware qualifications or FEC values.
- Hardware inspection and recommendation APIs, GUI workflows, configuration
  sharing, JSON reports and stale-response protection.

### Changed

- Assistant results expose exact SKU length, port orientation/settings, quantities,
  incomplete ordering evidence and bounded-search truncation.
- Regression coverage expanded to 58 backend and 17 frontend tests, with hardware
  inspection and recommendations included in the HTTP smoke test.

Snapshot: branch [`v0.03`](https://github.com/pi4-dev/nvidia-networking/tree/v0.03),
commit [`a2a41c6`](https://github.com/pi4-dev/nvidia-networking/commit/a2a41c6210a3267068daae0b387a31fa0c49cee2).

## [0.02-dev] - 2026-09-21

### Added

- Complete A–B connection checks for both cable ends and optical paths, using
  explicit per-cage modes, SKU lengths, optical parameters and common FEC.
- Rejected/retired-product diagnostics, saved and shared configurations, JSON
  result export and protection against obsolete browser responses.
- Structured data-model documentation and GitHub Actions regression/container
  checks: 34 backend tests, 11 frontend tests and an HTTP smoke test.

### Changed

- Split the application into strict contracts, catalog loading, validation rules,
  HTTP routes and browser modules.
- Expanded schema and cross-file validation for explicit hardware profiles. Failed
  reloads retain the last valid snapshot and expose ready/degraded catalog status.
- Missing required mechanical, electrical or optical evidence remains `unknown`;
  an exact cage match alone does not approve a complete connection.

Snapshot: branch [`v0.02`](https://github.com/pi4-dev/nvidia-networking/tree/v0.02),
commit [`d52782b`](https://github.com/pi4-dev/nvidia-networking/commit/d52782bd3ba8d282d1e999ba16b4f2073f501b67).

## [0.01] - 2026-09-19

This is the retrospectively named repository baseline. Its original FastAPI
metadata reported `0.5.0`; the snapshot label does not rewrite that historical value.

### Included in the baseline

- NVIDIA networking reference catalog, canonical JSON data and the web validator
  renamed from `bom-calculator` to `compatibility-validator`.
- Host-port compatibility filtering, explicit profile data and Docker Compose startup.
- Bounded input/schema checks, revision-aware caching, last-valid catalog fallback,
  minimal health responses and errors that omit internal exception details.
- Hardened container runtime and pinned Python dependencies with SHA-256 hashes
  and binary-only installation.

### Fixed

- Dockerfile `pip` command continuation that prevented the image from building.

Snapshot: branch [`v0.01`](https://github.com/pi4-dev/nvidia-networking/tree/v0.01),
commit [`6071fa9`](https://github.com/pi4-dev/nvidia-networking/commit/6071fa9f05b7ea5e116094f518fd4b6c15992867).

## Maintaining this file

- Update `Unreleased` in the same commit as each meaningful application, catalog,
  profile, dependency, deployment, documentation or workflow change.
- Use applicable categories: `Added`, `Changed`, `Fixed`, `Security`, `Deprecated`,
  `Removed`. Omit empty categories and describe the user-visible effect concisely.
- When recording the next version, move the accumulated entries into a dated
  section, leave `Unreleased` ready for subsequent changes, and keep the application
  version and READMEs consistent. Documentation-only updates do not require a bump.
- Preserve historical entries, dates and snapshot references. Correct factual
  errors explicitly; never record planned features as completed or tests as passed
  unless they actually ran successfully.

[Unreleased]: https://github.com/pi4-dev/nvidia-networking/blob/main/CHANGELOG.md#unreleased
[0.05-dev]: https://github.com/pi4-dev/nvidia-networking/compare/674fad8f5d87413f81a02bfd342a0c2d14a67041...main
[0.04-dev]: https://github.com/pi4-dev/nvidia-networking/compare/a2a41c6210a3267068daae0b387a31fa0c49cee2...674fad8f5d87413f81a02bfd342a0c2d14a67041
[0.03-dev]: https://github.com/pi4-dev/nvidia-networking/compare/d52782bd3ba8d282d1e999ba16b4f2073f501b67...a2a41c6210a3267068daae0b387a31fa0c49cee2
[0.02-dev]: https://github.com/pi4-dev/nvidia-networking/compare/6071fa9f05b7ea5e116094f518fd4b6c15992867...d52782bd3ba8d282d1e999ba16b4f2073f501b67
[0.01]: https://github.com/pi4-dev/nvidia-networking/tree/6071fa9f05b7ea5e116094f518fd4b6c15992867
