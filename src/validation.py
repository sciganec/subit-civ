#!/usr/bin/env python3
"""
Automated hypothesis validation for Caral‑Supe experiments.
Run from the project root:
    python src/validation.py
Or import into a notebook.
"""

import sqlite3
import os
import uuid
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'caral_facts.sqlite')

# Map test_uuid -> test_type (for custom SQL / logic)
TEST_TYPES = {
    "test-form-001": "marine_protein",
    "test-form-002": "site_size",
    "test-form-003": "earliest_date",
    "test-decl-001": "abandonment_synchrony",
    "test-decl-002": "abandonment_order",
    "test-decl-003": "cultural_continuity",
}

def get_connection():
    return sqlite3.connect(DB_PATH)

def evaluate_test(test_row, conn):
    """Return (supports, comment) for a single discriminating test."""
    test_uuid, exp_uuid, desc, expect_null, expect_alt = test_row
    test_type = TEST_TYPES.get(test_uuid)
    if not test_type:
        return ('insufficient_data', f'Unknown test type for {test_uuid}')

    c = conn.cursor()

    # ---- Marine protein test ----
    if test_type == "marine_protein":
        rows = c.execute("SELECT site_id, value FROM observations WHERE type='marine_protein_%'").fetchall()
        if len(rows) < 2:
            return ('insufficient_data', 'Need at least two marine protein observations.')
        caral_vals = [v for sid, v in rows if sid == 1]
        aspero_vals = [v for sid, v in rows if sid == 2]
        if not caral_vals:
            return ('insufficient_data', 'No marine protein data for Caral.')
        mean_caral = sum(caral_vals) / len(caral_vals)
        if mean_caral < 30:
            return ('alternative', f'Caral marine protein {mean_caral:.1f}% < 30% → agricultural primacy')
        else:
            return ('null', f'Caral marine protein {mean_caral:.1f}% ≥ 30% → complementarity')

    # ---- Site size test (use peak population) ----
    elif test_type == "site_size":
        pop_caral = c.execute("SELECT MAX(value) FROM observations WHERE site_id=1 AND type='population'").fetchone()[0]
        pop_aspero = c.execute("SELECT MAX(value) FROM observations WHERE site_id=2 AND type='population'").fetchone()[0]
        if pop_caral is None or pop_aspero is None:
            return ('insufficient_data', 'Missing population data for one or both sites.')
        ratio = pop_caral / pop_aspero if pop_aspero > 0 else 0
        if ratio >= 3:
            return ('alternative', f'Caral population {pop_caral} vs Aspero {pop_aspero} (ratio {ratio:.1f}) → inland much larger')
        else:
            return ('null', f'Caral/Aspero population ratio {ratio:.1f} → similar sizes')

    # ---- Earliest radiocarbon date test ----
    elif test_type == "earliest_date":
        caral_date = c.execute("SELECT value FROM observations WHERE site_id=1 AND type='earliest_radiocarbon_date'").fetchone()
        aspero_date = c.execute("SELECT value FROM observations WHERE site_id=2 AND type='earliest_radiocarbon_date'").fetchone()
        if caral_date is None or aspero_date is None:
            return ('insufficient_data', 'Missing radiocarbon date for one or both sites.')
        caral_val = caral_date[0]
        aspero_val = aspero_date[0]
        if caral_val < aspero_val:   # more negative = older BCE
            return ('alternative', f'Caral {caral_val} older than Aspero {aspero_val} → inland older')
        else:
            return ('null', f'Aspero {aspero_val} older or same as Caral {caral_val} → coastal first')

    # ---- Abandonment synchrony test ----
    elif test_type == "abandonment_synchrony":
        dates = c.execute("SELECT year_from FROM observations WHERE type='abandonment_year'").fetchall()
        if len(dates) < 2:
            return ('insufficient_data', 'Need at least two abandonment dates.')
        years = [d[0] for d in dates]
        span = max(years) - min(years)
        if span <= 100:
            return ('null', f'Span {span} years ≤ 100 → synchronous, consistent with seismic shock')
        else:
            return ('alternative', f'Span {span} years > 100 → asynchronous, gradual processes')

    # ---- Abandonment order (inland vs coastal) ----
    elif test_type == "abandonment_order":
        rows = c.execute("""
            SELECT sites.name, observations.year_from FROM observations
            JOIN sites ON observations.site_id = sites.site_id
            WHERE observations.type = 'abandonment_year'
        """).fetchall()
        inland_years = [y for name, y in rows if name in ('Caral', 'Huaricanga')]
        coastal_years = [y for name, y in rows if name in ('Aspero', 'Bandurria')]
        if not inland_years or not coastal_years:
            return ('insufficient_data', 'Need both inland and coastal abandonment data.')
        if max(inland_years) < min(coastal_years):   # inland abandoned earlier
            return ('null', 'Inland sites abandoned earlier → seismic shock')
        else:
            return ('alternative', 'Coastal sites abandoned at same time or earlier → gradual/migration')

    # ---- Cultural continuity test ----
    elif test_type == "cultural_continuity":
        cont = c.execute("SELECT value FROM observations WHERE type='cultural_continuity_index'").fetchall()
        if not cont:
            return ('insufficient_data', 'No cultural continuity data.')
        mean_cont = sum(v[0] for v in cont) / len(cont)
        if mean_cont > 0.5:
            return ('alternative', f'Cultural continuity index {mean_cont:.2f} > 0.5 → managed migration')
        else:
            return ('null', f'Cultural continuity index {mean_cont:.2f} ≤ 0.5 → abrupt change')

    # Fallback
    return ('insufficient_data', f'No handler for {test_uuid}')

def record_result(conn, test_uuid, supports, comment):
    """Insert a row into test_results (UUID, test_uuid, observation_id=0, supports, comment)."""
    result_uuid = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO test_results (result_uuid, test_uuid, observation_id, supports_hypothesis, comment) VALUES (?, ?, ?, ?, ?)",
        (result_uuid, test_uuid, 0, supports, comment)
    )

def run_all_tests():
    conn = get_connection()
    try:
        tests = conn.execute("SELECT * FROM discriminating_tests").fetchall()
        print(f"Found {len(tests)} tests.")
        for test in tests:
            test_uuid = test[0]
            supports, comment = evaluate_test(test, conn)
            record_result(conn, test_uuid, supports, comment)
            print(f"{test_uuid}: {supports.upper()} – {comment}")
        conn.commit()
        print("Validation complete. Results stored in test_results table.")
    except Exception as e:
        conn.rollback()
        print(f"Validation error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run_all_tests()