#!/usr/bin/env python3
"""
Comprehensive integrity tests for the subit-civ project.

Verifies:
- Database schema and seed data
- Correctness of civilisation rules (ρ)
- Simulation output
- Validation module
- Logic assertion generation
"""

import unittest
import sqlite3
import os
import sys
import yaml

# Add project root to path to import source modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rules import apply_rule, meta_evolution, classify_omega
from src.evolution import run_simulation
from src.validation import run_all_tests as validation_run
from src.generate_assertions import generate as generate_assertions

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'caral_facts.sqlite')
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'caral_params.yaml')

class TestDatabaseIntegrity(unittest.TestCase):
    """Check that the fact database is correctly built and populated."""

    def setUp(self):
        self.assertTrue(os.path.exists(DB_PATH), f"Database not found at {DB_PATH}")
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row

    def tearDown(self):
        self.conn.close()

    def test_tables_exist(self):
        """All required tables should be present."""
        required_tables = [
            'sites', 'sources', 'observations', 'climate_proxies',
            'rules', 'experiments', 'discriminating_tests',
            'test_results', 'logic_assertions'
        ]
        cursor = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        existing = {row[0] for row in cursor.fetchall()}
        for table in required_tables:
            self.assertIn(table, existing, f"Missing table: {table}")

    def test_sites_count(self):
        """Should have at least the 6 seeded sites."""
        count = self.conn.execute("SELECT COUNT(*) FROM sites").fetchone()[0]
        self.assertGreaterEqual(count, 6)

    def test_sources_count(self):
        count = self.conn.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
        self.assertGreaterEqual(count, 5)

    def test_observations_count(self):
        """Check that all observation types are present."""
        types = [row[0] for row in self.conn.execute(
            "SELECT DISTINCT type FROM observations"
        ).fetchall()]
        expected = [
            'population', 'monument_volume', 'trade_index',
            'marine_protein_%', 'abandonment_year', 'founding_year',
            'earliest_radiocarbon_date', 'cultural_continuity_index'
        ]
        for t in expected:
            self.assertIn(t, types, f"Missing observation type: {t}")

    def test_rules_have_hypotheses(self):
        """Rules 6 (agricultural_primacy) and 10 (megadrought_migration) must exist."""
        rule_ids = [row[0] for row in self.conn.execute(
            "SELECT rule_id FROM rules"
        ).fetchall()]
        self.assertIn(6, rule_ids)
        self.assertIn(10, rule_ids)

    def test_experiments_and_tests(self):
        """Two experiments and exactly six discriminating tests."""
        exp_count = self.conn.execute("SELECT COUNT(*) FROM experiments").fetchone()[0]
        test_count = self.conn.execute("SELECT COUNT(*) FROM discriminating_tests").fetchone()[0]
        self.assertEqual(exp_count, 2)
        self.assertEqual(test_count, 6)

class TestRules(unittest.TestCase):
    """Verify rule functions work correctly."""

    @classmethod
    def setUpClass(cls):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            cls.params = yaml.safe_load(f)

    def test_apply_rule_basic(self):
        """Rule 1 should increase population and create some monuments."""
        P, M, E = apply_rule(5.0, 1.0, 0.0, rule=1, stress=0, params=self.params)
        self.assertGreater(P, 5.0)
        self.assertGreater(M, 1.0 * (1 - self.params['rules']['spring']['M_decay']))

    def test_meta_evolution_triggers(self):
        """Check that rule transition occurs at population threshold."""
        new_rule = meta_evolution(1, P=9.0, M=1.0, E=0.0, step=10, stress=0, params=self.params)
        self.assertEqual(new_rule, 2)

    def test_classify_omega(self):
        """Rule 4 or low population should return CHAOTIC."""
        self.assertEqual(classify_omega(1.0, 0.0, 0.0, rule=4), "CHAOTIC")
        self.assertEqual(classify_omega(3.0, 1.0, 0.0, rule=2), "CHAOTIC")  # P < 5

class TestSimulation(unittest.TestCase):
    """End-to-end simulation test."""

    @classmethod
    def setUpClass(cls):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            cls.params = yaml.safe_load(f)
        # Predefine stress steps for the test
        cls.stress_steps = cls.params['climate_stress_steps']

    def _stress_func(self, step):
        """Helper method instead of lambda to avoid 'self' issues."""
        return 1 if step in self.stress_steps else 0

    def test_simulation_runs(self):
        """Simulation should return exactly 'steps' rows."""
        traj = run_simulation(self.params, self._stress_func)
        self.assertEqual(len(traj), self.params['simulation']['steps'])
        # Check first and last rows
        first = traj[0]
        self.assertEqual(first[0], 0)          # step
        self.assertGreater(first[1], 0)        # P > 0
        last = traj[-1]
        self.assertEqual(last[0], self.params['simulation']['steps'] - 1)

class TestValidationAndLogic(unittest.TestCase):
    """Ensure validation and assertion generation run without errors."""

    def test_validation_completes(self):
        """run_all_tests should not raise exceptions."""
        try:
            validation_run()
        except Exception as e:
            self.fail(f"Validation failed with error: {e}")

    def test_assertions_generated(self):
        """After validation, generate_assertions should create new logic records."""
        generate_assertions()
        conn = sqlite3.connect(DB_PATH)
        count = conn.execute("SELECT COUNT(*) FROM logic_assertions").fetchone()[0]
        conn.close()
        self.assertGreaterEqual(count, 2, "Expected at least 2 logic assertions")

if __name__ == '__main__':
    unittest.main(verbosity=2)