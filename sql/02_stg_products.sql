-- Dataform equivalent: definitions/staging/stg_products.sqlx
CREATE OR REPLACE VIEW `encoders-sandbox-rodo.plain_sql.stg_products`
OPTIONS (description = 'Products with unit margin.')
AS
SELECT
  product_id,
  TRIM(product_name) AS product_name,
  category,
  unit_price,
  unit_cost,
  unit_price - unit_cost AS unit_margin
FROM `encoders-sandbox-rodo.raw.products`;
