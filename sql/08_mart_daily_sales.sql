-- Dataform equivalent: definitions/marts/mart_daily_sales.sqlx
--
-- LIMITATION: this runs even if fct_orders is full of bad data. Dataform's
--             `dependOnDependencyAssertions: true` blocks it; here nothing does.
CREATE OR REPLACE TABLE `encoders-sandbox-rodo.plain_sql.mart_daily_sales`
PARTITION BY order_date
CLUSTER BY country_code, channel
OPTIONS (description = 'Daily sales of completed orders by channel and customer country.')
AS
SELECT
  DATE(f.order_ts) AS order_date,
  f.channel,
  c.country_code,
  COUNT(*) AS orders_count,
  SUM(f.units) AS units_sold,
  SUM(f.gross_revenue) AS gross_revenue,
  SUM(f.discount_amount) AS discount_amount,
  SUM(f.net_revenue) AS net_revenue,
  ROUND(SAFE_DIVIDE(SUM(f.net_revenue), COUNT(*)), 2) AS avg_order_value
FROM `encoders-sandbox-rodo.plain_sql.fct_orders` AS f
JOIN `encoders-sandbox-rodo.plain_sql.dim_customers` AS c
  ON f.customer_id = c.customer_id
WHERE f.status = 'completed'
GROUP BY 1, 2, 3;

-- Post-operation, done by hand (Dataform: `post_operations { ... }`).
ALTER TABLE `encoders-sandbox-rodo.plain_sql.mart_daily_sales`
SET OPTIONS (labels = [("managed_by", "plain_sql"), ("layer", "mart")]);
