#!/usr/bin/env python3
"""
Build the Caral‑Supe fact database (SQLite) from seed CSV files.

Run from the project root:
    python database/build_db.py
Creates ``caral_facts.sqlite``.
"""

import sqlite3, csv, os, sys

DB_PATH = "caral_facts.sqlite"
SCHEMA_FILE = os.path.join("database", "schema.sql")

# Table → (csv_path, [columns])
SEED_FILES = {
    "sites": ("database/seed_sites.csv", ["site_id", "name", "latitude", "longitude"]),
    "sources": ("database/seed_sources.csv", ["source_id", "author", "year", "title", "doi"]),
    "observations": [
        ("database/seed_population.csv", ["site_id", "source_id", "type", "value", "year_from", "year_to", "method"]),
        ("database/seed_monuments.csv", ["site_id", "source_id", "type", "value", "year_from", "year_to", "method"]),
        ("database/seed_trade.csv", ["site_id", "source_id", "type", "value", "year_from", "year_to", "method"]),
        ("database/seed_isotopes.csv", ["site_id", "source_id", "type", "value", "year_from", "year_to", "method"]),
        ("database/seed_abandonment.csv", ["site_id", "source_id", "type", "value", "year_from", "year_to", "method"]),
        ("database/seed_radiocarbon.csv", ["site_id", "source_id", "type", "value", "year_from", "year_to", "method"]),
        ("database/seed_cultural_continuity.csv", ["site_id", "source_id", "type", "value", "year_from", "year_to", "method"]),
    ],
    "climate_proxies": ("database/seed_climate.csv", ["site_id", "source_id", "proxy_type", "year", "value"]),
}

def execute_schema(conn):
    with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    print("Schema applied.")

def import_csv(conn, table_name, csv_path, columns):
    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} not found, skipping.")
        return
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [tuple(row[col] for col in columns) for row in reader]
    placeholders = ", ".join(["?"] * len(columns))
    cols = ", ".join(columns)
    conn.executemany(f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})", rows)
    print(f"Imported {len(rows)} rows into {table_name} from {csv_path}")

def seed_rules(conn):
    rules = [
        (1, "irrigation_growth", "Irrigation-driven population growth (SPRING)"),
        (2, "monumental_cooperation", "Monumental cooperation and trade (SUMMER)"),
        (3, "trade_compensation", "Trade compensation under environmental stress (AUTUMN)"),
        (4, "collapse", "System collapse and dispersal (WINTER)")
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO rules (rule_id, name, description) VALUES (?, ?, ?)", rules
    )
    print(f"Inserted {len(rules)} basic rules.")

def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        execute_schema(conn)
        # Import base tables
        import_csv(conn, "sites", *SEED_FILES["sites"])
        import_csv(conn, "sources", *SEED_FILES["sources"])
        # Import observations from multiple files
        for csv_path, cols in SEED_FILES["observations"]:
            import_csv(conn, "observations", csv_path, cols)
        # Import climate proxies
        import_csv(conn, "climate_proxies", *SEED_FILES["climate_proxies"])
        # Insert basic rules
        seed_rules(conn)
        conn.commit()
        print(f"Database {DB_PATH} created successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    main()