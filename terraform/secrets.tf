# GitHub token so Dataform can pull the (public) repo. Stored in Secret Manager.
# NOTE: the value also ends up in the Terraform state (local, gitignored). Use a fine-grained,
# read-only token scoped to this one repository, and delete it when the demo is over.
resource "google_secret_manager_secret" "github_token" {
  project   = var.project_id
  secret_id = "dataform-github-token"
  labels    = var.labels

  replication {
    auto {}
  }

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret_version" "github_token" {
  secret      = google_secret_manager_secret.github_token.id
  secret_data = var.github_token
}

# The Dataform service agent (not the custom SA) reads the token for Git operations.
resource "google_secret_manager_secret_iam_member" "dataform_agent_reads_token" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.github_token.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_project_service_identity.dataform.email}"
}
