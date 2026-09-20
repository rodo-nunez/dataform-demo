# 0009. Plain-SQL equivalent of the pipeline
- Status: Accepted
- Date: 2026-09-18

## Context
To argue for Dataform, the audience must see the same pipeline without it and feel the friction.

## Decision
`sql/NN_*.sql` mirrors every Dataform model, writing to the `plain_sql` dataset with hardcoded, fully
qualified names. A minimal runner executes them in filename order. Each file states its Dataform equivalent
and the limitation it shows (`-- LIMITATION:`). The incremental model is a hand-written `CREATE TABLE IF NOT
EXISTS` + `MERGE`. Checks are `ASSERT` statements at the end. `sql/compare_results.sql` proves equal outputs.
The runner deliberately has NO templating, ordering or gating: adding them would rebuild Dataform.

## Consequences
+ Fair comparison: identical logic, identical results (validated, see ADR 0012).
- Hardcoded project id repeated in every file (ADR 0011).

## Alternatives considered
Jinja/`envsubst` placeholders in SQL (hides the pain the demo wants to show); BigQuery scheduled queries
(different comparison, UI-only).
