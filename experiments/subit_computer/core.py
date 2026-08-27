"""
SUBIT-COMPUTER v0.1 — reference implementation of the computational core.

A faithful, mechanical translation of «SUBIT-COMPUTER SPECIFICATION v0.1».
Aligned with SUBIT-∞ v5.2 (SUBIT-64 ⊂ SUBIT⁺ ⊂ SUBIT-TOPOS ⊂ SUBIT_∞).

Design notes (deviations from a naive transcription are flagged inline):
  * The (p, q) gate formulas of §1.4 are implemented verbatim and cross-checked
    against the Belnap tables of §1.3 — they must agree.
  * d_M is defined on S0 only (§5.1); the claim in §7.4 that
    (S0 × R × C, d_M) is ultrametric is NOT asserted — see REVIEW.md.
  * Ω is implemented conservatively on a bounded observed run: fixed point =>
    STABLE, detected cycle length > 1 => CYCLIC, otherwise => CHAOTIC / BOT
    when the resource bound is exhausted.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from functools import total_ordering
from typing import Callable, List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# §1. SUBIT Atom
# ---------------------------------------------------------------------------


class Value(Enum):
    """A = {T, F, B, N} — four-valued Belnap atom."""

    T = "T"
    F = "F"
    B = "B"
    N = "N"


# Semantic realisation isomorphic (but not identical) to A.
SEMANTIC = {Value.T: "ME", Value.F: "WE", Value.B: "YOU", Value.N: "THEY"}


# (p, q) physical coding — §1.4
_CODING = {
    Value.T: (1, 0),
    Value.B: (1, 1),
    Value.F: (0, 1),
    Value.N: (0, 0),
}

# reverse lookup
_DECODING = {v: k for k, v in _CODING.items()}


def to_pq(v: Value) -> Tuple[int, int]:
    return _CODING[v]


def from_pq(p: int, q: int) -> Value:
    return _DECODING[(int(p), int(q))]


# --- Logical operations on A (§1.3) -----------------------------------------

def neg(v: Value) -> Value:
    return {Value.T: Value.F, Value.F: Value.T, Value.B: Value.B, Value.N: Value.N}[v]


# Belnap conjunction table (§1.3), rows = left operand, cols = right operand.
# Index order F, N, T, B to match the printed tables.
_ORDER = [Value.F, Value.N, Value.T, Value.B]

_AND = {
    (Value.F, Value.F): Value.F, (Value.F, Value.N): Value.F, (Value.F, Value.T): Value.F, (Value.F, Value.B): Value.F,
    (Value.N, Value.F): Value.F, (Value.N, Value.N): Value.N, (Value.N, Value.T): Value.N, (Value.N, Value.B): Value.F,
    (Value.T, Value.F): Value.F, (Value.T, Value.N): Value.N, (Value.T, Value.T): Value.T, (Value.T, Value.B): Value.B,
    (Value.B, Value.F): Value.F, (Value.B, Value.N): Value.F, (Value.B, Value.T): Value.B, (Value.B, Value.B): Value.B,
}

_OR = {
    (Value.F, Value.F): Value.F, (Value.F, Value.N): Value.N, (Value.F, Value.T): Value.T, (Value.F, Value.B): Value.B,
    (Value.N, Value.F): Value.N, (Value.N, Value.N): Value.N, (Value.N, Value.T): Value.T, (Value.N, Value.B): Value.T,
    (Value.T, Value.F): Value.T, (Value.T, Value.N): Value.T, (Value.T, Value.T): Value.T, (Value.T, Value.B): Value.T,
    (Value.B, Value.F): Value.B, (Value.B, Value.N): Value.T, (Value.B, Value.T): Value.T, (Value.B, Value.B): Value.B,
}


def conjoin(a: Value, b: Value) -> Value:
    return _AND[(a, b)]


def disjoin(a: Value, b: Value) -> Value:
    return _OR[(a, b)]


def xor(a: Value, b: Value) -> Value:
    """x ⊕ y := (x ∧ ¬y) ∨ (¬x ∧ y)."""
    return disjoin(conjoin(a, neg(b)), conjoin(neg(a), b))


# --- Gate-level implementation via (p, q) formulas (§1.4) --------------------
# These must reproduce the table-based operations above — verified in tests.

def gate_neg(p: int, q: int) -> Tuple[int, int]:
    return q, p


def gate_and(pa: int, qa: int, pb: int, qb: int) -> Tuple[int, int]:
    """§1.4: p_out(∧)=p_a·p_b, q_out(∧)=q_a+q_b.

    Note: `+` and `·` are *Boolean* (digital-logic) operators over the
    Boolean semiring {0,1} — `+` is OR (max), `·` is AND (min). Read as
    plain integer arithmetic they overflow (e.g. q_a=q_b=1 => 2) and fail to
    reproduce the §1.3 truth tables. See REVIEW.md §2.
    """
    return pa & pb, qa | qb


def gate_or(pa: int, qa: int, pb: int, qb: int) -> Tuple[int, int]:
    """§1.4: p_out(∨)=p_a+p_b, q_out(∨)=q_a·q_b (Boolean operators)."""
    return pa | pb, qa & qb


def neg_gate(v: Value) -> Value:
    p, q = to_pq(v)
    return from_pq(*gate_neg(p, q))


def conjoin_gate(a: Value, b: Value) -> Value:
    pa, qa = to_pq(a)
    pb, qb = to_pq(b)
    return from_pq(*gate_and(pa, qa, pb, qb))


def disjoin_gate(a: Value, b: Value) -> Value:
    pa, qa = to_pq(a)
    pb, qb = to_pq(b)
    return from_pq(*gate_or(pa, qa, pb, qb))


# ---------------------------------------------------------------------------
# §2. SUBIT-64 State
# ---------------------------------------------------------------------------

WHO, WHERE, WHEN = 0, 1, 2


@dataclass(frozen=True)
class SubitState:
    """s = (w, h, t) ∈ A^3 = S0."""

    w: Value
    h: Value
    t: Value

    def component(self, i: int) -> Value:
        return (self.w, self.h, self.t)[i]

    def as_tuple(self) -> Tuple[Value, Value, Value]:
        return (self.w, self.h, self.t)

    def to_bits(self) -> Tuple[int, ...]:
        """Six physical bits (pw, qw, ph, qh, pt, qt)."""
        out: List[int] = []
        for c in self.as_tuple():
            p, q = to_pq(c)
            out.extend((p, q))
        return tuple(out)

    def hex_index(self) -> int:
        """Index into the 64-state space (0..63)."""
        idx = 0
        for c in self.as_tuple():
            idx = idx * 4 + _ORDER.index(c)
        return idx


def all_states() -> List[SubitState]:
    return [SubitState(a, b, c) for a in Value for b in Value for c in Value]


# ---------------------------------------------------------------------------
# §3. Extended State  &  §4. Transition Grammar
# ---------------------------------------------------------------------------

Context = object  # opaque; v0.1 allows empty / finite history / horizon counter

# A rule rho : S0 × C -> S0
Rule = Callable[[SubitState, Context], SubitState]
# A meta-operator mu : (s, rho, c) -> rho'
MetaOp = Callable[[SubitState, Rule, Context], Rule]
# A context operator nu : (s, rho, c) -> c'
CtxtOp = Callable[[SubitState, Rule, Context], Context]


@dataclass
class ExtendedState:
    """Ŝ = (S, R, C)."""

    s: SubitState
    rho: Rule
    c: Context


@dataclass
class TransitionGrammar:
    """G(Ŝ) = (s', rho', c') with s'=ρ(s,c), ρ'=μ(s,ρ,c), c'=ν(s,ρ,c)."""

    rho: Rule
    mu: MetaOp
    nu: CtxtOp

    def __call__(self, hat: ExtendedState) -> ExtendedState:
        s, rho, c = hat.s, hat.rho, hat.c
        s_new = rho(s, c)
        rho_new = self.mu(s, rho, c)
        c_new = self.nu(s, rho, c)
        return ExtendedState(s_new, rho_new, c_new)


# ---------------------------------------------------------------------------
# §5. SUBIT-ALU
# ---------------------------------------------------------------------------


def state_neg(a: SubitState) -> SubitState:
    return SubitState(neg(a.w), neg(a.h), neg(a.t))


def state_and(a: SubitState, b: SubitState) -> SubitState:
    return SubitState(conjoin(a.w, b.w), conjoin(a.h, b.h), conjoin(a.t, b.t))


def state_or(a: SubitState, b: SubitState) -> SubitState:
    return SubitState(disjoin(a.w, b.w), disjoin(a.h, b.h), disjoin(a.t, b.t))


def state_xor(a: SubitState, b: SubitState) -> SubitState:
    return SubitState(xor(a.w, b.w), xor(a.h, b.h), xor(a.t, b.t))


def project(a: SubitState, i: int) -> Value:
    return a.component(i)


def rotate(a: SubitState) -> SubitState:
    """ROTATE(A) := (a_h, a_t, a_w)."""
    return SubitState(a.h, a.t, a.w)


def merge(a: SubitState, b: SubitState) -> SubitState:
    """MERGE := (a_w ∧ b_w, a_h ∨ b_h, a_t ⊕ b_t)."""
    return SubitState(conjoin(a.w, b.w), disjoin(a.h, b.h), xor(a.t, b.t))


def split(a: SubitState) -> Tuple[Value, Value, Value]:
    return a.w, a.h, a.t


def morpho_distance(a: SubitState, b: SubitState) -> int:
    """d_M := #{i : a_i ≠ b_i}."""
    return sum(1 for i in (WHO, WHERE, WHEN) if a.component(i) != b.component(i))


def transition(s: SubitState, rho: Rule, c: Context, G: TransitionGrammar) -> SubitState:
    return G(ExtendedState(s, rho, c)).s


# ---------------------------------------------------------------------------
# §6. Trajectory Model
# ---------------------------------------------------------------------------


@dataclass
class Trajectory:
    states: List[ExtendedState] = field(default_factory=list)

    def __iter__(self):
        return iter(self.states)

    def tail(self, k: int) -> "Trajectory":
        return Trajectory(self.states[k:])

    def __len__(self) -> int:
        return len(self.states)


def run_trajectory(
    hat0: ExtendedState,
    G: TransitionGrammar,
    max_steps: int,
) -> Trajectory:
    """Generate τ(Ŝ0) = (Ŝ0, Ŝ1, …) bounded by max_steps (resource bound)."""
    traj = [hat0]
    cur = hat0
    for _ in range(max_steps):
        cur = G(cur)
        traj.append(cur)
        # early stop on a fixed point of the extended state
        if _hat_key(cur) == _hat_key(traj[0]):
            pass  # keep going; cycle detection handled analytically
    return Trajectory(traj)


def _hat_key(hat: ExtendedState):
    # Rules are callable and may not be hashable; use id() for identity.
    return (hat.s, id(hat.rho), id(hat.c))


def fixed_points(G: TransitionGrammar, space: Sequence[ExtendedState]) -> List[ExtendedState]:
    """Fix(G) = { Ŝ : G(Ŝ) = Ŝ }."""
    out = []
    for hat in space:
        nxt = G(hat)
        if nxt.s == hat.s and id(nxt.rho) == id(hat.rho) and id(nxt.c) == id(hat.c):
            out.append(hat)
    return out


# ---------------------------------------------------------------------------
# §7. Analytical Layer
# ---------------------------------------------------------------------------


class Classification(Enum):
    STABLE = "STABLE"
    METASTABLE = "METASTABLE"
    CYCLIC = "CYCLIC"
    CHAOTIC = "CHAOTIC"
    BOT = "BOT"  # ⊥


# Heyting-algebra order (§7.4): CHAOTIC < CYCLIC < METASTABLE < STABLE
_HEYT_ORDER = {
    Classification.CHAOTIC: 0,
    Classification.CYCLIC: 1,
    Classification.METASTABLE: 2,
    Classification.STABLE: 3,
}


def detect_cycle(traj: Trajectory) -> Optional[Tuple[int, int]]:
    """Floyd-style detection on the *extended-state* identity of a bounded run.

    The spec's trajectory is over extended states Ŝ = (s, ρ, c); a genuine cycle
    requires the full extended state to recur. (When μ, ν are identity operators
    this reduces to morphological recurrence, as in the tests.)

    Returns (mu, period) where mu = first index inside the cycle, period = k>0
    such that Ŝ_{t+k} == Ŝ_t for all t >= mu. Returns None if no cycle is found
    within the observed run.
    """
    n = len(traj)
    if n == 0:
        return None
    keys = [_hat_key(h) for h in traj.states]
    seen = {}
    for i, k in enumerate(keys):
        if k in seen:
            mu = seen[k]
            period = i - mu
            ok = True
            for t in range(mu, n - period):
                if keys[t] != keys[t + period]:
                    ok = False
                    break
            if ok:
                return mu, period
        seen[k] = i
    return None


def omega_limit(traj: Trajectory) -> Optional[List[ExtendedState]]:
    """ω(Ŝ0) — extended states visited infinitely often.

    For a finite bounded run this reduces to the cycle members, or the
    terminal fixed point. Returns None (=> P(τ)=⊥) if no cycle is detected.
    Returns a list of `ExtendedState` objects (deduplicated by canonical key,
    since ExtendedState holds unhashable rule/context callables).
    """
    cyc = detect_cycle(traj)
    if cyc is None:
        return None
    mu, period = cyc
    seen = set()
    out = []
    for i in range(mu, mu + period):
        h = traj.states[i]
        k = _hat_key(h)
        if k not in seen:
            seen.add(k)
            out.append(h)
    return out


def p_point(traj: Trajectory) -> Optional[ExtendedState]:
    """P_pt(τ) := { Ŝ_{m(Ŝ0)} } — entry point into the ω-limit."""
    cyc = detect_cycle(traj)
    if cyc is None:
        return None
    mu, _ = cyc
    return traj.states[mu]


def classify_point(traj: Trajectory) -> Classification:
    """Conservative Ω over a bounded observed trajectory."""
    cyc = detect_cycle(traj)
    if cyc is None:
        return Classification.BOT  # resource bound exhausted / ⊥
    mu, period = cyc
    if period == 1:
        return Classification.STABLE
    return Classification.CYCLIC


def classify_set(P, G: TransitionGrammar, image_of: Callable[[ExtendedState], ExtendedState]) -> Classification:
    """Ω over an explicitly supplied finite collection P of extended states.

    `image_of` maps each element to G(element); provided so the caller
    controls how G acts on sets. Comparison is by canonical extended-state key
    (not object identity), so freshly constructed equal states compare equal.
    """
    P = list(P)
    if not P:
        return Classification.BOT
    keys_P = {_hat_key(x) for x in P}
    images = {_hat_key(image_of(x)) for x in P}
    if images == keys_P:
        return Classification.STABLE
    if images < keys_P:  # proper subset => image shrinks
        return Classification.METASTABLE
    return Classification.CHAOTIC


def omega_distance(traj_a: Trajectory, traj_b: Trajectory, max_t: int = 10_000) -> object:
    """d_Ω(τ, σ) — semantic ultrametric.

    Returns a float in [0, 1] (0 = identical classification tail), or
    Classification.BOT (⊥) if either classifier is undefined at the
    divergence point.
    """
    for t in range(max_t):
        ta = traj_a.tail(t) if t < len(traj_a) else None
        tb = traj_b.tail(t) if t < len(traj_b) else None
        if ta is None or tb is None:
            return Classification.BOT
        ca, cb = classify_point(ta), classify_point(tb)
        if ca == Classification.BOT or cb == Classification.BOT:
            return Classification.BOT
        if ca != cb:
            return 2 ** (-t)
        # Definitive classifications are tail-invariant: a fixed point stays
        # STABLE and a cycle's tail stays CYCLIC. Equal + definitive => the
        # infinite tails agree, so d_Ω == 0.
        if ca in (Classification.STABLE, Classification.CYCLIC):
            return 0.0
    return 0.0


__all__ = [
    "Value", "SEMANTIC", "to_pq", "from_pq",
    "neg", "conjoin", "disjoin", "xor",
    "gate_neg", "gate_and", "gate_or", "neg_gate", "conjoin_gate", "disjoin_gate",
    "SubitState", "all_states", "WHO", "WHERE", "WHEN",
    "ExtendedState", "TransitionGrammar", "Rule", "MetaOp", "CtxtOp",
    "state_neg", "state_and", "state_or", "state_xor",
    "project", "rotate", "merge", "split", "morpho_distance", "transition",
    "Trajectory", "run_trajectory", "fixed_points",
    "Classification", "detect_cycle", "omega_limit", "p_point",
    "classify_point", "classify_set", "omega_distance",
]
