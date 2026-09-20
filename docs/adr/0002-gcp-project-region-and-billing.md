# 0002. GCP project, BigQuery location and billing prerequisite
- Status: Accepted
- Date: 2026-09-18

## Context
The demo runs in the author's personal GCP. The project `encoders-sandbox-rodo` was just created; nothing else
is configured and it is not known whether billing is linked.

## Decision
- The project **already exists** and is NOT created by Terraform (creating projects needs an org/folder and a
  billing account, and `terraform destroy` on a project is too destructive for a demo).
- **Billing must be linked** before `terraform apply`. `make preflight` checks it and prints the fix.
- BigQuery location: **`US`** multi-region (maximum feature support). Dataform repository region:
  `us-central1` (variable `dataform_region`).
- Only two APIs are enabled outside Terraform (`make bootstrap`): `serviceusage` and `cloudresourcemanager`,
  because Terraform needs them to enable the others.

## Consequences
+ Small blast radius: destroying the demo never touches the project itself.
- One manual prerequisite (billing) and one bootstrap command.
- `US` data cannot be joined with datasets in other locations without copying.

## Alternatives considered
Terraform-created project (needs billing account + org permissions); BigQuery sandbox without billing (Dataform,
Secret Manager and other APIs need billing; sandbox limits distort the demo); `southamerica-west1` for latency
(less certain feature parity).
