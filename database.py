"""
database.py — Creates and seeds the logistics SQLite database.
Run directly: python database.py
Or imported by main.py on first startup.
"""

import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = "logistics.db"

CITIES = [
    ("Delhi",      "Delhi",          "North"),
    ("Mumbai",     "Maharashtra",    "West"),
    ("Bangalore",  "Karnataka",      "South"),
    ("Chennai",    "Tamil Nadu",     "South"),
    ("Hyderabad",  "Telangana",      "South"),
    ("Pune",       "Maharashtra",    "West"),
    ("Kolkata",    "West Bengal",    "East"),
    ("Jaipur",     "Rajasthan",      "North"),
    ("Ahmedabad",  "Gujarat",        "West"),
    ("Lucknow",    "Uttar Pradesh",  "North"),
    ("Chandigarh", "Punjab",         "North"),
    ("Surat",      "Gujarat",        "West"),
    ("Kochi",      "Kerala",         "South"),
    ("Indore",     "Madhya Pradesh", "Central"),
    ("Bhopal",     "Madhya Pradesh", "Central"),
]

PARTNERS = [
    "BlueDart Express",
    "Delhivery",
    "Ecom Express",
    "Xpressbees",
    "Shadowfax",
    "Porter",
    "Dunzo",
    "Shiprocket",
    "WareIQ",
    "FedEx India",
]

CATEGORIES = [
    "Electronics", "Clothing", "Food & Grocery",
    "Furniture", "Pharma", "Books", "Toys", "Sports",
]

# Status distribution: mostly delivered, some delays/cancellations
STATUSES = ["delivered", "pending", "cancelled", "delayed", "in_transit", "returned"]
STATUS_WEIGHTS = [0.55, 0.12, 0.08, 0.12, 0.09, 0.04]

DELAY_REASONS = [
    "Weather disruption",
    "Vehicle breakdown",
    "Address not found",
    "Customer unavailable",
    "High volume surge",
    "Road blockage",
    "Incorrect pin code",
    "Warehouse backlog",
]


def create_database(db_path: str = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.executescript("""
        DROP TABLE IF EXISTS daily_metrics;
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS delivery_partners;
        DROP TABLE IF EXISTS cities;

        CREATE TABLE cities (
            city_id   INTEGER PRIMARY KEY,
            name      TEXT NOT NULL,
            state     TEXT NOT NULL,
            zone      TEXT NOT NULL
        );

        CREATE TABLE delivery_partners (
            partner_id    INTEGER PRIMARY KEY,
            name          TEXT NOT NULL,
            base_city     TEXT NOT NULL,
            rating        REAL NOT NULL,
            active_orders INTEGER DEFAULT 0
        );

        CREATE TABLE orders (
            order_id          TEXT PRIMARY KEY,
            customer_id       TEXT NOT NULL,
            origin_city       TEXT NOT NULL,
            destination_city  TEXT NOT NULL,
            delivery_partner  TEXT NOT NULL,
            category          TEXT NOT NULL,
            status            TEXT NOT NULL,
            amount            REAL NOT NULL,
            weight_kg         REAL NOT NULL,
            created_at        TEXT NOT NULL,
            expected_at       TEXT NOT NULL,
            delivered_at      TEXT,
            delay_reason      TEXT
        );

        CREATE TABLE daily_metrics (
            metric_id              INTEGER PRIMARY KEY,
            date                   TEXT NOT NULL,
            city                   TEXT NOT NULL,
            total_orders           INTEGER,
            delivered_orders       INTEGER,
            cancelled_orders       INTEGER,
            delayed_orders         INTEGER,
            avg_delivery_time_hrs  REAL
        );
    """)

    # --- Cities ---
    for i, (name, state, zone) in enumerate(CITIES, 1):
        cur.execute(
            "INSERT INTO cities VALUES (?, ?, ?, ?)",
            (i, name, state, zone),
        )

    # --- Delivery partners ---
    random.seed(99)
    for i, name in enumerate(PARTNERS, 1):
        base_city = random.choice(CITIES)[0]
        rating = round(random.uniform(3.2, 4.9), 1)
        active = random.randint(40, 600)
        cur.execute(
            "INSERT INTO delivery_partners VALUES (?, ?, ?, ?, ?)",
            (i, name, base_city, rating, active),
        )

    # --- Orders (5 000 rows) ---
    random.seed(42)
    now = datetime.now()
    city_names = [c[0] for c in CITIES]

    for i in range(1, 5001):
        order_id    = f"ORD{i:05d}"
        customer_id = f"CUST{random.randint(1000, 9999)}"
        origin      = random.choice(city_names)
        dest        = random.choice([c for c in city_names if c != origin])
        partner     = random.choice(PARTNERS)
        category    = random.choice(CATEGORIES)
        status      = random.choices(STATUSES, STATUS_WEIGHTS)[0]
        amount      = round(random.uniform(200, 15000), 2)
        weight      = round(random.uniform(0.1, 30.0),  2)

        days_ago   = random.randint(0, 90)
        created_dt = now - timedelta(days=days_ago, hours=random.randint(0, 23))
        created_at = created_dt.strftime("%Y-%m-%d %H:%M:%S")

        expected_hrs = random.randint(24, 120)
        expected_at  = (created_dt + timedelta(hours=expected_hrs)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        delivered_at = None
        delay_reason = None

        if status == "delivered":
            # 60% on-time, 40% slightly late
            offset = random.randint(-12, 48)
            delivered_at = (
                created_dt + timedelta(hours=expected_hrs + offset)
            ).strftime("%Y-%m-%d %H:%M:%S")
        elif status == "delayed":
            delay_reason = random.choice(DELAY_REASONS)

        cur.execute(
            "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                order_id, customer_id, origin, dest, partner,
                category, status, amount, weight,
                created_at, expected_at, delivered_at, delay_reason,
            ),
        )

    # --- Daily metrics (last 30 days × 15 cities) ---
    metric_id = 1
    for days_ago in range(30, 0, -1):
        date = (now - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        for city in city_names:
            total     = random.randint(50, 300)
            delivered = int(total * random.uniform(0.50, 0.75))
            cancelled = int(total * random.uniform(0.05, 0.12))
            delayed   = int(total * random.uniform(0.08, 0.18))
            avg_time  = round(random.uniform(18, 72), 1)
            cur.execute(
                "INSERT INTO daily_metrics VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (metric_id, date, city, total, delivered, cancelled, delayed, avg_time),
            )
            metric_id += 1

    conn.commit()
    conn.close()
    print(
        "✅  Database ready:"
        " 5 000 orders | 15 cities | 10 partners | 30 days of metrics"
    )


if __name__ == "__main__":
    create_database()
