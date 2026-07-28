#!/usr/bin/env python3
"""
Build the minimal Caral‑Supe fact database (SQLite).

Run from the project root:
    python database/build_db.py

This will create ``caral_facts.sqlite`` in the current directory.
"""

import sqlite3
import csv
import os
import sys

DB_PATH = "caral_facts.sqlite"
SCHEMA_FILE = os.path.join("database", "schema.sql")
SEED_SITES = os.path.join("database", "seed_sites.csv")
SEED_POP = os.path.join("database", "seed_population.csv")

def execute_schema(conn):
    """Read and execute the SQL schema file."""
    with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
        sql = f.read()
    conn.executescript(sql)
    print("Schema applied.")

def import_csv(conn, table_name, csv_path, columns):
    """Import a CSV file into the given table."""
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            # Build a tuple of values in the same order as columns
            values = tuple(row[col] for col in columns)
            rows.append(values)
    placeholders = ", ".join(["?"] * len(columns))
    cols = ", ".join(columns)
    sql = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"
    conn.executemany(sql, rows)
    print(f"Imported {len(rows)} rows into {table_name}.")

def seed_rules(conn):
    """Insert the four civilization rules."""
    rules = [
        (1, "irrigation_growth", "Irrigation-driven population growth (SPRING)"),
        (2, "monumental_cooperation", "Monumental cooperation and trade (SUMMER)"),
        (3, "trade_compensation", "Trade compensation under environmental stress (AUTUMN)"),
        (4, "collapse", "System collapse and dispersal (WINTER)")
    ]
    conn.executemany(
        "INSERT INTO rules (rule_id, name, description) VALUES (?, ?, ?)",
        rules
    )
    print(f"Inserted {len(rules)} rules.")

def main():
    # Remove existing database to start fresh
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        execute_schema(conn)
        import_csv(conn, "sites", SEED_SITES, ["site_id", "name", "latitude", "longitude"])
        import_csv(conn, "observations", SEED_POP, ["site_id", "type", "value", "year_from", "year_to", "method"])
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