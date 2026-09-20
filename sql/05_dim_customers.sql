-- Dataform equivalent: definitions/marts/dim_customers.sqlx
--
-- LIMITATION: execution order is the file name. Nothing stops you from running this before
--             01_stg_customers.sql; you only find out when it fails (or worse, reads a stale view).
CREATE OR REPLACE TABLE `encoders-sandbox-rodo.plain_sql.dim_customers`
CLUSTER BY country_code
OPTIONS (description = 'Customer dimension, ready for BI.')
AS
SELECT
  customer_id,
  full_name,
  email,
  country_code,
  signup_date,
  DATE_TRUNC(signup_date, MONTH) AS signup_month,
  marketing_opt_in
FROM `encoders-sandbox-rodo.plain_sql.stg_customers`;
