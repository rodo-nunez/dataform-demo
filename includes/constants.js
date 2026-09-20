// Shared constants. Every file in includes/ is available as a global named after the file
// (this one is `constants`), both in .sqlx and in .js definitions.

// Ordered steps of the purchase funnel. Adding a step here changes the funnel mart AND
// generates one more daily table. No copy-paste.
const FUNNEL_STEPS = ["page_view", "add_to_cart", "begin_checkout", "purchase"];

module.exports = { FUNNEL_STEPS };
