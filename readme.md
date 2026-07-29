# subit-civ

**From simulation to reproducible hypothesis testing: Caral‑Supe civilisation (Peru, 3500–1800 BCE) powered by a fact‑based database and the SUBIT heuristic framework.**

## What is this?

`subit-civ` lets you **test competing archaeological hypotheses** about the rise and decline of the earliest civilisation in the Americas. It combines:

- a curated **SQLite fact database** of published archaeological data (sites, population estimates, isotope measurements, radiocarbon dates, abandonment chronologies),
- a **macro‑simulation** of the civilisation’s trajectory under different internal rules,
- and a **heuristic framework (SUBIT)** that helps formulate clear discriminating tests and logical assertions.

The project started as a minimal simulation (v0.1) and has grown into a **reproducible research platform** where every empirical claim can be traced back to its source.

## Quickstart

1. **Clone the repository and enter the folder**
   ```bash
   git clone https://github.com/sciganec/subit‑civ.git
   cd subit‑civ
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Build the fact database**
   ```bash
   python database/build_db.py
   python database/seed_experiments.py
   ```
   This creates `caral_facts.sqlite` containing sites, observations, climate proxies, rules, experiments, and discriminating tests.

4. **Run the notebooks**
   ```bash
   jupyter notebook
   ```
   - `notebooks/simulation.ipynb` – macro‑trajectory of population, monuments, trade, and stability class Ω.
   - `notebooks/hypothesis_testing.ipynb` – **evaluation of six competing hypotheses** (marine vs. agricultural primacy, seismic shock vs. gradual decay vs. managed migration).

## Project structure

```
subit‑civ/
├── config/
│   └── caral_params.yaml        # Simulation parameters
├── database/
│   ├── schema.sql               # Full database schema
│   ├── build_db.py              # Creates caral_facts.sqlite from CSV seeds
│   ├── seed_experiments.py      # Populates experiments, hypotheses, tests
│   ├── seed_sites.csv
│   ├── seed_sources.csv
│   ├── seed_population.csv
│   ├── seed_monuments.csv
│   ├── seed_trade.csv
│   ├── seed_isotopes.csv
│   ├── seed_abandonment.csv
│   ├── seed_radiocarbon.csv
│   ├── seed_climate.csv
│   └── __init__.py
├── src/
│   ├── db.py                    # Database connection helper
│   ├── rules.py                 # Core civilisation rules (ρ₁–ρ₄) and Ω classifier
│   └── evolution.py             # Simulation loop
├── notebooks/
│   ├── simulation.ipynb         # Run the macro‑simulation
│   └── hypothesis_testing.ipynb # Evaluate competing hypotheses
├── requirements.txt
├── README.md
└── .gitignore
```

## The fact database

The database (`caral_facts.sqlite`) follows a simple layered architecture:

| Table | Content |
|-------|---------|
| `sites` | Archaeological sites (Caral, Aspero, Vichama, etc.) |
| `sources` | Bibliographic references with DOIs |
| `observations` | Quantitative data of any type (population, monument volume, trade index, marine protein %, radiocarbon dates, abandonment years, cultural continuity index) |
| `climate_proxies` | Environmental proxies (flood frequency, drought severity) |
| `rules` | Internal civilisation rules (both the simulation rules ρ₁–ρ₄ and the six hypothesis rules ρ₅–ρ₁₀) |
| `experiments` | Two experiments: “Formation” and “Decline” |
| `discriminating_tests` | Six tests that distinguish between competing hypotheses |
| `test_results` | (to be populated by the automated validation module) |
| `logic_assertions` | Formal statements derived from test results |

Seed CSV files are provided for all tables. The database is rebuilt from scratch every time you run `build_db.py`.

## Hypothesis testing

The notebook `hypothesis_testing.ipynb` loads the database and evaluates the following hypotheses:

### Formation (ca. 3500–2600 BCE)
- **A** – Maritime priority (Moseley 1975) – largely falsified.
- **B** – Agricultural/inland priority – supported by isotope data (Pezo‑Lanfranco 2022) and radiocarbon dates.
- **C** – Parallel complementarity – not supported by current data.

### Decline (ca. 1800 BCE)
- **A** – Sudden seismic shock (Sandweiss 2009) – supported by abandonment synchrony and inland‑first timing.
- **B** – Gradual irrigation decay – not yet fully testable (needs more data).
- **C** – Megadrought + managed migration (Shady 2025) – supported by cultural continuity markers (once added).

All tests are explicit, and each conclusion is directly linked to the specific observation that supports it.

## How to add new data

1. Add rows to the relevant CSV file(s) in `database/`.
2. If needed, update `database/schema.sql` and `build_db.py` to handle new tables or observation types.
3. Rebuild the database:
   ```bash
   python database/build_db.py
   python database/seed_experiments.py
   ```
4. Re‑run the hypothesis testing notebook.

## Dependencies

- Python ≥ 3.8
- NumPy, Pandas, Matplotlib, PyYAML, Jupyter

Install with `pip install -r requirements.txt`.

## License

MIT

## Acknowledgements

This project relies on decades of fieldwork by Ruth Shady, Jonathan Haas, Winifred Creamer, David Sandweiss, and many others. The SUBIT heuristic framework was developed to organise complex historical transitions and is used here strictly as a methodological tool, not as a source of new empirical claims.