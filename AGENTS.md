# AGENTS.md

Guidance for AI coding agents working in this repo. Read `docs/spec.md` and `docs/adr/` first.

## What this is
Demo repo for a stream about Dataform: Terraform (GCP), Python/uv data loader, Dataform project, plain-SQL twin.

## Layout
- `workflow_settings.yaml`, `definitions/`, `includes/`: Dataform project (must stay at repo root, ADR 0004).
- `terraform/`: infrastructure. `src/dataform_demo/`: Python. `sql/`: plain-SQL twin. `data/`: committed CSVs.
- `docs/`: spec, ADRs, demo runbook.

## Commands
`make help` lists everything. Key ones: `uv sync`, `uv run dfdemo-generate`, `uv run dfdemo-load --batch 1 --dry-run`,
`make dataform-compile`, `tofu fmt -check -recursive terraform` (or `terraform fmt`).

## Rules
- Keep everything in English (ADR 0010). Add or supersede an ADR for any real decision change.
- Any Dataform change needs a matching change in `sql/` (and vice versa) so outputs stay equal; `sql/README.md` maps them.
- Do not commit secrets, tfstate, tfvars, or service-account keys. Never add JSON credentials.
- Never weaken `deletion`/teardown settings; `make tf-destroy` must stay clean.
- Batches: every `updated_at` in a later batch must be strictly greater than all earlier ones (incremental watermark).
- Nothing here has run on real GCP yet: see ADR 0012 for what is verified. Do not claim otherwise.
