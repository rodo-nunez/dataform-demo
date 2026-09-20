resource "google_dataform_repository" "demo" {
  provider = google-beta

  project      = var.project_id
  region       = var.dataform_region
  name         = var.dataform_repository_name
  display_name = "Dataform demo (en_coders)"
  labels       = var.labels

  service_account = google_service_account.dataform.email

  # Lets `terraform destroy` delete the repository even if it contains workspaces, releases, etc.
  deletion_policy = "FORCE"

  git_remote_settings {
    url                                 = var.github_repo_url
    default_branch                      = var.github_default_branch
    authentication_token_secret_version = google_secret_manager_secret_version.github_token.id
  }

  workspace_compilation_overrides {
    default_database = var.project_id
  }

  depends_on = [
    google_service_account_iam_member.dataform_agent_token_creator,
    google_secret_manager_secret_iam_member.dataform_agent_reads_token,
    google_project_iam_member.dataform_job_user,
    google_bigquery_dataset_iam_member.dataform,
  ]
}

# Compiles the repo (branch tracked in var.github_default_branch) on a schedule.
resource "google_dataform_repository_release_config" "production" {
  provider = google-beta

  project    = var.project_id
  region     = var.dataform_region
  repository = google_dataform_repository.demo.name

  name          = "production"
  git_commitish = var.github_default_branch
  cron_schedule = var.release_cron_schedule
  time_zone     = var.workflow_time_zone
}

# The two demo processes. Each one runs every action tagged with its tag (see definitions/).
locals {
  workflows = {
    sales_pipeline  = "sales"
    events_pipeline = "events"
  }
}

resource "google_dataform_repository_workflow_config" "this" {
  for_each = local.workflows
  provider = google-beta

  project        = var.project_id
  region         = var.dataform_region
  repository     = google_dataform_repository.demo.name
  name           = each.key
  release_config = google_dataform_repository_release_config.production.id

  cron_schedule = var.workflow_cron_schedule == "" ? null : var.workflow_cron_schedule
  time_zone     = var.workflow_time_zone

  invocation_config {
    included_tags   = [each.value]
    service_account = google_service_account.dataform.email
  }
}
