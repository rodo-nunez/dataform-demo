output "dataform_service_account" {
  description = "Service account Dataform runs queries as."
  value       = google_service_account.dataform.email
}

output "dataform_repository" {
  description = "Dataform repository resource name."
  value       = google_dataform_repository.demo.id
}

output "dataform_console_url" {
  description = "Open Dataform in the Google Cloud console."
  value       = "https://console.cloud.google.com/bigquery/dataform?project=${var.project_id}"
}

output "datasets" {
  description = "BigQuery datasets created."
  value       = sort(keys(local.datasets))
}

output "workflow_configs" {
  description = "Workflow configs (the demo processes) and the tag each one runs."
  value       = local.workflows
}
