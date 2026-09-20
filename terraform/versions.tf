terraform {
  required_version = ">= 1.6.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 8.0"
    }
    # google-beta is used for the Dataform resources and the service identity (see ADR 0003).
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 8.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.dataform_region

  # Bill API usage / quota to the demo project instead of the (gcloud) client project.
  user_project_override = true
  billing_project       = var.project_id
}

provider "google-beta" {
  project = var.project_id
  region  = var.dataform_region

  user_project_override = true
  billing_project       = var.project_id
}
