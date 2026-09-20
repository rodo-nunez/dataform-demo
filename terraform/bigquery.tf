locals {
  datasets = {
    raw                 = "Landing zone. Tables are created by src/dataform_demo/load_data.py; not managed by Dataform."
    staging             = "Dataform staging views (cleaning and typing)."
    analytics           = "Dataform marts: dimensions, facts and aggregates."
    dataform_assertions = "Dataform assertion views (data quality checks)."
    plain_sql           = "Output of the plain-SQL version of the pipeline (sql/ folder), for side-by-side comparison."
  }
}

resource "google_bigquery_dataset" "this" {
  for_each = local.datasets

  project     = var.project_id
  dataset_id  = each.key
  location    = var.bq_location
  description = each.value
  labels      = var.labels

  # Makes `terraform destroy` remove the datasets even though they contain tables.
  delete_contents_on_destroy = true

  depends_on = [google_project_service.apis]
}
