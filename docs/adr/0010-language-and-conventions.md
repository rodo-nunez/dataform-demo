# 0010. Everything in English; repo conventions
- Status: Accepted
- Date: 2026-09-18

## Decision
README, ADRs, comments, code identifiers, SQL and column names are in English. The stream and slides may be
in Spanish; this repo is not. Conventions: `stg_` (staging views), `dim_`, `fct_`, `mart_`; snake_case; one
model per file; Dataform tags `sales` / `events` map 1:1 to workflow configs; docs in Markdown; Python >= 3.11
with type hints; no secrets in git.

## Consequences
+ Consistent for tooling and AI agents. - Spoken explanations on stream need to translate on the fly.
