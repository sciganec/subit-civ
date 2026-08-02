"""
SUBIT-∞ v5.1 — інтерактивний блокнот
Unicode, без LaTeX. S_∞ = νX.(A ⊔ X³), S₀ = A³ = 64 стани.

Запуск: python subit.py
"""

from itertools import product
from collections import defaultdict
import random

# --- ЧАСТИНА I: Алфавіт ---
# Кодування: 10=T/ME, 11=B/WE, 01=F/YOU, 00=N/THEY
CODE = {
    "ME":    (1,0), "EAST":   (1,0), "SPRING": (1,0), "T": (1,0),
    "WE":    (1,1), "SOUTH":  (1,1), "SUMMER": (1,1), "B": (1,1),
    "YOU":   (0,1), "WEST":   (0,1), "AUTUMN": (0,1), "F": (0,1),
    "THEY":  (0,0), "NORTH":  (0,0), "WINTER": (0,0), "N": (0,0),
}
DECODE = {(1,0):"10:T/ME", (1,1):"11:B/WE", (0,1):"01:F/YOU", (0,0):"00:N/THEY"}

A_WHO = ["ME","WE","YOU","THEY"]
A_WHERE = ["EAST","SOUTH","WEST","NORTH"]
A_WHEN = ["SPRING","SUMMER","AUTUMN","WINTER"]

def encode_state(who, where, when):
    b = CODE[who] + CODE[where] + CODE[when]  # 6 біт
    return {"who":who,"where":where,"when":when,"bits":b,
            "lower":b[:3],"upper":b[3:], "code":"".join(map(str,b))}

# Генеруємо S₀ = 64 стани
S0 = [encode_state(who,whre,when) for who,whre,when in product(A_WHO,A_WHERE,A_WHEN)]
S0_index = { (s["who"],s["where"],s["when"]): i for i,s in enumerate(S0) }

def bit_to_hexagram(bits):
    # Проста відповідність: 1=суцільна, 0=переривчаста, для демо
    mapping = { (1,1,1,1,1,1):"䷀", (0,0,0,0,0,0):"䷁" }
    return mapping.get(tuple(bits), f"{''.join(map(str,bits))}")

# --- ЧАСТИНА II: Правила ---
# ℛ = скінченна множина функцій S₀→S₀
# Для демо задаємо 3 правила:

def rho_stay(s_idx): # ρ₀: залишитись
    return s_idx

def rho_next_season(s_idx):
    # SPRING→SUMMER→AUTUMN→WINTER→SPRING
    order = {"SPRING":"SUMMER","SUMMER":"AUTUMN","AUTUMN":"WINTER","WINTER":"SPRING"}
    s = S0[s_idx]
    new_when = order[s["when"]]
    return S0_index[(s["who"],s["where"],new_when)]

def rho_go_south(s_idx):
    s = S0[s_idx]
    return S0_index[(s["who"],"SOUTH",s["when"])]

R = [rho_stay, rho_next_season, rho_go_south]
R_names = ["ρ_stay: залишитись", "ρ_season: наступний сезон", "ρ_south: йти на південь"]

# g: ℛ×S₀→ℛ — метаеволюція
# Приклад: якщо на півдні влітку — правило стає "залишитись", інакше циклічно
def g(rho_idx, s_idx):
    s = S0[s_idx]
    if s["where"]=="SOUTH" and s["when"]=="SUMMER":
        return 0 # stay
    return (rho_idx+1) % len(R)

# F(s,ρ) = (f_ρ(s), g(ρ,s))
def F(state_idx, rho_idx):
    s_next = R[rho_idx](state_idx)
    rho_next = g(rho_idx, state_idx)
    return s_next, rho_next

# --- ЧАСТИНА II: Траєкторії ---
def trajectory(s0_idx, rho0_idx, steps=20):
    traj = [(s0_idx, rho0_idx)]
    visited = {}
    for n in range(steps):
        s,r = traj[-1]
        if (s,r) in visited:
            m = visited[(s,r)]
            k = n - m
            return traj, ("cycle", m, k)
        visited[(s,r)] = n
        s_next,r_next = F(s,r)
        traj.append((s_next,r_next))
    return traj, ("longer_than_Nmax", None, None)

def classify_trajectory(traj_info):
    typ,m,k = traj_info
    if typ=="cycle":
        if k==1:
            return "STABLE (атрактор) — болото"
        else:
            return f"CYCLIC k={k} — карусель, повернення через {k}"
    return "NEVYZNACHENO — цикл довший за горизонт"

# --- ЧАСТИНА III: Ω для множин ---
def apply_F_to_set(P_set):
    # P_set = set of (s_idx, rho_idx)
    return set(F(s,r) for s,r in P_set)

def omega_class(P_set, k_max=10):
    # Перевірка STABLE, METASTABLE, CYCLIC, CHAOTIC
    FP = apply_F_to_set(P_set)
    if FP == P_set:
        return "STABLE — F(P)=P"
    if FP < P_set: # ⊊
        return "METASTABLE — F(P)⊊P, лійка"
    # CYCLIC
    cur = FP
    for k in range(2, k_max+1):
        cur = apply_F_to_set(cur)
        if cur == P_set:
            return f"CYCLIC k={k}"
    return "CHAOTIC — ∀k F^k(P)≠P (на горизонті k_max)"

# --- ЧАСТИНА IV: d_Ω ---
def omega_of_single(s_idx, rho_idx):
    # Для однієї точки Ω визначаємо через траєкторію: якщо цикл k=1 → STABLE інакше CYCLIC (скінченний рівень)
    # Спрощення для демо
    traj,_ = trajectory(s_idx, rho_idx, steps=100)
    # якщо всі точки в traj мають однаковий rho? Ні, просто перевіримо чи є цикл
    seen=set()
    for s,r in traj:
        if (s,r) in seen:
            # знайшли цикл, перевіримо довжину
            idx = traj.index((s,r))
            k = len(traj)-1-idx
            if k==1 or k==0:
                return "STABLE"
            return "CYCLIC"
        seen.add((s,r))
    return "CYCLIC"

def n0_horizon(s1,r1,s2,r2, max_n=20):
    for n in range(max_n):
        # обчислити F^n
        sn1,rn1 = s1,r1
        sn2,rn2 = s2,r2
        for _ in range(n):
            sn1,rn1 = F(sn1,rn1)
            sn2,rn2 = F(sn2,rn2)
        o1 = omega_of_single(sn1,rn1)
        o2 = omega_of_single(sn2,rn2)
        if o1!=o2:
            return n, o1, o2
    return None,None,None

def d_omega(s1,r1,s2,r2):
    n,_,_ = n0_horizon(s1,r1,s2,r2)
    if n is None:
        return 0.0, None
    return 2**(-n), n

# --- ДЕМО ---
if __name__ == "__main__":
    print("=== SUBIT-64: 64 стани ===")
    for i,s in enumerate(S0[:5]):
        print(i, s["who"], s["where"], s["when"], s["code"], bit_to_hexagram(s["bits"]))
    print("... всього", len(S0))

    print("\n=== Траєкторія приклад ===")
    s0 = S0_index[("ME","EAST","SPRING")]
    rho0 = 1
    traj, info = trajectory(s0, rho0, steps=15)
    print(f"Старт: {S0[s0]} + {R_names[rho0]}")
    for i,(s,r) in enumerate(traj[:10]):
        print(f"  крок {i}: {S0[s]['who']},{S0[s]['where']},{S0[s]['when']} + {R_names[r]}")
    print("Класифікація:", classify_trajectory(info))

    print("\n=== Ω для множини ===")
    P = {(s0,rho0), (S0_index[("WE","SOUTH","SUMMER")],0)}
    print("P=",P)
    print("Ω(P)=", omega_class(P))

    print("\n=== d_Ω (горизонт узгодженості) ===")
    s1 = S0_index[("ME","EAST","SPRING")]
    s2 = S0_index[("ME","EAST","SUMMER")]
    d,n = d_omega(s1,1,s2,1)
    print(f"d_Ω між (ME,EAST,SPRING) і (ME,EAST,SUMMER) = {d}, n₀={n}")
    print("Чим більше n₀ — тим довше гіпотези йдуть разом")
