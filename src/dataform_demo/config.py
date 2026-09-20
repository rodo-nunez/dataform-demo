"""Central configuration. Everything can be overridden with environment variables."""

from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
SQL_DIR = REPO_ROOT / "sql"

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "encoders-sandbox-rodo")
BQ_LOCATION = os.environ.get("BQ_LOCATION", "US")
RAW_DATASET = os.environ.get("RAW_DATASET", "raw")
