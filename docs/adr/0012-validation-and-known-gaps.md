# 0012. How this was validated and what is NOT verified
- Status: Accepted
- Date: 2026-09-18

## Context
The repo was authored in a sandbox with no access to Google Cloud or the Terraform registry.

## Verified offline
- `dataform compile` (CLI 3.0.70) succeeds with zero graph errors: 14 tables/views, 15 built-in + manual
  assertions, 5 declarations; `dependOnDependencyAssertions` produces the expected dependencies.
- The compiled Dataform SQL and the plain-SQL files were executed in DuckDB (translated from BigQuery with
  sqlglot) against the real CSVs: batch 1, then batch 2 (incremental result equals a full refresh), then the bad
  batch. Dataform-style pipeline and plain-SQL pipeline produce identical marts. With the bad batch,
  Dataform assertions fail and downstream tables are skipped; plain SQL builds the bad data before its checks fail.
- Python scripts import and `--dry-run` works; `uv.lock` resolves.
- `tofu fmt -check` passes (syntax only).

## NOT verified (first things to test on real GCP)
- `terraform validate/plan/apply` (resource arguments were checked against provider docs, not executed).
- BigQuery-specific syntax (`MERGE ... INSERT ROW`, `ALTER TABLE ... SET OPTIONS(labels)`, partition/cluster DDL).
- Dataform Cloud compile with `dataformCoreVersion: 3.0.70`, PAT acceptance (fine-grained vs classic) and
  the exact console clicks in README step 6.
- Load jobs against BigQuery (CSV timestamp parsing, NUMERIC).

## Consequences
Expect a short debugging loop on the first real `terraform apply` and Dataform run; report errors and fix them here.
