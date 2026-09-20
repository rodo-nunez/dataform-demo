-- Dataform equivalent: the `assertions:` blocks in every .sqlx plus
-- definitions/assertions/assert_orders_have_customers.sqlx.
--
-- LIMITATION: checks run AFTER everything was built. If one fails, the bad data is already in
--             fct_orders and mart_daily_sales. Nothing gates the downstream tables.
-- LIMITATION: they are hand-written ASSERT statements; the first failure aborts the script, so
--             you don't get a list of every violation, and nothing is recorded anywhere.

ASSERT (
  SELECT COUNT(*) FROM (
    SELECT order_id FROM `encoders-sandbox-rodo.plain_sql.stg_orders` GROUP BY order_id HAVING COUNT(*) > 1
  )
) = 0 AS 'stg_orders.order_id must be unique';

ASSERT (
  SELECT COUNT(*) FROM `encoders-sandbox-rodo.plain_sql.stg_order_items` WHERE quantity <= 0
) = 0 AS 'stg_order_items.quantity must be > 0';

ASSERT (
  SELECT COUNT(*)
  FROM `encoders-sandbox-rodo.plain_sql.stg_orders` AS o
  LEFT JOIN `encoders-sandbox-rodo.plain_sql.stg_customers` AS c ON o.customer_id = c.customer_id
  WHERE c.customer_id IS NULL
) = 0 AS 'every order must belong to a known customer';

ASSERT (
  SELECT COUNT(*) FROM `encoders-sandbox-rodo.plain_sql.fct_orders` WHERE net_revenue < 0
) = 0 AS 'fct_orders.net_revenue must be >= 0';

ASSERT (
  SELECT COUNT(*) FROM (
    SELECT order_id FROM `encoders-sandbox-rodo.plain_sql.fct_orders` GROUP BY order_id HAVING COUNT(*) > 1
  )
) = 0 AS 'fct_orders.order_id must be unique';
