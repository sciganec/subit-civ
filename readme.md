# subit-civ

**From simulation to reproducible hypothesis testing: Caral‑Supe civilisation (Peru, 3500–1800 BCE) powered by a fact‑based database and the SUBIT heuristic framework.**

## Overview

`subit-civ` is an open‑source computational platform that combines:

- a curated **SQLite fact database** of published archaeological data,
- a **macro‑simulation** of societal dynamics with internal rule changes,
- an automated **hypothesis‑testing engine** that evaluates competing historical mechanisms,
- **counterfactual simulations** that compare alternative trajectories,
- a **provenance‑aware layered architecture** that traces every logical assertion back to its primary sources.

The platform is designed as a **reproducible research infrastructure** for formal hypothesis testing in archaeology. It is built around the **SUBIT heuristic framework** (see the [SUBIT specification](docs/SUBIT_specification.md)) and is currently instantiated for the Caral‑Supe civilisation, the earliest known state in the Americas.

## Key Features

- **Fact database** with 30+ quantitative observations (population, isotopes, radiocarbon dates, abandonment years, cultural continuity indices) from peer‑reviewed sources.
- **Six competing hypotheses** formalised as evolution rules (ρ) and evaluated against six discriminating tests.
- **Macro‑simulation** of the civilisation’s trajectory under baseline and counterfactual rules, with an Ω‑stability classifier.
- **Automated validation** that populates a `test_results` table and generates logical assertions.
- **Full integrity test suite** (12 tests) that verifies the database, rules, simulation, validation, and assertion modules.
- **Reproducibility** – the entire workflow (database build, simulation, hypothesis testing, figures) can be reproduced with a few terminal commands.

## Quickstart

1. **Clone the repository and enter the folder**
   ```bash
   git clone https://github.com/sciganec/subit-civ.git
   cd subit-civ
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Build the fact database and seed experiments**
   ```bash
   python database/build_db.py
   python database/seed_experiments.py
   ```
   This creates `caral_facts.sqlite` containing sites, observations, climate proxies, rules, experiments, and discriminating tests.

4. **Run the notebooks**
   ```bash
   jupyter notebook
   ```
   - `notebooks/simulation.ipynb` – baseline population, monument, trade, and Ω‑class trajectory.
   - `notebooks/hypothesis_testing.ipynb` – evaluation of the six competing hypotheses.
   - `notebooks/counterfactual.ipynb` – comparison of alternative decline scenarios.

5. **(Optional) Generate figures for the paper**
   ```bash
   python generate_figures.py
   ```
   Produces `outputs/fig1_architecture.png`, `fig2_simulation.png`, and `fig3_counterfactual.png`.

6. **Run the integrity tests**
   ```bash
   python tests/run_tests.py
   ```
   All 12 tests should pass, confirming the system’s correctness.

## Project Structure

```
subit-civ/
├── config/
│   └── caral_params.yaml           # Simulation parameters
├── database/
│   ├── schema.sql                  # Database schema (L-1 to L6)
│   ├── build_db.py                 # Creates caral_facts.sqlite from CSV seeds
│   ├── seed_experiments.py         # Populates experiments, hypotheses, tests
│   ├── seed_*.csv                  # Curated data files
│   └── __init__.py
├── src/
│   ├── db.py                       # Database connection helper
│   ├── rules.py                    # Evolution rules (ρ₁–ρ₄, ρ₆, ρ₁₀) & Ω classifier
│   ├── evolution.py                # Simulation loop
│   ├── validation.py               # Automated hypothesis evaluation
│   └── generate_assertions.py      # Generates logic assertions from test results
├── notebooks/
│   ├── simulation.ipynb            # Baseline simulation & archaeological comparison
│   ├── hypothesis_testing.ipynb    # Formal hypothesis testing (6 tests)
│   └── counterfactual.ipynb        # Counterfactual trajectories (rule 6, rule 10)
├── tests/
│   └── run_tests.py                # Integrity test suite (12 tests)
├── generate_figures.py             # Generates publication‑ready figures
├── outputs/                        # Generated figures (not tracked)
├── docs/
│   ├── SUBIT_specification.md      # Full SUBIT formal specification
│   └── paper_caral_supe.md         # Draft of the Caral‑Supe research paper
├── requirements.txt
├── README.md
└── .gitignore
```

## The Fact Database

The core database (`caral_facts.sqlite`) follows a provenance‑aware layered architecture:

| Layer | Content |
|-------|---------|
| **L-1** | Data provenance (datasets, extractions) |
| **L0** | Bibliographic sources with DOIs |
| **L1** | Archaeological facts (sites, artifacts, radiocarbon) |
| **L2** | Derived observations (population, isotopes, abandonment dates) |
| **L3** | SUBIT projection (rules, states, Ω‑classes) |
| **L4** | Simulation runs and trajectories |
| **L5** | Validation (comparisons, summaries) |
| **L6** | Logical assertions (formal conclusions) |

The database is fully rebuildable from CSV seed files; all observations are linked to their sources via foreign keys.

## The SUBIT Heuristic Framework

SUBIT (*Semantic Universe of Binary‑Interpreted Triads*) is a formal notation for describing the dynamics of complex historical systems. A state is a triple **WHO‑WHERE‑WHEN** plus an internal evolution rule **ρ**. The operator **F(s, ρ) = (fρ(s), g(ρ, s))** simultaneously updates the state and the rule, enabling metaevolution. The Ω‑classifier labels sets of states as **stable**, **metastable**, **cyclic**, or **chaotic**, and truth is defined as stability under evolution.

In this project, SUBIT is used strictly as a heuristic scaffolding tool: it forces the researcher to formulate each hypothesis as an explicit rule with an explicit empirical prediction. The full specification is available in [docs/SUBIT_specification.md](docs/SUBIT_specification.md).

## Hypothesis Testing

The platform evaluates six competing hypotheses about the formation and decline of Caral‑Supe:

### Formation (ca. 3500–2600 BCE)
- **A** – Maritime priority (Moseley 1975) – falsified.
- **B** – Agricultural/inland priority – **supported by 3/3 tests** (isotopic, demographic, radiometric).
- **C** – Parallel complementarity – not supported.

### Decline (ca. 1800 BCE)
- **A** – Sudden seismic shock (Sandweiss 2009) – not supported as the sole cause.
- **B** – Gradual irrigation decay – insufficient data.
- **C** – Megadrought + managed migration (Shady 2025) – **supported by 3/3 tests**, including cultural continuity at Vichama.

All test results are stored in the `test_results` table, and formal logical assertions are automatically generated.

## Simulation & Counterfactuals

The baseline simulation reproduces the general archaeological trajectory: a logistic rise to ~19 000 people, sustained monumentality, and a sharp collapse under the standard `winter` rule.

Counterfactual simulations show that:
- An **agricultural primacy** rule (ρ₆) produces a nearly identical early phase, confirming that agriculture alone suffices.
- A **managed migration** rule (ρ₁₀) stabilises the population at ~40 % of the peak, fitting the late‑phase archaeological estimates better than a full collapse (Ω = METASTABLE vs. CHAOTIC).

## Integrity Tests

The test suite (`tests/run_tests.py`) verifies:
- presence of all required database tables,
- correctness of seed data counts,
- rule functions, meta‑evolution triggers, and Ω‑classification,
- simulation length and output,
- validation and assertion generation.

Run it with `python tests/run_tests.py` – all 12 tests should pass.

## License

MIT