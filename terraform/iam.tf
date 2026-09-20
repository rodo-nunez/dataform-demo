data "google_project" "this" {
  project_id = var.project_id
}

# Service account that Dataform uses to run queries (least privilege, no keys).
resource "google_service_account" "dataform" {
  project      = var.project_id
  account_id   = "dataform-runner"
  display_name = "Dataform runner (demo)"

  depends_on = [google_project_service.apis]
}

# Creates the Dataform service agent (service-<project number>@gcp-sa-dataform...) if it does not
# exist yet. Without this, IAM bindings that reference it can fail on a fresh project.
resource "google_project_service_identity" "dataform" {
  provider = google-beta

  project = var.project_id
  service = "dataform.googleapis.com"

  depends_on = [google_project_service.apis]
}

# The Dataform service agent must be able to mint tokens for the custom service account.
resource "google_service_account_iam_member" "dataform_agent_token_creator" {
  service_account_id = google_service_account.dataform.name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "serviceAccount:${google_project_service_identity.dataform.email}"
}

# Run BigQuery jobs in the project.
resource "google_project_iam_member" "dataform_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.dataform.email}"
}

# Dataset-level access: read raw, write everywhere else.
locals {
  dataform_dataset_roles = {
    raw                 = "roles/bigquery.dataViewer"
    staging             = "roles/bigquery.dataEditor"
    analytics           = "roles/bigquery.dataEditor"
    dataform_assertions = "roles/bigquery.dataEditor"
  }
}

resource "google_bigquery_dataset_iam_member" "dataform" {
  for_each = local.dataform_dataset_roles

  project    = var.project_id
  dataset_id = google_bigquery_dataset.this[each.key].dataset_id
  role       = each.value
  member     = "serviceAccount:${google_service_account.dataform.email}"
}
