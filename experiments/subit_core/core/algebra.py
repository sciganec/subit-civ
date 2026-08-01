"""
SUBIT-∞ v5.1 — algebra.py
Розділ III. АЛГЕБРА

R ≔ S₀ = 64 — простір правил
f_ρ(s): R×S₀→S₀ — перехід, s' = f_ρ(s)
g(ρ,s): R×S₀→R — метаеволюція, ρ' = g(ρ,s)
F(s,ρ) = (f_ρ(s), g(ρ,s)): S₀×R → S₀×R, |S₀×R|=4096

Формули в юнікоді:
  f_ρ(s) ≔ s ⊕ ρ — базове зсувне правило
  δ(s→t) ≔ s⊕t
  F(s,ρ) ≔ (s⊕ρ, g(ρ,s))
  id = s·64 + ρ = (s<<6) | ρ ∈ {0,…,4095}
"""

from __future__ import annotations
from typing import Callable, List, Tuple, Dict, Literal
try:
    from .s0 import S0_SIZE
    from .arith import xor, w, d_H
except ImportError:
    from s0 import S0_SIZE
    from arith import xor, w, d_H

# -------------------------------------------------------------------
# Типи
# -------------------------------------------------------------------
State = int  # 0..63
Rule = int   # 0..63, R=S₀
PairId = int # 0..4095, id = s*64 + rho

S0_SIZE = 64
PAIR_SIZE = S0_SIZE * S0_SIZE  # 4096
ALL_BITS = 0b111111  # 63

# g: (rho, s) -> rho'
GFunc = Callable[[Rule, State], Rule]
# f: (rho, s) -> s'
FFunc = Callable[[Rule, State], State]

# -------------------------------------------------------------------
# Кодування пари (s,ρ) ↔ id
# -------------------------------------------------------------------

def pair_to_id(s: State, rho: Rule) -> PairId:
    """id = s·64 + ρ = (s<<6) | ρ ∈ {0,…,4095}"""
    if not (0 <= s < 64 and 0 <= rho < 64):
        raise ValueError(f"s,rho мають бути 0..63, отримано {s},{rho}")
    return (s << 6) | rho  # s*64 + rho

def id_to_pair(id_: PairId) -> Tuple[State, Rule]:
    """id → (s,ρ)"""
    if not (0 <= id_ < 4096):
        raise ValueError(f"id має бути 0..4095")
    s = (id_ >> 6) & 0b111111
    rho = id_ & 0b111111
    return s, rho

# -------------------------------------------------------------------
# f_ρ(s) — функція переходу
# -------------------------------------------------------------------

def f_shift(rho: Rule, s: State) -> State:
    """Базове зсувне правило: f_ρ(s) = s ⊕ ρ, ρ — це δ"""
    return s ^ rho

def f_masked(rho: Rule, s: State) -> State:
    """Масковане: f = (s ∧ ¬rho) ∨ rho — проекція на rho, але в S₀ це теж XOR з маскою"""
    # залишимо як приклад, еквівалент s^rho & rho? Для елементарного ядра використовуємо shift
    return (s & (~rho & ALL_BITS)) | rho

def f_conditional(threshold: int = 2) -> FFunc:
    """Умовне: діє лише якщо w(s) ≤ threshold, інакше стоїть"""
    def f(rho: Rule, s: State) -> State:
        return (s ^ rho) if w(s) <= threshold else s
    return f

# за замовчуванням
f_default: FFunc = f_shift

# -------------------------------------------------------------------
# g(ρ,s) — функції метаеволюції
# -------------------------------------------------------------------

def g_fix(rho: Rule, s: State) -> Rule:
    """FIX — фіксоване правило: g(ρ,s)=ρ, метаеволюції нема"""
    return rho

def g_self(rho: Rule, s: State) -> Rule:
    """SELF — самозмінне: g(ρ,s)=ρ⊕s, правило вчиться на стані"""
    return rho ^ s

def g_adapt_slow(rho: Rule, s: State) -> Rule:
    """ADAPT повільне: змінюється лише на 1 біт в бік s"""
    # наймолодший біт де rho і s різняться
    diff = rho ^ s
    if diff == 0:
        return rho
    # взяти наймолодший встановлений біт diff
    lsb = diff & -diff  # isolating lsb, працює для python int
    # але нам треба біт 0..5
    # якщо diff>0, lsb — степінь двійки
    return rho ^ lsb

def g_threshold_collapse(threshold_w: int = 1, jump: int = 0b000001) -> GFunc:
    """Порогове: змінюється лише біля колапсу w(s)≤threshold_w"""
    def g(rho: Rule, s: State) -> Rule:
        if w(s) <= threshold_w:
            return rho ^ s ^ jump
        else:
            return rho
    return g

def g_odyssey() -> GFunc:
    """
    Одіссея: FIX поки w(s)≥2, SELF коли w(s)≤1
    Моделює: стабільне правило в морі, зміна правила біля колапсу
    """
    def g(rho: Rule, s: State) -> Rule:
        if w(s) <= 1:
            return rho ^ s  # почати змінювати правило
        else:
            return rho
    return g

# словник готових g
G_PRESETS: Dict[str, GFunc] = {
    "FIX": g_fix,
    "SELF": g_self,
    "ADAPT_SLOW": g_adapt_slow,
    "COLLAPSE_1": g_threshold_collapse(1, 0b000001),
    "ODYSSEY": g_odyssey(),
}

# -------------------------------------------------------------------
# F(s,ρ) = (f_ρ(s), g(ρ,s)) — спільна динаміка
# -------------------------------------------------------------------

def F(s: State, rho: Rule, f: FFunc = f_default, g: GFunc = g_fix) -> Tuple[State, Rule]:
    """Один крок алгебри: (s,ρ) → (s',ρ') = (f_ρ(s), g(ρ,s))"""
    s_next = f(rho, s)
    rho_next = g(rho, s)
    return s_next, rho_next

def F_id(id_: PairId, f: FFunc = f_default, g: GFunc = g_fix) -> PairId:
    """F на id: id → id_next"""
    s, rho = id_to_pair(id_)
    s_next, rho_next = F(s, rho, f, g)
    return pair_to_id(s_next, rho_next)

def build_F_table(f: FFunc = f_default, g: GFunc = g_fix) -> List[PairId]:
    """
    Будує таблицю F: 4096 → 4096
    F_table[id] = id_next, де id = s*64+rho
    Розмір: 4096 * 2 байти = 8KB
    """
    table = [0] * PAIR_SIZE
    for s in range(64):
        for rho in range(64):
            id_ = pair_to_id(s, rho)
            table[id_] = F_id(id_, f, g)
    return table

# -------------------------------------------------------------------
# Траєкторії
# -------------------------------------------------------------------

def trajectory(s0: State, rho0: Rule, steps: int, f: FFunc = f_default, g: GFunc = g_fix) -> List[Tuple[State, Rule]]:
    """
    Траєкторія (s₀,ρ₀) →_F (s₁,ρ₁) → … довжини steps
    Повертає список пар [(s0,rho0), (s1,rho1), …]
    """
    traj: List[Tuple[State, Rule]] = []
    s, rho = s0, rho0
    for _ in range(steps):
        traj.append((s, rho))
        s, rho = F(s, rho, f, g)
    return traj

def trajectory_states(s0: State, rho0: Rule, steps: int, f: FFunc = f_default, g: GFunc = g_fix) -> List[State]:
    """Проекція траєкторії на S₀: [s0,s1,s2,…] — видима історія"""
    return [s for s, _ in trajectory(s0, rho0, steps, f, g)]

# -------------------------------------------------------------------
# Демо / тест
# -------------------------------------------------------------------
if __name__ == "__main__":
    # 1. FIX приклад: ρ=010000₂=16, цикл довжини 2
    s0_ = 0b101010  # 42 = Я,СХІД,ВЕСНА
    rho0 = 0b010000  # 16
    print("=== FIX ρ=010000, s0=101010 ===")
    traj = trajectory(s0_, rho0, 6, f_shift, g_fix)
    for i, (s, rho) in enumerate(traj):
        print(f"  step {i}: s={s:06b}({s:2d}) rho={rho:06b} d_H={w(s ^ traj[0][0])}")

    # 2. SELF приклад: Караль — швидкий колапс
    print("\n=== SELF — Караль: s0=111111, rho0=000001 ===")
    s0_ = 0b111111  # 63 повнота
    rho0 = 0b000001  # 1 малий зсув
    traj = trajectory(s0_, rho0, 6, f_shift, g_self)
    for i, (s, rho) in enumerate(traj):
        print(f"  step {i}: s={s:06b} w={w(s)} rho={rho:06b}")

    # 3. ODYSSEY
    print("\n=== ODYSSEY: порогове g ===")
    s0_ = 0b101010
    rho0 = 0b010000
    traj = trajectory(s0_, rho0, 10, f_shift, g_odyssey())
    for i, (s, rho) in enumerate(traj):
        print(f"  step {i}: s={s:06b} w={w(s)} rho={rho:06b}")

    # 4. F_table
    table = build_F_table(f_shift, g_fix)
    print(f"\nF_table built: len={len(table)}, F[0]={table[0]}, F[4095]={table[4095]}")
    # Перевірка: з кожної вершини рівно одне ребро, всього 4096
    print(f"S₀×R = {PAIR_SIZE} пар, граф 4096→4096")

    # 5. Приклад id кодування
    s, rho = 36, 16
    id_ = pair_to_id(s, rho)
    s2, rho2 = id_to_pair(id_)
    assert (s, rho) == (s2, rho2)
    print(f"\nКодування: (s={s},rho={rho}) -> id={id_} -> ({s2},{rho2}) OK")
