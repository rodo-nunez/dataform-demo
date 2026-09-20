"""Run the plain-SQL version of the pipeline (the ``sql/NN_*.sql`` files) in order.

This runner is intentionally dumb: it sorts files by name and executes them one by one.
Everything Dataform gives you for free (dependency graph, retries, assertions gating,
incremental logic, environments) is missing here on purpose. That is the point of the demo.

Usage:
    uv run dfdemo-run-sql                 # run everything in order
    uv run dfdemo-run-sql --list          # show the files and their order
    uv run dfdemo-run-sql --only 07 09    # run only files whose name starts with 07 or 09
"""

from __future__ import annotations

import argparse
import sys
import time

from dataform_demo.config import BQ_LOCATION, PROJECT_ID, SQL_DIR


def discover(only: list[str] | None):
    files = sorted(SQL_DIR.glob("[0-9][0-9]_*.sql"))
    if only:
        files = [f for f in files if any(f.name.startswith(prefix) for prefix in only)]
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--list", action="store_true", help="List the SQL files in execution order and exit.")
    parser.add_argument("--only", nargs="+", metavar="PREFIX", help="Only run files starting with these prefixes.")
    args = parser.parse_args()

    files = discover(args.only)
    if not files:
        sys.exit(f"No SQL files found in {SQL_DIR}")

    if args.list:
        for file in files:
            print(file.name)
        return

    from google.cloud import bigquery

    client = bigquery.Client(project=PROJECT_ID, location=BQ_LOCATION)
    for file in files:
        started = time.time()
        print(f"> {file.name} ...", end=" ", flush=True)
        job = client.query(file.read_text(encoding="utf-8"))
        try:
            job.result()
        except Exception as error:  # noqa: BLE001 - we want to show BigQuery's message and stop
            print("FAILED")
            print(f"  {error}")
            sys.exit(1)
        processed = (job.total_bytes_processed or 0) / 1e6
        print(f"ok ({time.time() - started:.1f}s, {processed:,.1f} MB processed)")


if __name__ == "__main__":
    main()
