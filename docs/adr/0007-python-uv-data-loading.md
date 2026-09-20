# 0007. Python + uv for data generation and loading
- Status: Accepted
- Date: 2026-09-18

## Context
Sample CSVs must reach BigQuery `raw` with minimal moving parts.

## Decision
- Python managed with **uv** (`pyproject.toml`, `uv.lock`, `.python-version`). Console scripts:
  `dfdemo-generate`, `dfdemo-load`, `dfdemo-run-sql`, `dfdemo-preflight`.
- Single runtime dependency: `google-cloud-bigquery`.
- `dfdemo-load` uses **BigQuery load jobs from local files with explicit schemas** (no autodetect). Batch `1`
  truncates (safe to repeat the demo); `2` and `bad` append. `--dry-run` needs no credentials.
- The loader creates the raw tables; Terraform only creates datasets.

## Consequences
+ Simple, fast, easy to explain on stream. Schemas are visible in code.
- Loading is not idempotent for batches 2 and bad (running them twice duplicates rows). Re-run batch 1 to reset.

## Alternatives considered
`bq load` in shell (fine but schema handling clumsier); GCS bucket + Terraform load jobs (more infra);
autodetect (unstable types).
