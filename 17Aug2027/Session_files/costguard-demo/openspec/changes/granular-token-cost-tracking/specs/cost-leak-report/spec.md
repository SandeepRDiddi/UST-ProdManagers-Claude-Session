## Purpose

Surfaces where token spend is concentrated by ranking task-phases by cost
directly, independent of whether they breach a budget cap or trip the
complexity-outlier threshold, so a leak can be seen even when no configured
rule flags it.

## ADDED Requirements

### Requirement: Cost-leak report ranks task-phases by cost
The system SHALL produce a report listing the top N task-phase records by
`cost_usd` in descending order, where N is configurable and defaults to 10.
The report SHALL run regardless of the outcome of the budget, outlier, and
hybrid-routing checks.

#### Scenario: Top contributor is not a budget or outlier flag
- **WHEN** a task-phase record has the highest `cost_usd` in the dataset but
  does not exceed its phase's budget cap or its complexity tier's outlier
  multiplier
- **THEN** the cost-leak report still lists it among the top N contributors

#### Scenario: Fewer records than N exist
- **WHEN** the dataset contains fewer task-phase records than the configured
  N
- **THEN** the report lists all available records ranked by cost, without
  error

### Requirement: Each ranked entry shows its token-type breakdown
For every task-phase record listed in the cost-leak report, the system SHALL
show the per-token-type cost contribution (cache-read, cache-write,
reasoning, tool-use, input, output), so the source of that record's spend is
visible, not just its total.

#### Scenario: Entry dominated by cache or reasoning spend
- **WHEN** a top-ranked record's cost is driven primarily by
  `reasoning_tokens` or `cache_write_tokens` rather than input/output tokens
- **THEN** the report's breakdown for that entry shows the reasoning or
  cache-write contribution as the largest component

### Requirement: Report identifies task and phase for each entry
Each entry in the cost-leak report SHALL identify the `task_id` and `phase`
it belongs to, so a specific leak can be traced back to where it occurred.

#### Scenario: Entry traceable to source
- **WHEN** the cost-leak report is generated
- **THEN** every listed entry includes its `task_id` and `phase`
