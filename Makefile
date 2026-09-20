# Convenience wrapper around the demo commands. Run `make help`.
# Variables are read from .env (KEY=value, NO quotes, NO `export`), see .env.example.

SHELL := /bin/bash
-include .env
export

GCP_PROJECT_ID ?= encoders-sandbox-rodo
TF             ?= terraform
TF_DIR         := terraform
DATAFORM_CLI   := npx --yes @dataform/cli@3.0.70

.DEFAULT_GOAL := help
.PHONY: help setup data auth bootstrap preflight preflight-post tf-init tf-plan tf-apply tf-destroy \
        load-1 load-2 load-bad sql-list sql-run dataform-compile set-project

help: ## Show this help
	@grep -E '^[a-zA-Z0-9_-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------- setup
setup: ## Install Python dependencies with uv
	uv sync

data: ## (Re)generate the sample CSVs in data/ (already committed)
	uv run dfdemo-generate

auth: ## Log in with gcloud and set Application Default Credentials
	gcloud auth login
	gcloud auth application-default login
	gcloud auth application-default set-quota-project $(GCP_PROJECT_ID)
	gcloud config set project $(GCP_PROJECT_ID)

bootstrap: ## Enable the two APIs Terraform needs before it can enable the rest
	gcloud services enable serviceusage.googleapis.com cloudresourcemanager.googleapis.com --project $(GCP_PROJECT_ID)

preflight: ## Check auth, project, billing and bootstrap APIs (run before terraform)
	uv run dfdemo-preflight

preflight-post: ## Check APIs and datasets (run after terraform apply)
	uv run dfdemo-preflight --post

# ---------------------------------------------------------------- infrastructure
tf-init: ## terraform init
	$(TF) -chdir=$(TF_DIR) init

tf-plan: ## terraform plan
	$(TF) -chdir=$(TF_DIR) plan

tf-apply: ## terraform apply (needs TF_VAR_github_token and terraform.tfvars)
	$(TF) -chdir=$(TF_DIR) apply

tf-destroy: ## terraform destroy: removes everything Terraform created (datasets, Dataform, secret, SA)
	$(TF) -chdir=$(TF_DIR) destroy

# ---------------------------------------------------------------- data
load-1: ## Load batch 1 into BigQuery raw (TRUNCATES raw tables first)
	uv run dfdemo-load --batch 1

load-2: ## Load batch 2 (new data + status changes), appends
	uv run dfdemo-load --batch 2

load-bad: ## Load the broken batch to make assertions fail, appends
	uv run dfdemo-load --batch bad

# ---------------------------------------------------------------- pipelines
sql-list: ## Show the plain-SQL files in execution order
	uv run dfdemo-run-sql --list

sql-run: ## Run the plain-SQL pipeline (writes to dataset plain_sql)
	uv run dfdemo-run-sql

dataform-compile: ## Compile the Dataform project locally (no GCP access needed, needs Node.js)
	$(DATAFORM_CLI) compile

set-project: ## Change the hardcoded project id: make set-project NEW_PROJECT=my-project
	@test -n "$(NEW_PROJECT)" || (echo "Usage: make set-project NEW_PROJECT=<project-id>"; exit 1)
	sed -i.bak 's/encoders-sandbox-rodo/$(NEW_PROJECT)/g' workflow_settings.yaml sql/*.sql \
	  src/dataform_demo/config.py terraform/variables.tf terraform/terraform.tfvars.example .env.example Makefile
	find . -name '*.bak' -not -path './.venv/*' -delete
	@echo "Project id replaced. Also update GCP_PROJECT_ID in your .env / terraform.tfvars."
