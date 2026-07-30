#!/usr/bin/env python3
"""
Generate logical assertions from test results.
Run: python src/generate_assertions.py
"""

import sqlite3, uuid, os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'caral_facts.sqlite')

def generate():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Отримуємо всі експерименти
    experiments = c.execute("SELECT * FROM experiments").fetchall()
    for exp in experiments:
        exp_uuid, title, question, null_rule, alt_rule = exp

        # Рахуємо підтримку гіпотез серед тестів цього експерименту
        tests = c.execute("""SELECT test_uuid FROM discriminating_tests
                             WHERE experiment_uuid = ?""", (exp_uuid,)).fetchall()
        test_uuids = [t[0] for t in tests]

        null_count = 0
        alt_count = 0
        for test_uuid in test_uuids:
            # Беремо останній результат для кожного тесту (якщо їх кілька)
            res = c.execute("""SELECT supports_hypothesis FROM test_results
                               WHERE test_uuid = ? ORDER BY rowid DESC LIMIT 1""",
                            (test_uuid,)).fetchone()
            if res:
                if res[0] == 'null':
                    null_count += 1
                elif res[0] == 'alternative':
                    alt_count += 1
                # insufficient_data ігноруємо

        # Визначаємо загальний висновок
        if alt_count > null_count:
            status = 'supported'
            rule_id = alt_rule
            conclusion = f"Alternative hypothesis (rule {alt_rule}) supported by {alt_count}/{len(test_uuids)} tests"
        elif null_count > alt_count:
            status = 'supported'
            rule_id = null_rule
            conclusion = f"Null hypothesis (rule {null_rule}) supported by {null_count}/{len(test_uuids)} tests"
        else:
            status = 'contradictory'
            rule_id = None
            conclusion = f"Tests are split ({null_count} vs {alt_count})"

        # Формула (спрощена)
        formula = f"⊢ {title} : {conclusion}"

        # Записуємо твердження
        assertion_uuid = str(uuid.uuid4())
        derived = str(test_uuids)  # JSON-подібний рядок
        c.execute("""INSERT INTO logic_assertions
                     (assertion_uuid, hypothesis_rule_id, formula, status, derived_from)
                     VALUES (?, ?, ?, ?, ?)""",
                  (assertion_uuid, rule_id, formula, status, derived))

        print(f"Assertion: {formula} (status={status})")

    conn.commit()
    conn.close()
    print("Assertions generated.")

if __name__ == "__main__":
    generate()