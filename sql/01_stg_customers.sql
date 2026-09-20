-- Dataform equivalent: definitions/staging/stg_customers.sqlx
--
-- LIMITATION: table names are hardcoded (`project.dataset.table`). No ref(): moving to another
--             project, or adding a dev/prod split, means find-and-replace across every file.
-- LIMITATION: column descriptions would need one extra ALTER COLUMN ... SET OPTIONS statement each.
CREATE OR REPLACE VIEW `encoders-sandbox-rodo.plain_sql.stg_customers`
OPTIONS (description = 'Cleaned customers: trimmed and lower-cased email, upper-cased country code, proper-cased names.')
AS
SELECT
  customer_id,
  INITCAP(TRIM(first_name)) AS first_name,
  INITCAP(TRIM(last_name)) AS last_name,
  CONCAT(INITCAP(TRIM(first_name)), ' ', INITCAP(TRIM(last_name))) AS full_name,
  LOWER(TRIM(email)) AS email,
  UPPER(TRIM(country)) AS country_code,
  signup_date,
  marketing_opt_in
FROM `encoders-sandbox-rodo.raw.customers`;
