# SUBIT-∞ v5.1 — core

Ядро: `S₀=64` як `TINYINT`, `(S₀,⊕) ≅ ℤ₂⁶`, `F: 4096→4096`, `Ω ≤4096` кроків.

## Установка

```bash
pip install subit-core
# або з репозиторію
pip install -e .
```

## Швидкий старт

```python
import subit_core as subit

# 1. ЕЛЕМЕНТИ — 64 стани як TINYINT
s = subit.encode("Я","ЗАХІД","ЗИМА")  # 36 = 100100₂
subit.decode(36)  # (2,1,0)
subit.read(36)    # "Я на ЗАХІД в зима"

# 2. АРИФМЕТИКА — XOR, d_H, кулі, Gray
subit.xor(42,16)  # 58, s⊕ρ
subit.d_H(42,58)  # 1
subit.ball(0,1)   # 7 станів біля колапсу
subit.gray_cycle() # 64 стани, кожен крок d_H=1

# 3. АЛГЕБРА — F: 4096→4096
id = subit.pair_to_id(s=36, rho=16) # 2320
F_table = subit.build_F_table() # 4096→4096, 8KB
traj = subit.trajectory(s0=42, rho0=16, steps=6) # [(42,16),(58,16)...] CYCLIC p=2

# 4. КОАЛГЕБРА — Ω, d_Ω, S∞
res = subit.omega(s0=63, rho0=1) # STABLE Караль: 111111→000000
res.type, res.period, res.preperiod
subit.d_Omega_history([42,58,42],[42,58,0]) # 0.25 = 2^-2
t = subit.s0_to_sinf(36) # Node(Leaf Я, Leaf ЗАХІД, Leaf ЗИМА)
```

## Структура

```
s0.py        — Розділ I: S₀=64, encode/decode, State, TINYINT
arith.py     — Розділ II: ⊕=XOR, w=popcount, d_H, B_r, Gray, Q₆
algebra.py   — Розділ III: R=S₀, f_ρ(s)=s⊕ρ, g(ρ,s), F(s,ρ), 4096→4096
coalgebra.py — Розділ IV: H=S₀^ℕ, d_Ω=2^-n₀, Ω→{STABLE,METASTABLE,CYCLIC,CHAOTIC}, S∞
tests/       — pytest, 100% детерміновано, ≤4096 кроків
```

## Специфікація

`docs/spec/v5.1/` — нормативні документи I-IV в юнікоді, елементарна академічна форма.

## Ліцензія

MIT
