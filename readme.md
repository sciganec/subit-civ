# subit-civ

**Minimal simulation of the Caral‑Supe civilization powered by a fact‑based database.**

## Overview

`subit-civ` is a lightweight, reproducible research tool that combines  
archaeological data, mathematical rules of societal change, and  
interactive visualisation to explore the dynamics of the **Caral‑Supe**  
civilisation (Norte Chico, Peru, c. 3500–1800 BCE).

The project grew out of the **SUBIT** formal framework (WHO‑WHERE‑WHEN  
states, internal rules ρ, and a stability classifier Ω) but remains  
self‑contained: you can run the simulation, inspect the fact database,  
and compare results against published population estimates without  
any prior knowledge of SUBIT.

## Quickstart

1. **Clone and enter the repository**  
   ```bash
   git clone https://github.com/sciganec/subit‑civ.git
   cd subit‑civ
   ```

2. **Create a virtual environment and install dependencies**  
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Build the local fact database**  
   ```bash
   python database/build_db.py
   ```
   This creates `caral_facts.sqlite` and populates it with the seed data
   (sites, population observations, climate stress indicators).

4. **Launch the simulation notebook**  
   ```bash
   jupyter notebook notebooks/simulation.ipynb
   ```
   Follow the cells to load the configuration, run the simulation, and
   produce plots of population, monument volume, trade intensity, and
   Ω‑stability class through time.

## What’s inside

- **Fact database** – A minimal SQLite store that holds archaeological
  sites (`Caral`, `Aspero`), derived observations (population,
  monument volume, trade index), and the four civilisation‑phase rules
  (ρ₁ – ρ₄).
- **Simulation engine** – A deterministic, macro‑level model that
  implements the four internal rules and the meta‑evolution function
  that switches between them.
- **Validation** – The simulation output is automatically compared
  against 95% confidence intervals of the observed population data,
  giving you a quick sense of model fit.
- **Exploratory notebook** – The entry point for visual analysis,
  ready to be extended with counter‑factual experiments or additional
  variables.

## Project structure

```
subit‑civ/
├── config/
│   └── caral_params.yaml       # All simulation parameters
├── database/
│   ├── schema.sql              # Database tables
│   ├── seed_sites.csv          # Archaeological site metadata
│   ├── seed_population.csv     # Population estimates with time ranges
│   └── build_db.py             # Script that creates caral_facts.sqlite
├── src/
│   ├── db.py                   # Database connection helper
│   ├── rules.py                # The four rules ρ₁–ρ₄ and meta‑evolution
│   └── evolution.py            # Main simulation loop
├── notebooks/
│   └── simulation.ipynb        # Interactive simulation & validation
├── requirements.txt
├── README.md
└── .gitignore
```

## Dependencies

- Python ≥ 3.8
- NumPy
- Pandas
- Matplotlib
- PyYAML
- Jupyter

All packages are listed in `requirements.txt`.

## How the simulation works

The Caral‑Supe civilisation is modelled as a system that passes through
four seasonal phases:

| Phase   | Rule    | Description                               |
|---------|---------|-------------------------------------------|
| SPRING  | ρ₁      | Irrigation‑driven population growth       |
| SUMMER  | ρ₂      | Monumental cooperation & trade            |
| AUTUMN  | ρ₃      | Trade compensation under environmental stress |
| WINTER  | ρ₄      | System collapse and dispersal             |

At each 25‑year step, the active rule updates three state variables:

- **P** – population (thousands)
- **M** – monument volume (arbitrary units)
- **E** – exotic import index (arbitrary units)

When a threshold is crossed, the meta‑evolution function **g** switches
to the next rule. External climate stress (El Niño events) can be
injected at specific time steps.

The Ω‑stability classifier labels each state as `STABLE`, `METASTABLE`,
`CYCLIC`, or `CHAOTIC` based on the trajectory of the system.

## Future plans

- Expand the database to the full multi‑layer architecture (L‑1 to L6)
- Add logical assertions and provenance tracking
- Support counter‑factual experiments via an experiment registry
- Extend to other early civilisations (e.g., Egypt, Harappa)

## License

MIT