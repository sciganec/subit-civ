PRAGMA foreign_keys = ON;

-- Archaeological sites
CREATE TABLE sites (
    site_id   INTEGER PRIMARY KEY,
    name      TEXT    NOT NULL,
    latitude  REAL,
    longitude REAL
);

-- Bibliographic sources
CREATE TABLE sources (
    source_id INTEGER PRIMARY KEY,
    author    TEXT,
    year      INTEGER,
    title     TEXT,
    doi       TEXT
);

-- Derived quantitative observations (any type)
CREATE TABLE observations (
    obs_id    INTEGER PRIMARY KEY,
    site_id   INTEGER REFERENCES sites(site_id),
    source_id INTEGER REFERENCES sources(source_id),
    type      TEXT    NOT NULL,
    value     REAL    NOT NULL,
    year_from INTEGER,
    year_to   INTEGER,
    method    TEXT
);

-- Climate / environmental proxies
CREATE TABLE climate_proxies (
    proxy_id   INTEGER PRIMARY KEY,
    site_id    INTEGER REFERENCES sites(site_id),
    year       INTEGER,
    proxy_type TEXT,
    value      REAL,
    source_id  INTEGER REFERENCES sources(source_id)
);

-- Civilisation rules (ρ)
CREATE TABLE rules (
    rule_id     INTEGER PRIMARY KEY,
    name        TEXT    NOT NULL,
    description TEXT
);

-- Simulation metadata
CREATE TABLE simulation_runs (
    run_id     INTEGER PRIMARY KEY,
    timestamp  TEXT    DEFAULT (datetime('now')),
    parameters TEXT,
    notes      TEXT
);

-- Simulation trajectories
CREATE TABLE trajectories (
    traj_id  INTEGER PRIMARY KEY,
    run_id   INTEGER REFERENCES simulation_runs(run_id),
    step     INTEGER NOT NULL,
    P        REAL,
    M        REAL,
    E        REAL,
    rule     INTEGER,
    omega    TEXT
);

-- ********** НОВІ ТАБЛИЦІ ДЛЯ ДОСЛІДЖЕНЬ **********

-- Experiments (groups of hypothesis tests)
CREATE TABLE experiments (
    experiment_uuid TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    research_question TEXT,
    null_hypothesis_rule_id INTEGER REFERENCES rules(rule_id),
    alternative_hypothesis_rule_id INTEGER REFERENCES rules(rule_id)
);

-- Discriminating tests belonging to an experiment
CREATE TABLE discriminating_tests (
    test_uuid TEXT PRIMARY KEY,
    experiment_uuid TEXT REFERENCES experiments(experiment_uuid),
    description TEXT,
    expected_result_if_null TEXT,
    expected_result_if_alternative TEXT
);

-- Results of applying a test to actual data
CREATE TABLE test_results (
    result_uuid TEXT PRIMARY KEY,
    test_uuid TEXT REFERENCES discriminating_tests(test_uuid),
    observation_id INTEGER REFERENCES observations(obs_id),
    supports_hypothesis TEXT,  -- 'null', 'alternative', 'neither', 'contradictory'
    comment TEXT
);

-- Logical assertions (L6)
CREATE TABLE logic_assertions (
    assertion_uuid TEXT PRIMARY KEY,
    hypothesis_rule_id INTEGER REFERENCES rules(rule_id),
    formula TEXT NOT NULL,
    status TEXT,  -- 'supported', 'falsified', 'contradictory', 'needs_data'
    derived_from TEXT  -- JSON array of result_uuid(s)
);