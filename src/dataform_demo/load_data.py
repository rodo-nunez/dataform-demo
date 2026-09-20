"""Load the sample CSVs into the BigQuery ``raw`` dataset.

Batches (see ``generate_data.py``):

* ``1``   -- initial load. TRUNCATES the raw tables first, so it is safe to re-run the whole demo.
* ``2``   -- August data + status changes for batch-1 orders. APPENDS.
* ``bad`` -- a few broken rows to make Dataform assertions fail. APPENDS.

Tables are created by this script with explicit schemas (no autodetect). Terraform only creates
the (empty) datasets: raw data is data, not infrastructure.

Usage:
    uv run dfdemo-load --batch 1
    uv run dfdemo-load --batch 2
    uv run dfdemo-load --batch bad
    uv run dfdemo-load --batch 1 --dry-run    # no GCP calls, just shows the plan
"""

from __future__ import annotations

import argparse
import sys

from dataform_demo.config import BQ_LOCATION, DATA_DIR, PROJECT_ID, RAW_DATASET

# BigQuery type names are used as strings so --dry-run works without importing the client.
SCHEMAS: dict[str, list[tuple[str, str, str]]] = {
    # (column, type, mode)
    "customers": [
        ("customer_id", "INT64", "REQUIRED"),
        ("first_name", "STRING", "NULLABLE"),
        ("last_name", "STRING", "NULLABLE"),
        ("email", "STRING", "NULLABLE"),
        ("country", "STRING", "NULLABLE"),
        ("signup_date", "DATE", "NULLABLE"),
        ("marketing_opt_in", "BOOL", "NULLABLE"),
    ],
    "products": [
        ("product_id", "INT64", "REQUIRED"),
        ("product_name", "STRING", "NULLABLE"),
        ("category", "STRING", "NULLABLE"),
        ("unit_price", "NUMERIC", "NULLABLE"),
        ("unit_cost", "NUMERIC", "NULLABLE"),
    ],
    "orders": [
        ("order_id", "INT64", "REQUIRED"),
        ("customer_id", "INT64", "REQUIRED"),
        ("order_ts", "TIMESTAMP", "REQUIRED"),
        ("updated_at", "TIMESTAMP", "REQUIRED"),
        ("status", "STRING", "NULLABLE"),
        ("channel", "STRING", "NULLABLE"),
    ],
    "order_items": [
        ("order_item_id", "INT64", "REQUIRED"),
        ("order_id", "INT64", "REQUIRED"),
        ("product_id", "INT64", "REQUIRED"),
        ("quantity", "INT64", "NULLABLE"),
        ("unit_price", "NUMERIC", "NULLABLE"),
        ("discount_pct", "NUMERIC", "NULLABLE"),
    ],
    "events": [
        ("event_id", "INT64", "REQUIRED"),
        ("customer_id", "INT64", "NULLABLE"),
        ("session_id", "STRING", "NULLABLE"),
        ("event_ts", "TIMESTAMP", "REQUIRED"),
        ("event_type", "STRING", "NULLABLE"),
        ("device", "STRING", "NULLABLE"),
    ],
}

# batch name -> (directory, write disposition)
BATCHES: dict[str, tuple[str, str]] = {
    "1": ("batch_1", "WRITE_TRUNCATE"),
    "2": ("batch_2", "WRITE_APPEND"),
    "bad": ("batch_bad", "WRITE_APPEND"),
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--batch", choices=sorted(BATCHES), required=True)
    parser.add_argument("--dry-run", action="store_true", help="Print the plan without calling BigQuery.")
    args = parser.parse_args()

    directory, disposition = BATCHES[args.batch]
    batch_dir = DATA_DIR / directory
    csv_files = sorted(batch_dir.glob("*.csv"))
    if not csv_files:
        sys.exit(f"No CSV files in {batch_dir}. Run `uv run dfdemo-generate` first.")

    unknown = [f.stem for f in csv_files if f.stem not in SCHEMAS]
    if unknown:
        sys.exit(f"No schema defined for: {', '.join(unknown)}")

    print(f"Batch '{args.batch}' -> {PROJECT_ID}.{RAW_DATASET} (location={BQ_LOCATION}, {disposition})")

    if args.dry_run:
        for csv_file in csv_files:
            rows = sum(1 for _ in csv_file.open(encoding="utf-8")) - 1
            print(f"  [dry-run] {csv_file.name}: {rows:,} rows -> {PROJECT_ID}.{RAW_DATASET}.{csv_file.stem}")
        return

    from google.cloud import bigquery  # imported lazily so --dry-run needs no credentials

    client = bigquery.Client(project=PROJECT_ID, location=BQ_LOCATION)

    for csv_file in csv_files:
        table_id = f"{PROJECT_ID}.{RAW_DATASET}.{csv_file.stem}"
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            schema=[bigquery.SchemaField(name, type_, mode=mode) for name, type_, mode in SCHEMAS[csv_file.stem]],
            write_disposition=getattr(bigquery.WriteDisposition, disposition),
        )
        with csv_file.open("rb") as handle:
            job = client.load_table_from_file(handle, table_id, job_config=job_config)
        job.result()
        table = client.get_table(table_id)
        print(f"  loaded {csv_file.name}: +{job.output_rows:,} rows (table now has {table.num_rows:,})")


if __name__ == "__main__":
    main()
