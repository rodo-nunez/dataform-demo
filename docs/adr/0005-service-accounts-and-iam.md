# 0005. Authentication and IAM model
- Status: Accepted
- Date: 2026-09-18

## Context
Avoid long-lived keys; keep permissions small but simple to reason about on stage.

## Decision
- Humans and local scripts: **Application Default Credentials** (`gcloud auth application-default login`);
  no JSON keys anywhere. The gitignore blocks `*credentials*.json` as a safety net.
- Dataform runs as a dedicated service account `dataform-runner`, set on the repository and on workflow
  invocations.
- Roles for `dataform-runner`: `roles/bigquery.jobUser` (project); `bigquery.dataViewer` on `raw`;
  `bigquery.dataEditor` on `staging`, `analytics`, `dataform_assertions`.
- The Dataform service agent gets `roles/iam.serviceAccountTokenCreator` on `dataform-runner` and
  `roles/secretmanager.secretAccessor` on the GitHub token secret. The agent is created explicitly with
  `google_project_service_identity`.
- The person running Terraform is the project owner.

## Consequences
+ Dataform cannot write to `raw`. No keys to leak.
- Dataset-level grants mean new datasets used by Dataform need a new IAM entry in `terraform/iam.tf`.

## Alternatives considered
Default Dataform service agent (broader, less explicit); project-level `dataEditor` (simpler, too broad);
service account keys (avoidable risk).
