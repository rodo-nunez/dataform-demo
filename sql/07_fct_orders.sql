-- Dataform equivalent: definitions/marts/fct_orders.sqlx  (type: "incremental")
--
-- In Dataform this whole file is: `type: "incremental"`, `uniqueKey: ["order_id"]`, one SELECT,
-- and a `${when(incremental(), ...)}` filter. Dataform generates the CREATE / MERGE for you.
--
-- LIMITATION: you write the DDL by hand, with every column and its type.
-- LIMITATION: you write the MERGE by hand, including every column in UPDATE SET. Add a column
--             to the SELECT and you must remember to change the DDL AND the MERGE.
-- LIMITATION: "full refresh" is a manual DROP TABLE.

CREATE TABLE IF NOT EXISTS `encoders-sandbox-rodo.plain_sql.fct_orders` (
  order_id INT64,
  customer_id INT64,
  order_ts TIMESTAMP,
  updated_at TIMESTAMP,
  status STRING,
  channel STRING,
  items_count INT64,
  units INT64,
  gross_revenue NUMERIC,
  discount_amount NUMERIC,
  net_revenue NUMERIC
)
PARTITION BY DATE(order_ts)
CLUSTER BY channel, status;

MERGE `encoders-sandbox-rodo.plain_sql.fct_orders` AS target
USING (
  WITH order_totals AS (
    SELECT
      order_id,
      COUNT(*) AS items_count,
      SUM(quantity) AS units,
      SUM(gross_amount) AS gross_revenue,
      SUM(discount_amount) AS discount_amount,
      SUM(net_amount) AS net_revenue
    FROM `encoders-sandbox-rodo.plain_sql.stg_order_items`
    GROUP BY order_id
  )
  SELECT
    o.order_id,
    o.customer_id,
    o.order_ts,
    o.updated_at,
    o.status,
    o.channel,
    IFNULL(t.items_count, 0) AS items_count,
    IFNULL(t.units, 0) AS units,
    IFNULL(t.gross_revenue, 0) AS gross_revenue,
    IFNULL(t.discount_amount, 0) AS discount_amount,
    IFNULL(t.net_revenue, 0) AS net_revenue
  FROM `encoders-sandbox-rodo.plain_sql.stg_orders` AS o
  LEFT JOIN order_totals AS t
    ON o.order_id = t.order_id
  WHERE o.updated_at > (
    SELECT IFNULL(MAX(updated_at), TIMESTAMP '1970-01-01 00:00:00+00')
    FROM `encoders-sandbox-rodo.plain_sql.fct_orders`
  )
) AS source
ON target.order_id = source.order_id
WHEN MATCHED THEN UPDATE SET
  customer_id = source.customer_id,
  order_ts = source.order_ts,
  updated_at = source.updated_at,
  status = source.status,
  channel = source.channel,
  items_count = source.items_count,
  units = source.units,
  gross_revenue = source.gross_revenue,
  discount_amount = source.discount_amount,
  net_revenue = source.net_revenue
WHEN NOT MATCHED THEN INSERT ROW;
