variable "project_id" {
  description = "GCP project that hosts the demo. It must already exist and have billing enabled (see README)."
  type        = string
  default     = "encoders-sandbox-rodo"
}

variable "bq_location" {
  description = "BigQuery dataset location."
  type        = string
  default     = "US"
}

variable "dataform_region" {
  description = "Region of the Dataform repository (also used as the provider default region)."
  type        = string
  default     = "us-central1"
}

variable "dataform_repository_name" {
  description = "Name of the Dataform repository created in GCP."
  type        = string
  default     = "dataform-demo"
}

variable "github_repo_url" {
  description = "HTTPS URL of the GitHub repo that holds this project, e.g. https://github.com/<user>/dataform-demo.git"
  type        = string
}

variable "github_default_branch" {
  description = "Branch Dataform tracks."
  type        = string
  default     = "main"
}

variable "github_token" {
  description = "GitHub personal access token Dataform uses to read the repo. Pass it with TF_VAR_github_token; never commit it."
  type        = string
  sensitive   = true
}

variable "release_cron_schedule" {
  description = "How often the release config compiles the repo (cron). Hourly by default so a compilation result exists soon after apply."
  type        = string
  default     = "0 * * * *"
}

variable "workflow_cron_schedule" {
  description = "Cron schedule for the two workflow configs. Empty string = no schedule (run them manually from the console)."
  type        = string
  default     = ""
}

variable "workflow_time_zone" {
  description = "Time zone used to interpret the cron schedules."
  type        = string
  default     = "America/Santiago"
}

variable "labels" {
  description = "Labels applied to resources that support them."
  type        = map(string)
  default = {
    project = "dataform-demo"
    owner   = "en-coders"
  }
}
