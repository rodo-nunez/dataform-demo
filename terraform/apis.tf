locals {
  required_apis = [
    "serviceusage.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "bigquery.googleapis.com",
    "dataform.googleapis.com",
    "secretmanager.googleapis.com",
  ]
}

resource "google_project_service" "apis" {
  for_each = toset(local.required_apis)

  project = var.project_id
  service = each.value

  # Keep APIs enabled on destroy: disabling them is slow, can fail on dependencies, and a
  # subsequent `terraform apply` would have to wait for them again.
  disable_on_destroy = false
}
