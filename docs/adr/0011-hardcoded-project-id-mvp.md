# 0011. Hardcoded project id for the MVP
- Status: Accepted
- Date: 2026-09-18

## Context
Dataform's `workflow_settings.yaml` cannot read environment variables, and the plain-SQL files must show
fully-qualified names.

## Decision
`encoders-sandbox-rodo` is written literally in `workflow_settings.yaml`, `sql/*.sql`, the default of
`src/dataform_demo/config.py` and `terraform/variables.tf`. `make set-project NEW_PROJECT=<id>` replaces it
everywhere. Everything else reads `GCP_PROJECT_ID` / Terraform variables.

## Consequences
+ Zero indirection for the audience. - Changing the project touches several files (one command).
- Future improvement: `vars`/`projectSuffix` in Dataform and environment separation.
