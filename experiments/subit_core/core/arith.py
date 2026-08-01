"""
SUBIT-∞ v5.1 — arith.py
Розділ II. АРИФМЕТИКА

(S₀, ⊕) ≅ V₄³ ≅ ℤ₂⁶, |S₀|=64
Операції: ⊕=XOR, w=popcount, d_H=w(s⊕t), inv=s⊕111111
Ґратка: ∧=AND, ∨=OR, ¬=inv
Порядок: lex = 0..63, Gray = гамільтонів цикл по Q₆

Формули в юнікоді:
  s ⊕ t ≔ s XOR t, e=000000₂
  w(s) ≔ popcount(s) = Σ bᵢ ∈ {0,…,6}
  d_H(s,t) ≔ w(s⊕t)
  inv(s) ≔ s ⊕ 111111₂
  B_r(s) ≔ { t | d_H(s,t) ≤ r }
"""

from __future__ import annotations
from typing import List, Set, Tuple
try:
    from .s0 import S0_SIZE  # type: ignore
except ImportError:
    from s0 import S0_SIZE  # type: ignore

# Константи
ALL_BITS = 0b111111  # 63 = ⊤ = (МИ,ПІВДЕНЬ,ЛІТО)
E = 0b000000  # ⊥ = (ВОНИ,ПІВНІЧ,ЗИМА) = нейтральний для ⊕

# -------------------------------------------------------------------
# Група V₄³
# -------------------------------------------------------------------

def xor(s: int, t: int) -> int:
    """s ⊕ t — групова операція, побітовий XOR, V₄³ ≅ ℤ₂⁶"""
    return s ^ t

# аліас для читабельності
oplus = xor

def neg(s: int) -> int:
    """-s = s, бо група експоненти 2, s⊕s=e"""
    return s

def sub(s: int, t: int) -> int:
    """s⊖t = s⊕t, бо віднімання = додаванню"""
    return s ^ t

def shift(s: int, t: int) -> int:
    """δ(s→t) ≔ s⊕t — семантичний зсув від s до t, t = s⊕δ"""
    return s ^ t

# -------------------------------------------------------------------
# Вага та відстань Хеммінга
# -------------------------------------------------------------------

def w(s: int) -> int:
    """Вага w(s) = popcount(s) ∈ {0,…,6}, кількість одиниць"""
    # Python 3.8+ : bin, 3.10+ : int.bit_count()
    try:
        return s.bit_count()  # type: ignore
    except AttributeError:
        return bin(s).count("1")

def d_H(s: int, t: int) -> int:
    """Відстань Хеммінга d_H(s,t) = w(s⊕t) ∈ {0,…,6}"""
    return w(s ^ t)

def is_neighbor(s: int, t: int) -> bool:
    """Чи d_H(s,t)=1 — чи t ∈ S₁(s), ребро гіперкуба Q₆"""
    return d_H(s, t) == 1

def neighbors(s: int) -> List[int]:
    """6 сусідів s в Q₆, всі t з d_H=1, тобто s⊕(1<<i) для i=0..5"""
    return [s ^ (1 << i) for i in range(6)]

# -------------------------------------------------------------------
# Інверсія та булева алгебра 𝔹⁶
# -------------------------------------------------------------------

def inv(s: int) -> int:
    """Інверсія inv(s) = s⊕111111₂ = ¬s, d_H(s,inv(s))=6, w(inv(s))=6-w(s)"""
    return s ^ ALL_BITS

def band(s: int, t: int) -> int:
    """s ∧ t = AND — спільні присутності"""
    return s & t

def bor(s: int, t: int) -> int:
    """s ∨ t = OR — об'єднання присутностей"""
    return s | t

def bnot(s: int) -> int:
    """¬s = inv(s)"""
    return inv(s)

# -------------------------------------------------------------------
# Кулі та сфери в (S₀,d_H) — метрика гіперкуба Q₆
# -------------------------------------------------------------------

def ball(s: int, r: int) -> Set[int]:
    """B_r(s) = { t | d_H(s,t) ≤ r }, куля радіуса r"""
    if r < 0:
        return set()
    if r >= 6:
        return set(range(64))
    result: Set[int] = set()
    # brute-force 64 — дешево
    for t in range(64):
        if d_H(s, t) <= r:
            result.add(t)
    return result

def sphere(s: int, r: int) -> Set[int]:
    """S_r(s) = { t | d_H(s,t) = r }, сфера радіуса r"""
    return {t for t in range(64) if d_H(s, t) == r}

# розміри куль для перевірки: |B₀|=1, |B₁|=7, |B₂|=22, |B₆|=64
BALL_SIZES = [len(ball(0, r)) for r in range(7)]  # [1,7,22,42,57,63,64]

# -------------------------------------------------------------------
# Порядки: lex та Gray
# -------------------------------------------------------------------

def lex_order() -> List[int]:
    """Лексикографічний порядок ≤_lex — просто 0..63"""
    return list(range(64))

def gray_encode(n: int) -> int:
    """
    Код Грея: G(n) = n ⊕ (n>>1), бієкція {0,…,63}→S₀
    Властивість: d_H(G(n), G(n+1 mod 64)) = 1 — гамільтонів цикл по Q₆
    """
    if not (0 <= n < 64):
        raise ValueError("n має бути 0..63")
    return n ^ (n >> 1)

def gray_decode(g: int) -> int:
    """Обернений до gray_encode: n з G(n)=g"""
    n = g
    n ^= n >> 1
    n ^= n >> 2
    n ^= n >> 4
    # для 6 біт достатньо 3 ітерацій
    return n & 0b111111

def gray_cycle() -> List[int]:
    """Цикл Грея G(0),G(1),…,G(63) — 64 стани, кожен крок d_H=1, замикається"""
    return [gray_encode(n) for n in range(64)]

def wen_wan_pairs() -> List[Tuple[int, int]]:
    """
    Пари Вень-ван (І-Цзін): (s, inv(s)), s<inv(s), 32 пари
    Традиційний порядок групує такі пари поруч
    """
    pairs = []
    seen = set()
    for s in range(64):
        t = inv(s)
        if s not in seen:
            pairs.append((s, t))
            seen.add(s)
            seen.add(t)
    return pairs

# -------------------------------------------------------------------
# Q₆ — гіперкуб
# -------------------------------------------------------------------

def q6_edges() -> List[Tuple[int, int]]:
    """Всі ребра Q₆: пари (s,t) з d_H=1, всього 64*6/2=192 ребер"""
    edges = []
    for s in range(64):
        for i in range(6):
            t = s ^ (1 << i)
            if s < t:  # щоб не дублювати
                edges.append((s, t))
    return edges

# -------------------------------------------------------------------
# Демо / тест
# -------------------------------------------------------------------
if __name__ == "__main__":
    # Приклади з Розділу II
    s = 0b101010  # 42 = (Я,СХІД,ВЕСНА)
    t = 0b111010  # 58 = (МИ,СХІД,ВЕСНА)
    print(f"s={s:2d} {s:06b}, t={t:2d} {t:06b}")
    print(f"s⊕t = {xor(s,t):06b} = {xor(s,t)}")
    print(f"w(s)={w(s)}, d_H(s,t)={d_H(s,t)}")
    print(f"inv(s)={inv(s):06b}, w(inv(s))={w(inv(s))}")
    print(f"B₁({s}) size={len(ball(s,1))} = 1+6=7, B₂ size={len(ball(s,2))}=22")
    print(f"neighbors({s}) = {[f'{n:06b}' for n in neighbors(s)]}")

    print("\nGray cycle check d_H=1:")
    cycle = gray_cycle()
    ok = all(d_H(cycle[i], cycle[(i+1) % 64]) == 1 for i in range(64))
    print(f"  len={len(cycle)}, all d_H=1: {ok}")
    print(f"  start: {[f'{x:06b}' for x in cycle[:5]]}")

    print("\nBALL_SIZES:", BALL_SIZES, "очікується [1,7,22,42,57,63,64]")
    print("Q6 edges:", len(q6_edges()), "очікується 192")

    # Лема: трансляційна інваріантність
    import random
    for _ in range(100):
        a, b, u = random.randint(0,63), random.randint(0,63), random.randint(0,63)
        assert d_H(a^u, b^u) == d_H(a,b)
    print("Лема d_H(s⊕u,t⊕u)=d_H(s,t) OK")
