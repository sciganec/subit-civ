"""
SUBIT-∞ v5.1 — s0.py
Розділ I. ЕЛЕМЕНТИ

S₀ = A³ = 64 стани, A = {00,01,10,11}
Кодування: s = b₁b₂ b₃b₄ b₅b₆ ∈ 𝔹⁶, idx(s) ∈ {0,…,63}

Формули в юнікоді:
  A ≔ 𝔹² = {00,01,10,11}, |A|=4
  S₀ ≔ A × A × A, |S₀|=64
  idx(s) = 16·idx(хто) + 4·idx(де) + idx(коли)
  s = (хто, де, коли), хто∈A, де∈A, коли∈A
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Dict, List

# -------------------------------------------------------------------
# Алфавіт A
# -------------------------------------------------------------------
# Код: 2 біти як рядок "00","01","10","11" -> idx 0..3
# 00↦0, 01↦1, 10↦2, 11↦3

CODE_TO_IDX: Dict[str, int] = {"00": 0, "01": 1, "10": 2, "11": 3}
IDX_TO_CODE: Dict[int, str] = {v: k for k, v in CODE_TO_IDX.items()}

# Імена модусів — українські позначки з Розділу I
# 00=ВОНИ, 01=ТИ, 10=Я, 11=МИ
IDX_TO_NAME: Dict[int, str] = {0: "ВОНИ", 1: "ТИ", 2: "Я", 3: "МИ"}
NAME_TO_IDX: Dict[str, int] = {v: k for k, v in IDX_TO_NAME.items()}

# Для ДЕ та КОЛИ ті ж коди, але інші прочитання (для зручності)
WHERE_NAMES: Dict[int, str] = {
    0: "ПІВНІЧ",  # 00
    1: "ЗАХІД",   # 01
    2: "СХІД",    # 10
    3: "ПІВДЕНЬ"  # 11
}
WHEN_NAMES: Dict[int, str] = {
    0: "ЗИМА",    # 00
    1: "ОСІНЬ",   # 01
    2: "ВЕСНА",   # 10
    3: "ЛІТО"     # 11
}

# Константи для зручності
VONY = 0  # 00
TY = 1    # 01
YA = 2    # 10
MY = 3    # 11

A_SIZE = 4
S0_SIZE = 64

# -------------------------------------------------------------------
# Кодування S₀
# -------------------------------------------------------------------

def encode(who: int | str, where: int | str, when: int | str) -> int:
    """
    Кодує трійку (хто, де, коли) в idx ∈ {0,…,63}

    who, where, when можуть бути:
      - int 0..3
      - str "00","01","10","11"
      - str "Я","МИ","ТИ","ВОНИ" (для хто)

    Формула: idx(s) = 16·idx(хто) + 4·idx(де) + idx(коли)
    Біти: s = b₁b₂ b₃b₄ b₅b₆, b₁b₂=хто, b₃b₄=де, b₅b₆=коли
    """
    def to_idx(v: int | str, axis: str) -> int:
        if isinstance(v, int):
            if 0 <= v <= 3:
                return v
            raise ValueError(f"{axis} int має бути 0..3, отримано {v}")
        if v in CODE_TO_IDX:
            return CODE_TO_IDX[v]
        if v in NAME_TO_IDX:
            return NAME_TO_IDX[v]
        # Для ДЕ/КОЛИ дозволити імена сторін
        upper = v.upper()
        # зворотний пошук по WHERE/WHEN
        for k, name in WHERE_NAMES.items():
            if name == upper:
                return k
        for k, name in WHEN_NAMES.items():
            if name == upper:
                return k
        raise ValueError(f"Невідомий код {v} для {axis}")

    who_i = to_idx(who, "хто")
    where_i = to_idx(where, "де")
    when_i = to_idx(when, "коли")
    return (who_i << 4) | (where_i << 2) | when_i
    # еквівалент: 16*who_i + 4*where_i + when_i

def decode(s: int) -> Tuple[int, int, int]:
    """
    Декодує s ∈ {0,…,63} в (хто, де, коли), кожен ∈ {0,…,3}
    """
    if not (0 <= s < 64):
        raise ValueError(f"s має бути 0..63, отримано {s}")
    who = (s >> 4) & 0b11
    where = (s >> 2) & 0b11
    when = s & 0b11
    return who, where, when

def bits_str(s: int) -> str:
    """6-бітний рядок, напр. 36 -> '100100'"""
    return format(s, "06b")

def code_str(s: int) -> str:
    """Запис як (10,01,00), напр. 36 -> '(10,01,00)'"""
    who, where, when = decode(s)
    return f"({IDX_TO_CODE[who]},{IDX_TO_CODE[where]},{IDX_TO_CODE[when]})"

def read(s: int) -> str:
    """Людське читання: Я на ЗАХОДІ взимку і т.д."""
    who, where, when = decode(s)
    return f"{IDX_TO_NAME[who]} на {WHERE_NAMES[where]} в {WHEN_NAMES[when].lower()}"

@dataclass(frozen=True)
class State:
    """Один елемент S₀ — обгортка над int 0..63 для зручності"""
    id: int

    def __post_init__(self):
        if not (0 <= self.id < 64):
            raise ValueError(f"State id має бути 0..63")

    @property
    def triple(self) -> Tuple[int, int, int]:
        return decode(self.id)

    @property
    def who(self) -> int: return self.triple[0]
    @property
    def where(self) -> int: return self.triple[1]
    @property
    def when(self) -> int: return self.triple[2]

    @property
    def bits(self) -> str: return bits_str(self.id)
    @property
    def code(self) -> str: return code_str(self.id)
    @property
    def reading(self) -> str: return read(self.id)

    def __repr__(self): return f"State({self.id} {self.code} {self.reading})"

# -------------------------------------------------------------------
# Таблиця всіх 64 станів
# -------------------------------------------------------------------

def all_states() -> List[State]:
    return [State(i) for i in range(64)]

def s0_table() -> List[Dict]:
    """Повна таблиця для БД або CSV: 64 рядки"""
    rows = []
    for i in range(64):
        who, where, when = decode(i)
        rows.append({
            "id": i,
            "bits": bits_str(i),
            "who_idx": who,
            "who_code": IDX_TO_CODE[who],
            "who_name": IDX_TO_NAME[who],
            "where_idx": where,
            "where_code": IDX_TO_CODE[where],
            "where_name": WHERE_NAMES[where],
            "when_idx": when,
            "when_code": IDX_TO_CODE[when],
            "when_name": WHEN_NAMES[when],
            "reading": read(i),
        })
    return rows

# -------------------------------------------------------------------
# Тест / демо
# -------------------------------------------------------------------
if __name__ == "__main__":
    # Приклади з Розділу I
    examples = [
        (0, "000000₂ = (ВОНИ,ПІВНІЧ,ЗИМА) — колапс Караль"),
        (36, "100100₂ = (Я,ЗАХІД,ЗИМА) — Одіссей на Ітаці"),
        (42, "101010₂ = (Я,СХІД,ВЕСНА)"),
        (63, "111111₂ = (МИ,ПІВДЕНЬ,ЛІТО) — повнота"),
    ]
    for id_, note in examples:
        st = State(id_)
        print(f"{id_:2d} {st.bits} {st.code:12s} {st.reading:35s} # {note}")

    print("\nПеревірка кодування:")
    s = encode("Я", "ЗАХІД", "ЗИМА")  # 10,01,00
    assert s == 36
    assert decode(s) == (YA, 1, 0)
    assert bits_str(s) == "100100"
    print(f"encode(Я,ЗАХІД,ЗИМА) = {s} = {bits_str(s)} OK")

    print(f"\nВсього станів: {S0_SIZE}, розмір: TINYINT UNSIGNED")
