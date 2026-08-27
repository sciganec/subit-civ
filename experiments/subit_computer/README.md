# SUBIT-COMPUTER v0.1 — Reference Implementation

Референсна реалізація обчислювального ядра **SUBIT-COMPUTER SPECIFICATION v0.1** —
механічна трансляція розділів 1–7 специфікації у виконуваний Python. Узгоджено з
SUBIT-∞ v5.2 (`SUBIT-64 ⊂ SUBIT⁺ ⊂ SUBIT-TOPOS ⊂ SUBIT_∞`).

## Структура

```
subit_computer/
├── __init__.py     # публічний API
├── core.py         # реалізація розділів 1–7
├── tests.py        # 22 тести (таблиці, вентилі, ALU, траєкторії, Ω, d_Ω)
└── REVIEW.md       # формальний огляд специфікації + 5 знахідок
```

## Запуск

```bash
python -m unittest subit_computer.tests -v   # 22 тести, всі проходять
```

## Приклад

```python
from subit_computer.core import *

# правило, що циклює всі компоненти через 4-цикл T→F→N→B→T
cyc = {Value.T: Value.F, Value.F: Value.N, Value.N: Value.B, Value.B: Value.T}
rule = lambda s, c: SubitState(cyc[s.w], cyc[s.h], cyc[s.t])
G = TransitionGrammar(rho=rule, mu=lambda s,r,c: r, nu=lambda s,r,c: c)

h0 = ExtendedState(SubitState(Value.T, Value.N, Value.B), rule, None)
traj = run_trajectory(h0, G, max_steps=80)

print(classify_point(traj))   # Classification.CYCLIC
print(detect_cycle(traj))    # (0, 4)  — period 4
```

## Що перевірено

- **Таблиці Белнапа** (§1.3): ∧, ∨, XOR — усі 16 пар входів.
- **Вентилі (p,q)** (§1.4): формули точно відтворюють таблиці §1.3 — за умови
  булевого тлумачення `+`/`·` (OR/AND над {0,1}). Див. REVIEW.md §2.
- **SUBIT-ALU** (§5): ¬ ∧ ∨ ⊕ покомпонентно, ROTATE, MERGE, SPLIT, d_M.
- **Transition Grammar** (§4): аксіоми детермінованості, замкненості,
  ієрархії самореференції (ρ/μ/ν).
- **Analytical Layer** (§7): ω-границя, P(τ), Ω (STABLE/CYCLIC/⊥),
  ультраметрика d_Ω.

## Знахідки огляду (деталі в REVIEW.md)

1. Формули вентилів §1.4 переповнюються при цілочисельному читанні → потрібне
   булеве тлумачення `+`/`·`.
2. Твердження про ультраметричність `(S₀×R×C, d_M)` (§7.4) формально хибне:
   d_M визначена лише на S₀ і Хеммінг не є ультраметрикою загалом.
3. Ω змішує точкову (STABLE/CYCLIC) та множинну (METASTABLE/CHAOTIC)
   класифікацію — реалізовано роздільно.
4. ω-границя вимагає скінченності, тоді як R, C можуть бути нескінченними —
   оброблено через ресурсну межу `max_steps` → ⊥.
5. SPLIT семантично вироджений; MERGE фіксований (параметризація — v0.2).

## Відповідність SUBIT-∞

| Рівень SUBIT-∞ | Реалізація тут |
|---|---|
| SUBIT-64 | `SubitState` = A³ |
| SUBIT⁺ | `ExtendedState` + `TransitionGrammar` |
| SUBIT-TOPOS | `Classification`, алгебра Гейтінга, `classify_set` |
| SUBIT_∞ | `omega_distance` (d_Ω), `p_point` (P(τ)), ⊥ |

## Наступні кроки (з §9 spec)

- [x] Реалізувати SUBIT-ALU v0.1 — механічна трансляція розділу 5
- [ ] Модель Logisim/Verilog для вентилів ¬ ∧ ∨ та клітинки (p,q)
- [ ] Підтримка S_∞ та нескінченних траєкторій (v0.2)
- [ ] SUBIT-NEURON поверх Transition Grammar
