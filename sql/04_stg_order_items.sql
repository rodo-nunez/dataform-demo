-- Dataform equivalent: definitions/staging/stg_order_items.sqlx
CREATE OR REPLACE VIEW `encoders-sandbox-rodo.plain_sql.stg_order_items`
OPTIONS (description = 'Order lines with gross, discount and net amounts.')
AS
SELECT
  order_item_id,
  order_id,
  product_id,
  quantity,
  unit_price,
  discount_pct,
  quantity * unit_price AS gross_amount,
  ROUND(quantity * unit_price * discount_pct, 2) AS discount_amount,
  quantity * unit_price - ROUND(quantity * unit_price * discount_pct, 2) AS net_amount
FROM `encoders-sandbox-rodo.raw.order_items`;
