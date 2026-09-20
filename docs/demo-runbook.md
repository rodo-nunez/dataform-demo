# Demo runbook (second 45 minutes)

Pre-flight the day before: repo pushed to GitHub, PAT created, `make preflight` green, ideally a full dry
rehearsal. If `terraform apply` is slow on stream, pre-provision and only show `terraform plan` + the files.

| Time | Segment | What to do / show |
|---|---|---|
| 0-5 | Recap and map | Repo tour: `terraform/`, `data/`, `definitions/`, `sql/`. Show the architecture diagram in the README. |
| 5-12 | Infrastructure | `make tf-plan`, read the plan (datasets, SA, IAM, secret, Dataform). `make tf-apply` (or show pre-provisioned outputs). Open the Dataform console. |
| 12-17 | Data | `make load-1`. In BigQuery show `raw.*` and the messy emails/countries. |
| 17-27 | Dataform run #1 | Console: release config `production` -> workflow `sales_pipeline` -> start execution. Show the DAG, compiled SQL, the assertions dataset. Then `events_pipeline`. Show generated tables and funnel columns (`includes/`). |
| 27-32 | Plain SQL | `make sql-list`, `make sql-run`. Read two `-- LIMITATION:` comments. Run `sql/compare_results.sql` in the console: 0 / 0. |
| 32-38 | Incremental | `make load-2`. Re-run `sales_pipeline`. Show bytes processed and the MERGE in the run log; pending orders now completed. Re-run `make sql-run` and compare with the hand-written MERGE. |
| 38-43 | Bad data | `make load-bad`. Re-run `sales_pipeline`: assertions fail, `fct_orders` / `mart_daily_sales` skipped. `make sql-run`: bad rows are already in `plain_sql.fct_orders` before `12_checks.sql` fails. |
| 43-45 | Teardown | `make tf-destroy`. Revoke the GitHub PAT. Mention costs (cents). |

Reset between rehearsals: `make load-1` truncates raw; then re-run the pipelines (use "full refresh" for the
incremental table in Dataform, and `DROP TABLE plain_sql.fct_orders` for the plain-SQL side).

Backup plan: `make dataform-compile` locally to show the compiled graph if the console misbehaves.
