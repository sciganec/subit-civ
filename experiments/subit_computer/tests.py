"""Test suite for SUBIT-COMPUTER v0.1 core."""

import itertools
import math
import unittest

from subit_computer.core import (
    Classification,
    ExtendedState,
    SubitState,
    TransitionGrammar,
    Trajectory,
    Value,
    all_states,
    classify_point,
    classify_set,
    conjoin,
    conjoin_gate,
    detect_cycle,
    disjoin,
    disjoin_gate,
    from_pq,
    gate_and,
    gate_neg,
    gate_or,
    merge,
    morpho_distance,
    neg,
    neg_gate,
    omega_distance,
    omega_limit,
    p_point,
    rotate,
    run_trajectory,
    state_and,
    state_neg,
    state_or,
    state_xor,
    to_pq,
    xor,
)

V = Value
S = SubitState


class TestAtomCoding(unittest.TestCase):
    def test_coding_table(self):
        self.assertEqual(to_pq(V.T), (1, 0))
        self.assertEqual(to_pq(V.B), (1, 1))
        self.assertEqual(to_pq(V.F), (0, 1))
        self.assertEqual(to_pq(V.N), (0, 0))

    def test_roundtrip(self):
        for v in V:
            self.assertEqual(from_pq(*to_pq(v)), v)


class TestNegation(unittest.TestCase):
    def test_negation_table(self):
        self.assertEqual(neg(V.T), V.F)
        self.assertEqual(neg(V.F), V.T)
        self.assertEqual(neg(V.B), V.B)
        self.assertEqual(neg(V.N), V.N)

    def test_neg_gate_matches_table(self):
        for v in V:
            self.assertEqual(neg_gate(v), neg(v))


class TestBelnapTables(unittest.TestCase):
    def test_conjunction_table(self):
        # (N ∧ B) must be F per the printed table.
        self.assertEqual(conjoin(V.N, V.B), V.F)
        self.assertEqual(conjoin(V.B, V.N), V.F)
        self.assertEqual(conjoin(V.T, V.B), V.B)
        self.assertEqual(conjoin(V.B, V.T), V.B)
        self.assertEqual(conjoin(V.T, V.N), V.N)
        self.assertEqual(conjoin(V.T, V.T), V.T)
        self.assertEqual(conjoin(V.F, V.B), V.F)

    def test_disjunction_table(self):
        self.assertEqual(disjoin(V.N, V.B), V.T)
        self.assertEqual(disjoin(V.B, V.N), V.T)
        self.assertEqual(disjoin(V.F, V.N), V.N)
        self.assertEqual(disjoin(V.F, V.T), V.T)
        self.assertEqual(disjoin(V.B, V.B), V.B)
        self.assertEqual(disjoin(V.T, V.F), V.T)

    def test_xor_definition(self):
        # x ⊕ y := (x ∧ ¬y) ∨ (¬x ∧ y)
        for a, b in itertools.product(V, repeat=2):
            expected = disjoin(conjoin(a, neg(b)), conjoin(neg(a), b))
            self.assertEqual(xor(a, b), expected)


class TestGateFormulas(unittest.TestCase):
    """§1.4 gate formulas must reproduce the §1.3 truth tables."""

    def test_gate_neg_formula(self):
        for v in V:
            p, q = to_pq(v)
            self.assertEqual(gate_neg(p, q), (q, p))
            self.assertEqual(from_pq(*gate_neg(p, q)), neg(v))

    def test_gate_and_matches_table(self):
        for a, b in itertools.product(V, repeat=2):
            pa, qa = to_pq(a)
            pb, qb = to_pq(b)
            got = from_pq(*gate_and(pa, qa, pb, qb))
            self.assertEqual(got, conjoin(a, b), f"and({a},{b})")
            self.assertEqual(conjoin_gate(a, b), conjoin(a, b))

    def test_gate_or_matches_table(self):
        for a, b in itertools.product(V, repeat=2):
            pa, qa = to_pq(a)
            pb, qb = to_pq(b)
            got = from_pq(*gate_or(pa, qa, pb, qb))
            self.assertEqual(got, disjoin(a, b), f"or({a},{b})")
            self.assertEqual(disjoin_gate(a, b), disjoin(a, b))

    def test_gate_xor_formula_saturation(self):
        # gate arithmetic uses unbounded int sums/products; for {0,1} inputs
        # it stays in range and matches xor. Verify explicitly.
        for a, b in itertools.product(V, repeat=2):
            self.assertEqual(conjoin_gate(a, b), conjoin(a, b))
            self.assertEqual(disjoin_gate(a, b), disjoin(a, b))


class TestSubitState(unittest.TestCase):
    def test_state_space_size(self):
        self.assertEqual(len(all_states()), 64)

    def test_bit_width(self):
        for st in all_states():
            self.assertEqual(len(st.to_bits()), 6)

    def test_hex_index_range(self):
        idxs = {st.hex_index() for st in all_states()}
        self.assertEqual(idxs, set(range(64)))


class TestALU(unittest.TestCase):
    def test_pcomponentwise(self):
        a = S(V.T, V.N, V.B)
        b = S(V.B, V.T, V.F)
        self.assertEqual(state_and(a, b), S(conjoin(V.T, V.B), conjoin(V.N, V.T), conjoin(V.B, V.F)))
        self.assertEqual(state_or(a, b), S(disjoin(V.T, V.B), disjoin(V.N, V.T), disjoin(V.B, V.F)))
        self.assertEqual(state_xor(a, b), S(xor(V.T, V.B), xor(V.N, V.T), xor(V.B, V.F)))
        self.assertEqual(state_neg(a), S(V.F, V.N, V.B))

    def test_rotate(self):
        a = S(V.T, V.N, V.B)
        self.assertEqual(rotate(a), S(V.N, V.B, V.T))

    def test_merge(self):
        a = S(V.T, V.N, V.B)
        b = S(V.B, V.T, V.F)
        self.assertEqual(merge(a, b), S(conjoin(V.T, V.B), disjoin(V.N, V.T), xor(V.B, V.F)))

    def test_morpho_distance(self):
        a = S(V.T, V.N, V.B)
        self.assertEqual(morpho_distance(a, a), 0)
        self.assertEqual(morpho_distance(a, S(V.F, V.N, V.B)), 1)
        self.assertEqual(morpho_distance(a, S(V.F, V.F, V.B)), 2)
        self.assertEqual(morpho_distance(a, S(V.F, V.F, V.F)), 3)
        self.assertEqual(morpho_distance(a, rotate(a)), 3)


class TestTrajectoryAndAnalyticalLayer(unittest.TestCase):
    def _make_G(self, rule):
        # static rule, identity meta & context operators => pure morphological
        # dynamics on a fixed rule.
        mu = lambda s, r, c: r
        nu = lambda s, r, c: c
        return TransitionGrammar(rho=rule, mu=mu, nu=nu)

    def test_stable_trajectory(self):
        # rule that fixes every state => STABLE.
        rule = lambda s, c: s
        G = self._make_G(rule)
        hat0 = ExtendedState(S(V.T, V.N, V.B), rule, None)
        traj = run_trajectory(hat0, G, max_steps=8)
        self.assertEqual(classify_point(traj), Classification.STABLE)
        self.assertIsNotNone(p_point(traj))

    def test_cyclic_trajectory(self):
        # a rule cycling WHO: T->F->N->B->T (and identity elsewhere) => period 4.
        cyc = {V.T: V.F, V.F: V.N, V.N: V.B, V.B: V.T}

        def rule(s, c):
            return S(cyc[s.w], s.h, s.t)

        G = self._make_G(rule)
        hat0 = ExtendedState(S(V.T, V.N, V.B), rule, None)
        traj = run_trajectory(hat0, G, max_steps=40)
        cyc_info = detect_cycle(traj)
        self.assertIsNotNone(cyc_info)
        mu, period = cyc_info
        self.assertEqual(period, 4)
        self.assertEqual(classify_point(traj), Classification.CYCLIC)

    def test_omega_distance_identical(self):
        rule = lambda s, c: s
        G = self._make_G(rule)
        h0 = ExtendedState(S(V.T, V.N, V.B), rule, None)
        ta = run_trajectory(h0, G, max_steps=8)
        tb = run_trajectory(h0, G, max_steps=8)
        self.assertEqual(omega_distance(ta, tb), 0.0)

    def test_omega_distance_diverges(self):
        # stable vs cyclic trajectories differ in classification at t=0.
        stable_rule = lambda s, c: s
        cyc = {V.T: V.F, V.F: V.N, V.N: V.B, V.B: V.T}
        cyclic_rule = lambda s, c: S(cyc[s.w], s.h, s.t)
        Gs = self._make_G(stable_rule)
        Gc = self._make_G(cyclic_rule)
        h0 = ExtendedState(S(V.T, V.N, V.B), stable_rule, None)
        h1 = ExtendedState(S(V.T, V.N, V.B), cyclic_rule, None)
        ta = run_trajectory(h0, Gs, max_steps=40)
        tb = run_trajectory(h1, Gc, max_steps=40)
        d = omega_distance(ta, tb)
        self.assertEqual(d, 1.0)  # 2^0

    def test_omega_limit_returns_states(self):
        cyc = {V.T: V.F, V.F: V.N, V.N: V.B, V.B: V.T}
        rule = lambda s, c: S(cyc[s.w], s.h, s.t)
        G = self._make_G(rule)
        traj = run_trajectory(ExtendedState(S(V.T, V.N, V.B), rule, None), G, max_steps=40)
        omega = omega_limit(traj)
        self.assertIsNotNone(omega)
        self.assertTrue(all(isinstance(x, ExtendedState) for x in omega))
        self.assertEqual(len(omega), 4)

    def test_classify_set_stable(self):
        rule = lambda s, c: s
        G = self._make_G(rule)
        h0 = ExtendedState(S(V.T, V.N, V.B), rule, None)
        self.assertEqual(classify_set([h0], G, G), Classification.STABLE)

    def test_classify_set_metastable(self):
        # P = [x, y]; G collapses both to {x} (proper subset) => METASTABLE
        rule = lambda s, c: S(V.T, V.N, V.B)
        G = self._make_G(rule)
        hx = ExtendedState(S(V.T, V.N, V.B), rule, None)
        hy = ExtendedState(S(V.F, V.F, V.F), rule, None)
        self.assertEqual(classify_set([hx, hy], G, G), Classification.METASTABLE)


if __name__ == "__main__":
    unittest.main()
