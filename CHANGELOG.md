# Changelog

## 0.2.0 (unreleased)

### Added
- Allergies. The schema has an optional `allergies` list. Each item has the allergy
  `text` and its `source` sentence, and nothing else.
- `Allergy` dataclass and `RecoveryState.allergies`, an empty list by default.
- `validate_allergies`. It flags an allergy with missing or unclear text and never
  drops or changes it. `validate_recovery_plan` runs it.
- `SCHEMA_VERSION`, the version of the bundled schema.

### Changed
- Task clock times must be written as HH:MM, for example 07:30. Values like 7:30,
  25:00 or 07:30:00 no longer pass the schema.
- The test extra now installs `jsonschema`. The package itself still has no
  dependencies.

### Unchanged
- Data without an `allergies` list still passes the schema.
- Appointment times keep their old rule, because they can carry uncertainty markers.

## 0.1.0 (2026-10-13)

- First release.
