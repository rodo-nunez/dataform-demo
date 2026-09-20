-- Dataform equivalent: definitions/events/daily_event_tables.js (a 15-line loop over FUNNEL_STEPS).
--
-- LIMITATION: the same statement copy-pasted once per event type. Fix a bug in one copy and
--             the other three silently keep the bug.
CREATE OR REPLACE TABLE `encoders-sandbox-rodo.plain_sql.daily_page_view_events` AS
SELECT event_date, device, COUNT(*) AS events_count, COUNT(DISTINCT session_id) AS sessions_count
FROM `encoders-sandbox-rodo.plain_sql.stg_events`
WHERE event_type = 'page_view'
GROUP BY event_date, device;

CREATE OR REPLACE TABLE `encoders-sandbox-rodo.plain_sql.daily_add_to_cart_events` AS
SELECT event_date, device, COUNT(*) AS events_count, COUNT(DISTINCT session_id) AS sessions_count
FROM `encoders-sandbox-rodo.plain_sql.stg_events`
WHERE event_type = 'add_to_cart'
GROUP BY event_date, device;

CREATE OR REPLACE TABLE `encoders-sandbox-rodo.plain_sql.daily_begin_checkout_events` AS
SELECT event_date, device, COUNT(*) AS events_count, COUNT(DISTINCT session_id) AS sessions_count
FROM `encoders-sandbox-rodo.plain_sql.stg_events`
WHERE event_type = 'begin_checkout'
GROUP BY event_date, device;

CREATE OR REPLACE TABLE `encoders-sandbox-rodo.plain_sql.daily_purchase_events` AS
SELECT event_date, device, COUNT(*) AS events_count, COUNT(DISTINCT session_id) AS sessions_count
FROM `encoders-sandbox-rodo.plain_sql.stg_events`
WHERE event_type = 'purchase'
GROUP BY event_date, device;
