-- Dataform equivalent: definitions/events/mart_event_funnel.sqlx
--
-- LIMITATION: no JavaScript templating. Every funnel step is copy-pasted, by hand, twice
--             (sessions and rates). Add a step to the funnel and you edit both lists.
CREATE OR REPLACE TABLE `encoders-sandbox-rodo.plain_sql.mart_event_funnel`
PARTITION BY event_date
OPTIONS (description = 'Daily purchase funnel by device.')
AS
WITH sessions AS (
  SELECT
    event_date,
    device,
    COUNT(DISTINCT IF(event_type = 'page_view', session_id, NULL)) AS page_view_sessions,
    COUNT(DISTINCT IF(event_type = 'add_to_cart', session_id, NULL)) AS add_to_cart_sessions,
    COUNT(DISTINCT IF(event_type = 'begin_checkout', session_id, NULL)) AS begin_checkout_sessions,
    COUNT(DISTINCT IF(event_type = 'purchase', session_id, NULL)) AS purchase_sessions
  FROM `encoders-sandbox-rodo.plain_sql.stg_events`
  GROUP BY event_date, device
)
SELECT
  *,
  SAFE_DIVIDE(add_to_cart_sessions, page_view_sessions) AS page_view_to_add_to_cart_rate,
  SAFE_DIVIDE(begin_checkout_sessions, add_to_cart_sessions) AS add_to_cart_to_begin_checkout_rate,
  SAFE_DIVIDE(purchase_sessions, begin_checkout_sessions) AS begin_checkout_to_purchase_rate
FROM sessions;
