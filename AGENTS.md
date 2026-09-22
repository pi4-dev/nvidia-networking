# Repository instructions

## Changelog maintenance

The user requires an ongoing changelog. `CHANGELOG.md` at the repository root is
the single history for this repository and `compatibility-validator`.

- Read its latest entries before making changes.
- Include a concise entry under `Unreleased` in the same commit as each meaningful
  application, catalog/profile, dependency, deployment, documentation or workflow
  change. Describe the resulting behavior, fixes and relevant limitations.
- Follow the categories and versioning procedure in `CHANGELOG.md`. Keep historical
  entries and commit references accurate; record completed work only.
- When a version changes, move accumulated entries to the new dated section,
  update comparison links, and align the version in the application and READMEs.
  Documentation-only changes do not require a version bump.
- Before publishing, check that the changelog matches the diff. Record validation
  results only when actually verified. No application tests are required solely
  for prose changes; check Markdown links and whitespace instead.
