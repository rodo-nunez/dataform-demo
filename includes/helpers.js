// SQL-generating helpers. Available in .sqlx / .js definitions as `helpers`.

// COUNT(DISTINCT IF(event_type = 'x', session_id, NULL)) AS x_sessions, one line per step.
function sessionsByStep(steps) {
  return steps
    .map((step) => `COUNT(DISTINCT IF(event_type = '${step}', session_id, NULL)) AS ${step}_sessions`)
    .join(",\n    ");
}

// Step-to-step conversion: add_to_cart_sessions / page_view_sessions, and so on.
function conversionRates(steps) {
  return steps
    .slice(1)
    .map((step, index) => {
      const previous = steps[index];
      return `SAFE_DIVIDE(${step}_sessions, ${previous}_sessions) AS ${previous}_to_${step}_rate`;
    })
    .join(",\n    ");
}

module.exports = { sessionsByStep, conversionRates };
