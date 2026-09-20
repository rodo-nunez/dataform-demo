# 0003. Terraform scope, local state and easy teardown
- Status: Accepted
- Date: 2026-09-18

## Context
Infrastructure must be created with IaC and be trivial to destroy after the stream.

## Decision
Terraform (`terraform/`) manages: API enablement, 5 BigQuery datasets (`raw`, `staging`, `analytics`,
`dataform_assertions`, `plain_sql`), the Dataform service account and IAM, the Secret Manager secret with the
GitHub token, the Dataform repository, one release config and two workflow configs.
- **State is local** (gitignored). No remote backend for the MVP.
- Teardown flags: datasets use `delete_contents_on_destroy = true`; the Dataform repository uses
  `deletion_policy = "FORCE"`; APIs use `disable_on_destroy = false` (stay enabled).
- Providers: `google` and `google-beta`, both `~> 8.0`. Dataform resources and
  `google_project_service_identity` use `google-beta` (the latter is documented as beta-only).
- Tables inside `raw` are NOT Terraform-managed (see ADR 0007).
- `.terraform.lock.hcl` should be committed after the first `terraform init`.

## Consequences
+ `make tf-destroy` leaves only the project and enabled APIs.
- Local state contains the GitHub token (secret version). Keep it out of git, use a short-lived read-only token.
- No collaboration/locking: single operator.

## Alternatives considered
GCS backend (needs a bucket that itself must be bootstrapped); OpenTofu (works, `TF=tofu make ...`);
managing raw tables in Terraform (schema changes would need infra applies).
