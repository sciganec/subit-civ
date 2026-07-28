-- schema.sql
-- Minimal fact database for the Caral‑Supe simulation (SQLite)

-- Enable foreign key support
PRAGMA foreign_keys = ON;

------------------------------------------------------------
-- Table: sites
-- Archaeological sites related to the Caral‑Supe civilisation.
------------------------------------------------------------
CREATE TABLE sites (
    site_id   INTEGER PRIMARY KEY,
    name      TEXT    NOT NULL,
    latitude  REAL,
    longitude REAL
);

------------------------------------------------------------
-- Table: observations
-- Reconstructed quantitative observations derived from archaeological data.
-- Each row is a single measurement with a time range and method.
------------------------------------------------------------
CREATE TABLE observations (
    obs_id    INTEGER PRIMARY KEY,
    site_id   INTEGER REFERENCES sites(site_id),
    type      TEXT    NOT NULL,   -- 'population', 'monument_volume', 'trade_index'
    value     REAL    NOT NULL,
    year_from INTEGER,           -- BCE (negative) or BP
    year_to   INTEGER,
    method    TEXT
);

------------------------------------------------------------
-- Table: rules
-- Internal rules (ρ) that govern the dynamics of the system.
------------------------------------------------------------
CREATE TABLE rules (
    rule_id     INTEGER PRIMARY KEY,
    name        TEXT    NOT NULL,   -- e.g., 'irrigation_growth'
    description TEXT
);

------------------------------------------------------------
-- Table: simulation_runs
-- Metadata for each simulation run.
------------------------------------------------------------
CREATE TABLE simulation_runs (
    run_id     INTEGER PRIMARY KEY,
    timestamp  TEXT    DEFAULT (datetime('now')),
    parameters TEXT,               -- JSON snapshot of the config used
    notes      TEXT
);

------------------------------------------------------------
-- Table: trajectories
-- State of the system at each step of a simulation run.
------------------------------------------------------------
CREATE TABLE trajectories (
    traj_id  INTEGER PRIMARY KEY,
    run_id   INTEGER REFERENCES simulation_runs(run_id),
    step     INTEGER NOT NULL,
    P        REAL,                 -- population (thousands)
    M        REAL,                 -- monument volume (arbitrary units)
    E        REAL,                 -- exotic import index
    rule     INTEGER,              -- active rule (1–4)
    omega    TEXT                   -- Ω class: STABLE, METASTABLE, CYCLIC, CHAOTIC
);