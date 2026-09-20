# Spec: Dataform demo repo (MVP)

## Goal
A self-contained repo to run a ~90-minute stream about Dataform (en_coders): 45 min of slides on Dataform vs
plain SQL, 45 min of live demo on a personal GCP project. Success = two Dataform processes running in GCP,
infrastructure created and destroyed with Terraform.

## Requirements
| ID | Requirement | Where |
|---|---|---|
| R-01 | All GCP infrastructure is created with Terraform and removable with one `destroy` | `terraform/`, ADR 0003 |
| R-02 | Sample data is reproducible and loadable into BigQuery with a Python/uv process | `src/`, `data/`, ADR 0006/0007 |
| R-03 | Dataform project in `.sqlx` (+ JS includes) covering: refs, declarations, assertions, incremental, JS templating, tags, post-ops | `definitions/`, `includes/`, ADR 0008 |
| R-04 | Same pipeline in plain `.sql`, annotated with limitations | `sql/`, ADR 0009 |
| R-05 | Dataform is connected to GitHub and exposes two runnable workflows (`sales_pipeline`, `events_pipeline`) | `terraform/dataform.tf`, ADR 0004 |
| R-06 | Incremental behaviour is demonstrable (batch 2) and data-quality gating is demonstrable (bad batch) | `data/`, ADR 0006/0008 |
| R-07 | README explains the full demo end to end; `docs/demo-runbook.md` has a timed script | `README.md`, `docs/` |
| R-08 | Decisions documented as ADRs | `docs/adr/` |
| R-09 | No secrets in git; no service-account keys | `.gitignore`, ADR 0005 |

## Non-goals (MVP)
dbt comparison code, CI/CD, remote Terraform state, multiple environments, unit tests, dashboards, the slides.

## Acceptance criteria
| ID | Check | Expected |
|---|---|---|
| AC-01 | `make preflight` | all `[OK]` (after project + billing + bootstrap) |
| AC-02 | `make tf-apply` | creates 5 datasets, SA, secret, Dataform repo, release config, 2 workflow configs |
| AC-03 | `make load-1` | 5 tables in `raw` (700 / 80 / 4,037 / 7,533 / 12,292 rows) |
| AC-04 | Run `sales_pipeline` then `events_pipeline` in Dataform | all actions and assertions succeed; `analytics.fct_orders` has 4,037 rows |
| AC-05 | `make sql-run` | `plain_sql.*` built; `sql/compare_results.sql` returns 0 / 0 after both pipelines processed the same data |
| AC-06 | `make load-2`, re-run both pipelines | `fct_orders` = 6,186 rows; 127 previously pending orders changed status |
| AC-07 | `make load-bad`, re-run `sales_pipeline` | assertions fail; `fct_orders` and `mart_daily_sales` are skipped; `make sql-run` fails only at `12_checks.sql` after building bad data |
| AC-08 | `make tf-destroy` | datasets, Dataform repo, secret and SA are gone |

Expected row counts come from the offline emulation (ADR 0012); BigQuery must match them.

## Next steps (after MVP works)
Fix whatever the first real run reveals; add optional `dbt/` comparison folder; unit tests; `vars` and dev/prod
environments; CI running `dataform compile`; then the Quarto revealJS presentation.
