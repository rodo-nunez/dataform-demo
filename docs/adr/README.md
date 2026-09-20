# Architecture Decision Records

Each file records one decision: context, what was decided, consequences and alternatives. They are written
so a person or an AI agent can rebuild or extend the repo without re-litigating choices
(see also `../spec.md` and `../../AGENTS.md`).

| # | Decision | Status |
|---|---|---|
| [0001](0001-record-architecture-decisions.md) | Record decisions as ADRs | Accepted |
| [0002](0002-gcp-project-region-and-billing.md) | GCP project, BigQuery location and billing prerequisite | Accepted |
| [0003](0003-terraform-scope-state-and-teardown.md) | Terraform scope, local state, easy teardown | Accepted |
| [0004](0004-dataform-git-integration-github.md) | Dataform connected to a public GitHub repo; project at repo root | Accepted |
| [0005](0005-service-accounts-and-iam.md) | Authentication and IAM model | Accepted |
| [0006](0006-synthetic-ecommerce-dataset-and-batches.md) | Synthetic e-commerce dataset delivered in batches | Accepted |
| [0007](0007-python-uv-data-loading.md) | Python + uv for data generation and loading | Accepted |
| [0008](0008-dataform-pipeline-design.md) | Dataform pipeline design and features covered | Accepted |
| [0009](0009-plain-sql-equivalent.md) | Plain-SQL equivalent of the pipeline | Accepted |
| [0010](0010-language-and-conventions.md) | Everything in English; repo conventions | Accepted |
| [0011](0011-hardcoded-project-id-mvp.md) | Hardcoded project id for the MVP | Accepted |
| [0012](0012-validation-and-known-gaps.md) | How this was validated and what is NOT verified | Accepted |

## Template

```markdown
# NNNN. Title
- Status: Proposed | Accepted | Superseded by NNNN
- Date: YYYY-MM-DD

## Context
## Decision
## Consequences
## Alternatives considered
```
