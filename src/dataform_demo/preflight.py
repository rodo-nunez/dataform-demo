"""Sanity checks before (and after) `terraform apply`.

Before Terraform (default): gcloud installed, Application Default Credentials, the project exists,
billing is enabled, and the two bootstrap APIs Terraform needs are on.
After Terraform (--post): the Terraform-managed APIs are on and the BigQuery datasets exist.

Usage:
    uv run dfdemo-preflight
    uv run dfdemo-preflight --post
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys

from dataform_demo.config import PROJECT_ID

BOOTSTRAP_APIS = ["serviceusage.googleapis.com", "cloudresourcemanager.googleapis.com"]
TERRAFORM_APIS = [
    "bigquery.googleapis.com",
    "dataform.googleapis.com",
    "secretmanager.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
]
DATASETS = ["raw", "staging", "analytics", "dataform_assertions", "plain_sql"]

results: list[bool] = []


def report(ok: bool, label: str, hint: str = "") -> None:
    results.append(ok)
    print(f"[{'OK' if ok else 'FAIL'}] {label}")
    if not ok and hint:
        print(f"       -> {hint}")


def gcloud(*args: str) -> tuple[bool, str]:
    completed = subprocess.run(["gcloud", *args], capture_output=True, text=True)
    return completed.returncode == 0, completed.stdout.strip()


def enabled_apis() -> set[str]:
    ok, out = gcloud("services", "list", "--enabled", "--project", PROJECT_ID, "--format=value(config.name)")
    return set(out.split()) if ok else set()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--post", action="store_true", help="Check the state AFTER terraform apply.")
    args = parser.parse_args()

    print(f"Project: {PROJECT_ID}\n")

    if shutil.which("gcloud") is None:
        report(False, "gcloud CLI installed", "Install it: https://cloud.google.com/sdk/docs/install")
        sys.exit(1)
    report(True, "gcloud CLI installed")

    try:
        import google.auth

        google.auth.default()
        report(True, "Application Default Credentials found")
    except Exception:  # noqa: BLE001
        report(False, "Application Default Credentials found", "Run: gcloud auth application-default login")

    ok, _ = gcloud("projects", "describe", PROJECT_ID, "--format=value(projectId)")
    report(ok, f"Project '{PROJECT_ID}' exists and is accessible", "Create it in the console or check the ID / your account.")

    ok, out = gcloud("billing", "projects", "describe", PROJECT_ID, "--format=value(billingEnabled)")
    report(ok and out.lower() == "true", "Billing is enabled on the project",
           "List accounts: gcloud billing accounts list; link: gcloud billing projects link "
           f"{PROJECT_ID} --billing-account=<ID>")

    apis = enabled_apis()
    wanted = TERRAFORM_APIS if args.post else BOOTSTRAP_APIS
    for api in wanted:
        report(api in apis, f"API enabled: {api}",
               "Run: make bootstrap" if not args.post else "Run: terraform apply")

    if args.post:
        from google.cloud import bigquery

        try:
            client = bigquery.Client(project=PROJECT_ID)
            existing = {d.dataset_id for d in client.list_datasets()}
        except Exception as error:  # noqa: BLE001
            existing = set()
            print(f"       (could not list datasets: {error})")
        for dataset in DATASETS:
            report(dataset in existing, f"BigQuery dataset exists: {dataset}", "Run: terraform apply")

    print()
    if all(results):
        print("All checks passed.")
    else:
        print("Some checks failed. Fix them before continuing.")
        sys.exit(1)


if __name__ == "__main__":
    main()
