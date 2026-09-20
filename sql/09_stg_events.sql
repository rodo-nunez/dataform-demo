-- Dataform equivalent: definitions/staging/stg_events.sqlx
CREATE OR REPLACE VIEW `encoders-sandbox-rodo.plain_sql.stg_events`
OPTIONS (description = 'Clickstream events with normalised event_type / device and a derived event_date.')
AS
SELECT
  event_id,
  customer_id,
  session_id,
  event_ts,
  DATE(event_ts) AS event_date,
  LOWER(TRIM(event_type)) AS event_type,
  LOWER(TRIM(device)) AS device
FROM `encoders-sandbox-rodo.raw.events`;
