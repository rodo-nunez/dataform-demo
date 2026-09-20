-- Dataform equivalent: definitions/marts/dim_products.sqlx
CREATE OR REPLACE TABLE `encoders-sandbox-rodo.plain_sql.dim_products`
OPTIONS (description = 'Product dimension with margin, ready for BI.')
AS
SELECT
  product_id,
  product_name,
  category,
  unit_price,
  unit_cost,
  unit_margin,
  SAFE_DIVIDE(unit_margin, unit_price) AS margin_pct
FROM `encoders-sandbox-rodo.plain_sql.stg_products`;
