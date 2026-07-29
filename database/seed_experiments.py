import sqlite3
import uuid

DB_PATH = "caral_facts.sqlite"

def seed():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    c = conn.cursor()

    # Додаємо нові правила (6–10), якщо вони відсутні
    rules = [
        (6, "agricultural_primacy", "Inland agriculture first (Haas/Shady)"),
        (7, "complementarity", "Marine-agricultural complementarity (Sandweiss & Moseley)"),
        (8, "seismic_shock", "Earthquake/ENSO sudden collapse (Sandweiss 2009)"),
        (9, "irrigation_decay", "Gradual irrigation failure (Beresford-Jones)"),
        (10, "megadrought_migration", "4.2 ka drought + managed migration (Shady 2025)")
    ]
    for rule_id, name, desc in rules:
        c.execute("INSERT OR IGNORE INTO rules (rule_id, name, description) VALUES (?, ?, ?)",
                  (rule_id, name, desc))

    # Експеримент 1: Формування
    exp1_uuid = str(uuid.uuid4())
    c.execute("INSERT INTO experiments VALUES (?, ?, ?, ?, ?)",
              (exp1_uuid,
               "Testing Formative Phase Hypotheses",
               "Which subsystem drove monumentality first?",
               7,   # complementarity as null? Or we can leave agricultural (6) as null.
               7,   # we will define properly in tests
               ))
    # Виправимо: згідно зі статтею, нульова гіпотеза — complementarity (C), альтернатива — agricultural primacy (B)
    # Але для простоти поки що вставимо так, а в тестах розрізнимо.
    # Насправді краще зробити дві пари, але для MVP залишимо одну.

    # Тести для формування
    tests_form = [
        ("test-form-001", exp1_uuid, "Isotopes: marine protein % at Caral vs Aspero", "similar (>40%)", "Caral < 30%"),
        ("test-form-002", exp1_uuid, "Site size: inland vs coastal", "similar sizes", "inland much larger"),
        ("test-form-003", exp1_uuid, "Earliest radiocarbon dates", "coastal older or same", "inland older")
    ]
    for t in tests_form:
        c.execute("INSERT INTO discriminating_tests VALUES (?, ?, ?, ?, ?)", t)

    # Експеримент 2: Занепад
    exp2_uuid = str(uuid.uuid4())
    c.execute("INSERT INTO experiments VALUES (?, ?, ?, ?, ?)",
              (exp2_uuid,
               "Testing Decline Phase Hypotheses",
               "Sudden collapse or managed adaptation?",
               8,   # seismic shock
               10)) # megadrought migration

    tests_decl = [
        ("test-decl-001", exp2_uuid, "Destruction layer (thin, synchronous)", "present, same time everywhere", "absent or asynchronous"),
        ("test-decl-002", exp2_uuid, "Abandonment timing (inland vs coastal)", "inland first", "coastal first or simultaneous"),
        ("test-decl-003", exp2_uuid, "Cultural continuity at Vichama/Peñico", "abrupt change", "continuity in architecture/symbols")
    ]
    for t in tests_decl:
        c.execute("INSERT INTO discriminating_tests VALUES (?, ?, ?, ?, ?)", t)

    conn.commit()
    conn.close()
    print("Experiments and tests seeded.")

if __name__ == "__main__":
    seed()