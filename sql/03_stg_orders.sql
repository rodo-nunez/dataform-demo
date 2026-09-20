-- Dataform equivalent: definitions/staging/stg_orders.sqlx
CREATE OR REPLACE VIEW `encoders-sandbox-rodo.plain_sql.stg_orders`
OPTIONS (description = 'One row per order: the latest snapshot from the append-only raw log.')
AS
SELECT
  order_id,
  customer_id,
  order_ts,
  updated_at,
  LOWER(TRIM(status)) AS status,
  channel
FROM `encoders-sandbox-rodo.raw.orders`
QUALIFY ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC) = 1;
