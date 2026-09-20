"""Generate the synthetic e-commerce dataset used in the demo.

The output is deterministic (fixed seed) and is committed to the repo under ``data/``,
so you only need to re-run this script if you want to change the dataset.

Three "batches" simulate data arriving over time:

* ``batch_1``   -- June + July 2026. Customers, products, orders, order items, events.
                   The last days of July contain ``pending`` orders.
* ``batch_2``   -- August 2026. New customers/orders/items/events, PLUS new snapshots of
                   batch-1 orders whose status changed (pending -> completed, completed -> returned).
                   This is what makes the incremental + MERGE logic interesting.
* ``batch_bad`` -- A handful of deliberately broken rows (orphan customer, negative quantity)
                   used to show assertions failing.

The raw ``orders`` table is an append-only log of order snapshots: the same ``order_id`` can
appear more than once, and the latest ``updated_at`` wins.

Usage:
    uv run dfdemo-generate            # writes data/batch_*/
    uv run dfdemo-generate --seed 7
"""

from __future__ import annotations

import argparse
import bisect
import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path

from dataform_demo.config import DATA_DIR

# --------------------------------------------------------------------------------------
# Static reference data
# --------------------------------------------------------------------------------------
COUNTRIES = ["US", "CL", "MX", "BR", "AR", "CO", "PE", "ES"]
COUNTRY_WEIGHTS = [30, 12, 14, 14, 8, 8, 6, 8]

FIRST_NAMES = [
    "Ana", "Luis", "Sofia", "Mateo", "Valentina", "Diego", "Camila", "Lucas", "Isabella", "Javier",
    "Martina", "Pablo", "Emma", "Nicolas", "Julia", "Andres", "Laura", "Felipe", "Daniela", "Tomas",
    "Carla", "Sebastian", "Paula", "Gabriel", "Elena", "Ricardo", "Marta", "Bruno", "Lucia", "Hugo",
]
LAST_NAMES = [
    "Garcia", "Rodriguez", "Martinez", "Lopez", "Gonzalez", "Perez", "Sanchez", "Ramirez", "Torres", "Flores",
    "Rivera", "Gomez", "Diaz", "Reyes", "Morales", "Cruz", "Ortiz", "Silva", "Castro", "Vargas",
    "Rojas", "Herrera", "Medina", "Aguilar", "Navarro", "Molina", "Suarez", "Campos", "Fuentes", "Vega",
]

# category -> (product nouns, (min price, max price))
CATALOG: dict[str, tuple[list[str], tuple[float, float]]] = {
    "Electronics": (["Earbuds", "Speaker", "Webcam", "Keyboard", "Mouse", "Charger", "Monitor Stand", "Power Bank"], (15, 220)),
    "Home": (["Desk Lamp", "Throw Blanket", "Coffee Grinder", "Storage Bin", "Wall Clock", "Candle Set", "Plant Pot", "Cutting Board"], (8, 90)),
    "Sports": (["Yoga Mat", "Water Bottle", "Resistance Bands", "Running Belt", "Jump Rope", "Gym Bag", "Foam Roller", "Cycling Gloves"], (6, 70)),
    "Books": (["SQL Cookbook", "Python Handbook", "Statistics Primer", "Data Viz Guide", "ML Field Guide", "Analytics Journal", "Cloud Atlas", "Dashboard Design"], (9, 45)),
    "Beauty": (["Face Cream", "Shampoo", "Lip Balm", "Hair Brush", "Sunscreen", "Body Lotion", "Nail Kit", "Perfume Mini"], (5, 60)),
    "Toys": (["Puzzle", "Building Blocks", "Board Game", "Plush Bear", "RC Car", "Art Set", "Card Deck", "Science Kit"], (7, 80)),
}
ADJECTIVES = ["Classic", "Pro", "Mini", "Eco", "Deluxe", "Smart", "Compact", "Ultra", "Travel", "Studio"]

CHANNELS = ["web", "mobile_app", "marketplace"]
CHANNEL_WEIGHTS = [50, 35, 15]
DEVICES = ["desktop", "mobile", "tablet"]
DEVICE_WEIGHTS = [45, 45, 10]

# --------------------------------------------------------------------------------------
# Time windows
# --------------------------------------------------------------------------------------
BATCH1_START, BATCH1_END = date(2026, 6, 1), date(2026, 7, 31)
BATCH2_START, BATCH2_END = date(2026, 8, 1), date(2026, 8, 31)
BAD_DAY = date(2026, 9, 1)

N_PRODUCTS = 80
N_CUSTOMERS_BATCH1 = 700
N_CUSTOMERS_BATCH2 = 100
N_PENDING_TO_UPDATE_DAYS = 3   # last N days of a batch keep pending orders
N_RETURNS_IN_BATCH2 = 60       # completed batch-1 orders that become "returned" in batch 2


def fmt_ts(value: datetime) -> str:
    """BigQuery-friendly UTC timestamp for CSV loads."""
    return value.strftime("%Y-%m-%d %H:%M:%S")


def at_midnight(day: date) -> datetime:
    return datetime(day.year, day.month, day.day)


def days_between(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        for row in rows:
            writer.writerow(["" if value is None else value for value in row])
    print(f"  wrote {path.relative_to(DATA_DIR.parent)} ({len(rows):,} rows)")


# --------------------------------------------------------------------------------------
# Generators
# --------------------------------------------------------------------------------------
def make_products(rng: random.Random) -> list[dict]:
    combos = [
        (category, adjective, noun)
        for category, (nouns, _) in CATALOG.items()
        for noun in nouns
        for adjective in ADJECTIVES
    ]
    chosen = rng.sample(combos, N_PRODUCTS)
    products = []
    for index, (category, adjective, noun) in enumerate(sorted(chosen), start=1):
        low, high = CATALOG[category][1]
        price = round(rng.uniform(low, high), 2)
        cost = round(price * rng.uniform(0.45, 0.75), 2)
        products.append(
            {
                "product_id": 1000 + index,
                "product_name": f"{adjective} {noun}",
                "category": category,
                "unit_price": price,
                "unit_cost": cost,
            }
        )
    return products


def make_customers(rng: random.Random, start_id: int, count: int, signup_from: date, signup_to: date) -> list[dict]:
    span = (signup_to - signup_from).days
    customers = []
    for offset in range(count):
        customer_id = start_id + offset
        first, last = rng.choice(FIRST_NAMES), rng.choice(LAST_NAMES)
        email = f"{first}.{last}{customer_id}@example.com"
        country = rng.choices(COUNTRIES, COUNTRY_WEIGHTS)[0]

        # Deliberately messy raw data: the staging layer cleans it up.
        if rng.random() < 0.20:
            email = email.upper()
        if rng.random() < 0.10:
            email = f"  {email} "
        if rng.random() < 0.10:
            country = country.lower()
        if rng.random() < 0.15:
            first, last = first.upper(), last.lower()

        customers.append(
            {
                "customer_id": customer_id,
                "first_name": first,
                "last_name": last,
                "email": email,
                "country": country,
                "signup_date": signup_from + timedelta(days=rng.randint(0, span)),
                "marketing_opt_in": str(rng.random() < 0.55).lower(),
            }
        )
    return customers


class CustomerPool:
    """Picks customers that already exist (signup_date <= order day)."""

    def __init__(self, customers: list[dict]):
        self._sorted = sorted(customers, key=lambda c: c["signup_date"])
        self._dates = [c["signup_date"] for c in self._sorted]

    def pick(self, rng: random.Random, day: date) -> dict:
        upper = bisect.bisect_right(self._dates, day)
        return self._sorted[rng.randrange(upper)]


def make_orders_and_items(
    rng: random.Random,
    pool: CustomerPool,
    products: list[dict],
    start_day: date,
    end_day: date,
    first_order_id: int,
    first_item_id: int,
    orders_per_day: tuple[int, int],
    window_end: datetime,
) -> tuple[list[dict], list[dict]]:
    orders: list[dict] = []
    items: list[dict] = []
    order_id, item_id = first_order_id, first_item_id
    pending_from = end_day - timedelta(days=N_PENDING_TO_UPDATE_DAYS - 1)

    for day in days_between(start_day, end_day):
        for _ in range(rng.randint(*orders_per_day)):
            customer = pool.pick(rng, day)
            order_ts = at_midnight(day) + timedelta(seconds=rng.randrange(86400))

            if day >= pending_from and rng.random() < 0.6:
                status = "pending"
                updated_at = order_ts
            else:
                status = rng.choices(["completed", "cancelled", "returned"], [86, 8, 6])[0]
                updated_at = order_ts + timedelta(hours=rng.randint(1, 48))

            # Watermark safety: the incremental model filters on updated_at, so every row of a
            # batch must stay inside that batch's time window.
            updated_at = min(updated_at, window_end)

            orders.append(
                {
                    "order_id": order_id,
                    "customer_id": customer["customer_id"],
                    "order_ts": order_ts,
                    "updated_at": updated_at,
                    "status": status,
                    "channel": rng.choices(CHANNELS, CHANNEL_WEIGHTS)[0],
                }
            )

            for _ in range(rng.choices([1, 2, 3, 4], [45, 30, 15, 10])[0]):
                product = rng.choice(products)
                items.append(
                    {
                        "order_item_id": item_id,
                        "order_id": order_id,
                        "product_id": product["product_id"],
                        "quantity": rng.choices([1, 2, 3, 4], [60, 25, 10, 5])[0],
                        "unit_price": product["unit_price"],
                        "discount_pct": rng.choice([0, 0, 0, 0.05, 0.10, 0.15, 0.20]),
                    }
                )
                item_id += 1
            order_id += 1
    return orders, items


def make_status_changes(rng: random.Random, batch1_orders: list[dict]) -> list[dict]:
    """New snapshots for batch-1 orders (same order_id, later updated_at)."""
    snapshots = []

    for order in batch1_orders:
        if order["status"] == "pending":
            new_status = rng.choices(["completed", "cancelled"], [90, 10])[0]
            snapshots.append({**order, "status": new_status, "updated_at": at_midnight(BATCH2_START) + timedelta(hours=rng.randint(1, 60))})

    completed = [o for o in batch1_orders if o["status"] == "completed"]
    for order in rng.sample(completed, N_RETURNS_IN_BATCH2):
        snapshots.append({**order, "status": "returned", "updated_at": at_midnight(BATCH2_START) + timedelta(hours=rng.randint(24, 24 * 20))})
    return snapshots


def make_events(
    rng: random.Random,
    pool: CustomerPool,
    start_day: date,
    end_day: date,
    first_event_id: int,
    first_session_no: int,
    sessions_per_day: tuple[int, int],
) -> list[dict]:
    events: list[dict] = []
    event_id, session_no = first_event_id, first_session_no

    for day in days_between(start_day, end_day):
        for _ in range(rng.randint(*sessions_per_day)):
            session_id = f"s{session_no:07d}"
            session_no += 1
            device = rng.choices(DEVICES, DEVICE_WEIGHTS)[0]
            if rng.random() < 0.05:
                device = device.title()  # messy raw data on purpose
            customer_id = pool.pick(rng, day)["customer_id"] if rng.random() < 0.6 else None
            clock = at_midnight(day) + timedelta(seconds=rng.randrange(86400 - 3600))

            steps = ["page_view"] * rng.randint(1, 4)
            if rng.random() < 0.40:
                steps.append("add_to_cart")
                if rng.random() < 0.55:
                    steps.append("begin_checkout")
                    if rng.random() < 0.65:
                        steps.append("purchase")

            for event_type in steps:
                clock += timedelta(seconds=rng.randint(3, 120))
                events.append(
                    {
                        "event_id": event_id,
                        "customer_id": customer_id,
                        "session_id": session_id,
                        "event_ts": clock,
                        "event_type": event_type,
                        "device": device,
                    }
                )
                event_id += 1
    return events


def make_bad_batch(first_order_id: int, first_item_id: int) -> tuple[list[dict], list[dict]]:
    """Rows that violate the data contract on purpose (orphan customer, negative quantity)."""
    orders, items = [], []
    base = at_midnight(BAD_DAY) + timedelta(hours=10)
    for index in range(5):
        order_id = first_order_id + index
        orders.append(
            {
                "order_id": order_id,
                "customer_id": 999999,  # does not exist in customers
                "order_ts": base + timedelta(minutes=index * 7),
                "updated_at": base + timedelta(minutes=index * 7),
                "status": "completed",
                "channel": "web",
            }
        )
        items.append(
            {
                "order_item_id": first_item_id + index,
                "order_id": order_id,
                "product_id": 1001,
                "quantity": -3 if index == 0 else 1,  # one negative quantity
                "unit_price": 19.99,
                "discount_pct": 0,
            }
        )
    return orders, items


# --------------------------------------------------------------------------------------
# Serialisation
# --------------------------------------------------------------------------------------
ORDER_HEADER = ["order_id", "customer_id", "order_ts", "updated_at", "status", "channel"]
ITEM_HEADER = ["order_item_id", "order_id", "product_id", "quantity", "unit_price", "discount_pct"]
EVENT_HEADER = ["event_id", "customer_id", "session_id", "event_ts", "event_type", "device"]
CUSTOMER_HEADER = ["customer_id", "first_name", "last_name", "email", "country", "signup_date", "marketing_opt_in"]
PRODUCT_HEADER = ["product_id", "product_name", "category", "unit_price", "unit_cost"]


def order_rows(orders: list[dict]) -> list[list]:
    return [
        [o["order_id"], o["customer_id"], fmt_ts(o["order_ts"]), fmt_ts(o["updated_at"]), o["status"], o["channel"]]
        for o in orders
    ]


def item_rows(items: list[dict]) -> list[list]:
    return [
        [i["order_item_id"], i["order_id"], i["product_id"], i["quantity"], f"{i['unit_price']:.2f}", f"{i['discount_pct']:.2f}"]
        for i in items
    ]


def event_rows(events: list[dict]) -> list[list]:
    return [
        [e["event_id"], e["customer_id"], e["session_id"], fmt_ts(e["event_ts"]), e["event_type"], e["device"]]
        for e in events
    ]


def customer_rows(customers: list[dict]) -> list[list]:
    return [
        [c["customer_id"], c["first_name"], c["last_name"], c["email"], c["country"], c["signup_date"].isoformat(), c["marketing_opt_in"]]
        for c in customers
    ]


def product_rows(products: list[dict]) -> list[list]:
    return [[p["product_id"], p["product_name"], p["category"], f"{p['unit_price']:.2f}", f"{p['unit_cost']:.2f}"] for p in products]


# --------------------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------------------
def generate(seed: int, out_dir: Path) -> None:
    rng = random.Random(seed)
    print(f"Generating dataset (seed={seed}) into {out_dir}")

    products = make_products(rng)
    customers_1 = make_customers(rng, 10001, N_CUSTOMERS_BATCH1, date(2025, 1, 1), BATCH1_END)
    customers_2 = make_customers(rng, 10001 + N_CUSTOMERS_BATCH1, N_CUSTOMERS_BATCH2, BATCH2_START, BATCH2_END)
    pool_1 = CustomerPool(customers_1)
    pool_all = CustomerPool(customers_1 + customers_2)

    # ---- batch 1
    orders_1, items_1 = make_orders_and_items(
        rng, pool_1, products, BATCH1_START, BATCH1_END,
        first_order_id=100001, first_item_id=1, orders_per_day=(50, 80),
        window_end=at_midnight(BATCH1_END) + timedelta(hours=23, minutes=59, seconds=59),
    )
    events_1 = make_events(rng, pool_1, BATCH1_START, BATCH1_END, 1, 1, (45, 75))

    batch1 = out_dir / "batch_1"
    write_csv(batch1 / "customers.csv", CUSTOMER_HEADER, customer_rows(customers_1))
    write_csv(batch1 / "products.csv", PRODUCT_HEADER, product_rows(products))
    write_csv(batch1 / "orders.csv", ORDER_HEADER, order_rows(orders_1))
    write_csv(batch1 / "order_items.csv", ITEM_HEADER, item_rows(items_1))
    write_csv(batch1 / "events.csv", EVENT_HEADER, event_rows(events_1))

    # ---- batch 2 (new data + status changes of batch-1 orders)
    next_order_id = max(o["order_id"] for o in orders_1) + 1
    next_item_id = max(i["order_item_id"] for i in items_1) + 1
    orders_2, items_2 = make_orders_and_items(
        rng, pool_all, products, BATCH2_START, BATCH2_END,
        first_order_id=next_order_id, first_item_id=next_item_id, orders_per_day=(55, 85),
        window_end=at_midnight(BATCH2_END) + timedelta(hours=23, minutes=59, seconds=59),
    )
    snapshots = make_status_changes(rng, orders_1)
    events_2 = make_events(rng, pool_all, BATCH2_START, BATCH2_END, max(e["event_id"] for e in events_1) + 1, 3_000_000, (45, 75))

    batch2 = out_dir / "batch_2"
    write_csv(batch2 / "customers.csv", CUSTOMER_HEADER, customer_rows(customers_2))
    write_csv(batch2 / "orders.csv", ORDER_HEADER, order_rows(snapshots + orders_2))
    write_csv(batch2 / "order_items.csv", ITEM_HEADER, item_rows(items_2))
    write_csv(batch2 / "events.csv", EVENT_HEADER, event_rows(events_2))

    # ---- bad batch
    bad_orders, bad_items = make_bad_batch(
        max(o["order_id"] for o in orders_2) + 1,
        max(i["order_item_id"] for i in items_2) + 1,
    )
    bad = out_dir / "batch_bad"
    write_csv(bad / "orders.csv", ORDER_HEADER, order_rows(bad_orders))
    write_csv(bad / "order_items.csv", ITEM_HEADER, item_rows(bad_items))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42).")
    parser.add_argument("--out-dir", type=Path, default=DATA_DIR, help="Output directory (default: ./data).")
    args = parser.parse_args()
    generate(args.seed, args.out_dir)


if __name__ == "__main__":
    main()
