## Purpose

Captures token spend at a per-type granularity (cache-read, cache-write,
reasoning, tool-use, input, output) for every task-phase record, so cost can
be attributed to the specific kind of token activity that produced it instead
of a single input/output split.

## ADDED Requirements

### Requirement: Task-phase records carry a token-type breakdown
Each record in the token log SHALL report token counts broken out by type:
`input_tokens`, `output_tokens`, `cache_read_tokens`, `cache_write_tokens`,
`reasoning_tokens`, and `tool_use_tokens`. `total_tokens` SHALL equal the sum
of all six type-level fields for that record.

#### Scenario: Record with all token types populated
- **WHEN** a task-phase record is generated with non-zero values for every
  token type
- **THEN** `total_tokens` equals the sum of `input_tokens`, `output_tokens`,
  `cache_read_tokens`, `cache_write_tokens`, `reasoning_tokens`, and
  `tool_use_tokens`

#### Scenario: Record with a token type absent
- **WHEN** a task-phase record has no tool-use or cache activity (those
  fields are `0`)
- **THEN** `total_tokens` still equals the sum of the remaining populated
  fields, with the zero-valued types contributing nothing

### Requirement: Cost is computed per token type
The system SHALL price each token type independently and SHALL compute a
record's `cost_usd` as the sum of each token type's count multiplied by its
own per-million-token rate for the record's model tier (frontier or
efficient), not a single blended input/output rate.

#### Scenario: Cost includes cache and reasoning spend
- **WHEN** a record has non-zero `cache_read_tokens` and `reasoning_tokens`
  in addition to `input_tokens`/`output_tokens`
- **THEN** `cost_usd` reflects the priced contribution of all four token
  types, not just input/output

### Requirement: Loading a token log without type-level columns fails
The system SHALL require `cache_read_tokens`, `cache_write_tokens`,
`reasoning_tokens`, and `tool_use_tokens` columns when loading a token log.
It SHALL raise an error rather than silently defaulting missing columns to
zero.

#### Scenario: Legacy log missing new columns
- **WHEN** a CSV file lacking the four new token-type columns is loaded
- **THEN** the system raises an error identifying the missing column(s)
  instead of proceeding with partial data
