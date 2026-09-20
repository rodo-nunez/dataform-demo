# 0004. Dataform connected to a public GitHub repo; project at repo root
- Status: Accepted
- Date: 2026-09-18

## Context
The author wants a realistic setup, not code pasted into the console. Terraform should create the Dataform
repository already linked to Git and with schedulable workflows.

## Decision
- Dataform repository links to a **public GitHub repo** (this one) over HTTPS, branch `main`.
- Authentication uses a **GitHub personal access token (PAT)** stored in Secret Manager
  (`dataform-github-token`), passed to Terraform via `TF_VAR_github_token`. Read-only, fine-grained, scoped to
  this repo, short expiry. Even for public repos Dataform's HTTPS integration expects a token.
- The Dataform project (`workflow_settings.yaml`, `definitions/`, `includes/`) lives at the **repository root**
  because Dataform's Git integration reads the project from the root of the remote and has no subdirectory
  option. Terraform, Python, SQL and docs live next to it; Dataform ignores them.
- One release config (`production`, tracks `main`, compiles hourly) and two workflow configs:
  `sales_pipeline` (tag `sales`) and `events_pipeline` (tag `events`) = the "one or two processes".
  Workflow schedules are off by default (`workflow_cron_schedule = ""`), runs are triggered manually.
- `dataformCoreVersion` is pinned in `workflow_settings.yaml` (currently 3.0.70). If the Dataform console
  rejects it, set the version it suggests.

## Consequences
+ Same flow as production teams: commit, push, release config compiles, workflow runs.
- The repo must be pushed to GitHub before Dataform can compile it.
- A PAT exists in state and Secret Manager; must be revoked after the demo.

## Alternatives considered
Dataform workspace without Git (code lives only in GCP); separate repo just for Dataform (two repos to demo);
SSH key or Developer Connect (more setup, no benefit here); local `dataform run` only (does not show the
managed service).
