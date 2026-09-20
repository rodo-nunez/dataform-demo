// Programmatic table generation: one table per funnel step, from a single loop.
// In plain SQL this would be four copy-pasted files that drift apart over time.
constants.FUNNEL_STEPS.forEach((eventType) => {
  publish(`daily_${eventType}_events`, {
    type: "table",
    schema: "analytics",
    tags: ["events"],
    description: `Daily ${eventType} events and distinct sessions by device.`,
  }).query(
    (ctx) => `
      SELECT
        event_date,
        device,
        COUNT(*) AS events_count,
        COUNT(DISTINCT session_id) AS sessions_count
      FROM ${ctx.ref("stg_events")}
      WHERE event_type = '${eventType}'
      GROUP BY event_date, device
    `
  );
});
