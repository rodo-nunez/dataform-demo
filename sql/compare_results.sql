-- Not part of the numbered pipeline (the runner ignores it). Run it in the BigQuery console after
-- BOTH pipelines have run, to prove that Dataform and plain SQL produce the same numbers.
-- Both counts should be 0.
SELECT
  (SELECT COUNT(*) FROM (
     SELECT * FROM `encoders-sandbox-rodo.analytics.mart_daily_sales`
     EXCEPT DISTINCT
     SELECT * FROM `encoders-sandbox-rodo.plain_sql.mart_daily_sales`)) AS rows_only_in_dataform,
  (SELECT COUNT(*) FROM (
     SELECT * FROM `encoders-sandbox-rodo.plain_sql.mart_daily_sales`
     EXCEPT DISTINCT
     SELECT * FROM `encoders-sandbox-rodo.analytics.mart_daily_sales`)) AS rows_only_in_plain_sql;
