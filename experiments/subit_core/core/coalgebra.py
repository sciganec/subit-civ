"""
SUBIT-∞ v5.1 — coalgebra.py
Розділ IV. КОАЛГЕБРА

H ≔ S₀^ℕ — простір історій, послідовності (s₀,s₁,…)
d_Ω(h,h') ≔ 2⁻ⁿ⁰, n₀ = min{ n | s_n≠t_n } — ультраметрика
Ω: S₀×R → {STABLE, METASTABLE, CYCLIC, CHAOTIC} — тип поведінки
S∞ — дерева Leaf a | Node(l,m,r), S₀↪S∞ як глибина 1

Формули в юнікоді:
  (s₀,ρ₀) →_F (s₁,ρ₁) →_F … , (s_{n+1},ρ_{n+1})=F(s_n,ρ_n)
  h = (s₀,s₁,…) ∈ H
  d_Ω(h,h') = {0 якщо h=h'; 2⁻ⁿ⁰ інакше}
  Ω(s₀,ρ₀) = тип історії h
"""

from __future__ import annotations
from typing import List, Tuple, Dict, Literal, Optional, Union
from dataclasses import dataclass

try:
    from .s0 import S0_SIZE
    from .arith import w, d_H, ball
    from .algebra import pair_to_id, id_to_pair, F, trajectory, PairId, State, Rule, GFunc, FFunc, f_shift, g_fix
except ImportError:
    from s0 import S0_SIZE
    from arith import w, d_H, ball
    from algebra import pair_to_id, id_to_pair, F, trajectory, PairId, State, Rule, GFunc, FFunc, f_shift, g_fix

# -------------------------------------------------------------------
# Типи поведінки Ω
# -------------------------------------------------------------------
Behavior = Literal["STABLE", "METASTABLE", "CYCLIC", "CHAOTIC"]

@dataclass(frozen=True)
class OmegaResult:
    """Результат Ω(s₀,ρ₀) — класифікація поведінки"""
    type: Behavior
    s0: State
    rho0: Rule
    attractor: State  # точка або представник циклу
    period: int       # p для CYCLIC, 1 для STABLE, len(cycle) для CHAOTIC
    preperiod: int    # μ — крок входу в цикл, N з визначення
    cycle: List[Tuple[State, Rule]]  # цикл пар (s,ρ)
    history: List[Tuple[State, Rule]]  # повна траєкторія до повтору
    # для METASTABLE
    metastable_center: Optional[State] = None
    metastable_plateau_len: int = 0

    def __repr__(self):
        return f"Ω({self.s0},{self.rho0})={self.type} pre={self.preperiod} p={self.period} attr={self.attractor:06b}"

# -------------------------------------------------------------------
# d_Ω — відстань між історіями
# -------------------------------------------------------------------

def first_divergence(h1: List[State], h2: List[State]) -> int:
    """
    n₀(h,h') = min{ n | s_n≠t_n }, ∞ якщо збігаються до min(len)
    Для нескінченних історій — перший індекс розходження
    """
    m = min(len(h1), len(h2))
    for n in range(m):
        if h1[n] != h2[n]:
            return n
    if len(h1) == len(h2):
        return 10**9  # ∞, позначаємо великим числом
    return m  # одна коротша — розходження на її довжині

def d_Omega_history(h1: List[State], h2: List[State]) -> float:
    """
    d_Ω(h,h') = 2⁻ⁿ⁰, 0 якщо h=h'
    h1,h2 — списки s, проекції траєкторій
    """
    if h1 == h2:
        return 0.0
    n0 = first_divergence(h1, h2)
    if n0 >= 10**9:
        return 0.0
    return 2.0 ** (-n0)

# -------------------------------------------------------------------
# Ω — класифікація, brute-force ≤4096 кроків
# -------------------------------------------------------------------

def omega(
    s0: State,
    rho0: Rule,
    f: FFunc = f_shift,
    g: GFunc = g_fix,
    metastable_L: int = 10,
) -> OmegaResult:
    """
    Обчислює Ω(s₀,ρ₀) — тип поведінки історії, породженої F

    Алгоритм: йдемо по F до першого повтору пари (s,ρ), макс 4096 кроків
    S₀×R скінченне → обов'язково цикл

    - STABLE: цикл довжини 1, s_{n+1}=s_n (і ρ_{n+1}=ρ_n)
    - CYCLIC: цикл довжини p≥2
    - METASTABLE: довге плато в B₁(c) ≥L кроків, потім вихід
    - CHAOTIC: довгий цикл p≫1 без плато

    metastable_L — параметр L для METASTABLE
    """
    visited: Dict[PairId, int] = {}
    hist: List[Tuple[State, Rule]] = []  # (s,rho)

    s, rho = s0, rho0
    step = 0
    while True:
        id_ = pair_to_id(s, rho)
        if id_ in visited:
            # знайшли цикл
            mu = visited[id_]  # початок циклу
            cycle = hist[mu:]  # пари в циклі
            preperiod = mu
            period = len(cycle)
            # атрактор — перший s циклу
            attractor = cycle[0][0]

            # Перевірка STABLE: period=1 і s не змінюється
            if period == 1:
                # також перевірити що s_next == s
                s_next, _ = F(s, rho, f, g)
                if s_next == s:
                    typ: Behavior = "STABLE"
                else:
                    # теоретично неможливо для FIX, але для повноти
                    typ = "STABLE"
            else:
                # перевірка METASTABLE — чи є довге плато до циклу
                meta_center, plateau_len = _find_plateau(
                    [s for s, _ in hist], metastable_L
                )
                if plateau_len >= metastable_L:
                    typ = "METASTABLE"
                    return OmegaResult(
                        type=typ,
                        s0=s0,
                        rho0=rho0,
                        attractor=attractor,
                        period=period,
                        preperiod=preperiod,
                        cycle=cycle,
                        history=hist,
                        metastable_center=meta_center,
                        metastable_plateau_len=plateau_len,
                    )
                # інакше CYCLIC vs CHAOTIC за довжиною
                if period <= 16:
                    typ = "CYCLIC"
                else:
                    typ = "CHAOTIC"

            return OmegaResult(
                type=typ,
                s0=s0,
                rho0=rho0,
                attractor=attractor,
                period=period,
                preperiod=preperiod,
                cycle=cycle,
                history=hist,
            )

        visited[id_] = step
        hist.append((s, rho))

        if step >= 4096:
            # на випадок — мало статися раніше
            return OmegaResult(
                type="CHAOTIC",
                s0=s0,
                rho0=rho0,
                attractor=s,
                period=0,
                preperiod=len(hist),
                cycle=[],
                history=hist,
            )

        s, rho = F(s, rho, f, g)
        step += 1


def _find_plateau(states: List[State], L: int) -> Tuple[Optional[State], int]:
    """
    Шукає найдовше плато: сегмент довжини ≥L де всі s ∈ B₁(center)
    Повертає (center, довжина)
    """
    if len(states) < L:
        return None, 0

    best_center = None
    best_len = 0

    # Для кожного можливого центру — центр це один з s в історії або його сусід
    # brute-force: перевірити кожне вікно L, центр = states[i]
    n = len(states)
    for i in range(n - L + 1):
        center = states[i]
        # розширити вікно поки всі в B₁(center)
        j = i
        while j < n and d_H(states[j], center) <= 1:
            j += 1
        length = j - i
        if length > best_len:
            best_len = length
            best_center = center

    return best_center, best_len

# -------------------------------------------------------------------
# S∞ — простір дерев Leaf a | Node(l,m,r)
# -------------------------------------------------------------------

@dataclass(frozen=True)
class Leaf:
    """Листок S∞ — елемент A = {0,1,2,3}, a∈A"""
    a: int  # 0..3 = ВОНИ,ТИ,Я,МИ

    def __repr__(self): return f"Leaf({self.a})"

@dataclass(frozen=True)
class Node:
    """Вузол S∞ — трійка (l,m,r), l,m,r ∈ S∞"""
    l: Union[Leaf, Node]
    m: Union[Leaf, Node]
    r: Union[Leaf, Node]

    def __repr__(self): return f"Node({self.l},{self.m},{self.r})"

# Тип S∞
SInf = Union[Leaf, Node]

def s0_to_sinf(s: State) -> Node:
    """Вкладення S₀↪S∞: (a₁,a₂,a₃) ↦ Node(Leaf a₁, Leaf a₂, Leaf a₃), глибина 1"""
    from s0 import decode as s0_decode  # локальний імпорт для незалежності

    # якщо s0 не імпортовано як модуль, використати бітові операції
    try:
        who, where, when = s0_decode(s)
    except Exception:
        who = (s >> 4) & 0b11
        where = (s >> 2) & 0b11
        when = s & 0b11
    return Node(Leaf(who), Leaf(where), Leaf(when))

def depth(t: SInf) -> Union[int, float]:
    """Глибина дерева: Leaf=0, Node=1+max(depth(children)), ∞ якщо нескінченне (не визначаємо тут)"""
    if isinstance(t, Leaf):
        return 0
    else:
        return 1 + max(depth(t.l), depth(t.m), depth(t.r))

def first_diff_depth(t1: SInf, t2: SInf) -> Union[int, float]:
    """
    Перша глибина розходження двох дерев S∞
    0 якщо корені різні за типом або Leaf a≠b, інакше 1+ min(diff дітей)
    """
    if isinstance(t1, Leaf) and isinstance(t2, Leaf):
        return 0 if t1.a != t2.a else float("inf")
    if type(t1) != type(t2):
        return 0
    # обидва Node
    assert isinstance(t1, Node) and isinstance(t2, Node)
    dl = first_diff_depth(t1.l, t2.l)
    dm = first_diff_depth(t1.m, t2.m)
    dr = first_diff_depth(t1.r, t2.r)
    d = min(dl, dm, dr)
    if d == float("inf"):
        return float("inf")
    return 1 + d

def d_sinf(t1: SInf, t2: SInf) -> float:
    """d(s,t)=2⁻ⁿ, n=перша глибина розходження, 0 якщо рівні"""
    n = first_diff_depth(t1, t2)
    if n == float("inf"):
        return 0.0
    return 2.0 ** (-n)

# -------------------------------------------------------------------
# Зручні обгортки для аналізу всіх 4096
# -------------------------------------------------------------------

def omega_all(f: FFunc = f_shift, g: GFunc = g_fix) -> Dict[Behavior, int]:
    """Статистика Ω для всіх 4096 пар (s,ρ) — скільки STABLE/CYCLIC/..."""
    counts: Dict[Behavior, int] = {"STABLE": 0, "METASTABLE": 0, "CYCLIC": 0, "CHAOTIC": 0}
    for s in range(64):
        for rho in range(64):
            res = omega(s, rho, f, g)
            counts[res.type] += 1
    return counts

# -------------------------------------------------------------------
# Демо / тест
# -------------------------------------------------------------------
if __name__ == "__main__":
    print("=== Ω STABLE — Караль ===")
    # SELF: s0=63, rho0=1 → швидкий колапс в 0
    from algebra import g_self
    res = omega(s0=63, rho0=1, f=f_shift, g=g_self)
    print(res)
    print(f"  history s: {[f'{s:06b}' for s,_ in res.history]}")
    print(f"  w: {[w(s) for s,_ in res.history]}")

    print("\n=== Ω CYCLIC — Одіссея FIX ===")
    res = omega(s0=42, rho0=16, f=f_shift, g=g_fix)
    print(res)
    print(f"  cycle len={res.period}, preperiod={res.preperiod}")
    print(f"  cycle s: {[f'{s:06b}' for s,_ in res.cycle]}")

    print("\n=== Ω METASTABLE — пошук плато ===")
    # штучний приклад: довго в B₁(0)
    res = omega(s0=0, rho0=0, f=f_shift, g=g_fix)
    print(res, "очікується STABLE")

    # приклад з ODYSSEY g
    from algebra import g_odyssey
    res = omega(s0=42, rho0=16, f=f_shift, g=g_odyssey())
    print("\nODYSSEY g:", res)

    print("\n=== d_Ω ===")
    h1 = [42, 58, 42, 58, 42]
    h2 = [42, 58, 42, 0, 0]
    print(f"h1={h1}, h2={h2}, n₀={first_divergence(h1,h2)}, d_Ω={d_Omega_history(h1,h2)} = 2^-3=0.125")

    print("\n=== S∞ ===")
    s = 36  # Я на ЗАХІД в зима
    t = s0_to_sinf(s)
    print(f"s0={s:06b} -> S∞ {t}, depth={depth(t)}")
    s2 = 37
    t2 = s0_to_sinf(s2)
    print(f"d_sinf({s},{s2}) = {d_sinf(t,t2)} — розходження на глибині 1 в WHEN, 2^-1=0.5")

    print("\n=== Статистика FIX ===")
    stats = omega_all(f_shift, g_fix)
    print(stats, "очікується багато CYCLIC/STABLE з періодом ≤2, бо f=s⊕rho")
