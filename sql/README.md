# Plain-SQL version of the pipeline

The same transformations as the Dataform project, written as vanilla BigQuery SQL, to show what you give up
without Dataform. Run with `make sql-run`; results land in the `plain_sql` dataset. Each file starts with a
`-- Dataform equivalent:` comment and lists the `-- LIMITATION:` it illustrates.

| Plain SQL file | Dataform equivalent | What Dataform adds |
|---|---|---|
| `01`-`04_stg_*.sql` | `definitions/staging/*.sqlx` | `ref()` instead of hardcoded names, column docs, built-in assertions |
| `05`-`06_dim_*.sql` | `definitions/marts/dim_*.sqlx` | Automatic dependency order (here: the file name) |
| `07_fct_orders.sql` | `definitions/marts/fct_orders.sqlx` | `type: "incremental"` generates the DDL and MERGE for you |
| `08_mart_daily_sales.sql` | `definitions/marts/mart_daily_sales.sqlx` | `dependOnDependencyAssertions` gates bad data; `post_operations` |
| `09_stg_events.sql` | `definitions/staging/stg_events.sqlx` | |
| `10_mart_event_funnel.sql` | `definitions/events/mart_event_funnel.sqlx` | JavaScript templating from `includes/` |
| `11_daily_event_tables.sql` | `definitions/events/daily_event_tables.js` | Generate N tables from one loop |
| `12_checks.sql` | `assertions:` blocks + `definitions/assertions/` | Assertions as first-class, tracked, gating actions |
| `compare_results.sql` | n/a | Run manually: proves both pipelines give the same numbers |

The runner (`src/dataform_demo/run_sql.py`) just executes the numbered files in filename order.
