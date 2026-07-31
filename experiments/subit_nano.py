import random
import hashlib
from collections import deque

# ============================================================
# НАЛАШТУВАННЯ
# ============================================================
TOTAL_STEPS = 200000
PRINT_INTERVAL = 5000
TRAJECTORY_LENGTH = 15

# ============================================================
# ІНІЦІАЛІЗАЦІЯ
# ============================================================
S = list(range(64))
random.shuffle(S)
s = random.randint(0, 63)
hist = deque(maxlen=2000)
visit_counts = [0] * 64

best_R = S.copy()
stuck_counter = 0
phase = "EXPLORE"
deep_count = 0
prev_unique = 0

def mutate_rule_type(R):
    if random.random() < 0.3:
        newR = R.copy()
        for i in range(64):
            if random.random() < 0.2:
                newR[i] = (R[i] + R[(i+1)%64] + R[(i-1)%64]) % 64
        return newR
    elif random.random() < 0.5:
        newR = R.copy()
        shift = random.randint(1, 63)
        for i in range(64):
            newR[i] = (R[i] + shift) % 64
        return newR
    else:
        newR = R.copy()
        for i in range(64):
            if random.random() < 0.1:
                newR[i] = random.randint(0, 63)
        return newR

def format_trajectory(hist, n=TRAJECTORY_LENGTH):
    if len(hist) < 2:
        return "..."
    recent = list(hist)[-n:]
    return " → ".join(f"{x:2d}" for x in recent)

def print_heatmap(counts):
    print("     0  1  2  3  4  5  6  7")
    print("   +------------------------+")
    for row in range(8):
        line = f" {row} |"
        for col in range(8):
            idx = row * 8 + col
            c = counts[idx]
            if c == 0:      line += " · "
            elif c < 5:     line += " . "
            elif c < 20:    line += " o "
            elif c < 50:    line += " O "
            elif c < 100:   line += " # "
            else:           line += "██ "
        line += "|"
        print(line)
    print("   +------------------------+")

# ============================================================
# ДРУК СТАТУСУ (ВИНОСИМО В ОКРЕМУ ФУНКЦІЮ)
# ============================================================
def print_status(t, phase, omega, unique_count, delta, novelty_score, s, hist):
    print(f"{t:8d} | {phase:<7} | {omega:<4} | {unique_count:>3}/64 | {delta:>+3} | {novelty_score:<8.2f} | {s:>3} | {format_trajectory(hist)}")

# ============================================================
# ГОЛОВНИЙ ЦИКЛ
# ============================================================
print("🚀 ЗАПУСК SUBIT-nano (ВІЗУАЛІЗАЦІЯ ЕВОЛЮЦІЇ)")
print(f"   Кроків: {TOTAL_STEPS}, друк кожні {PRINT_INTERVAL} кроків")
print("-" * 80)
print(f"{'Крок':>8} | {'Фаза':<7} | {'Ω':<4} | {'Унік':<5} | {'+':<4} | {'Новизна':<8} | {'Стан':<3} | Траєкторія (останні {TRAJECTORY_LENGTH})")
print("-" * 80)

last_phase = phase

for t in range(1, TOTAL_STEPS + 1):
    # --- ОНОВЛЕННЯ ДАНИХ ---
    hist.append(s)
    visit_counts[s] += 1
    unique_count = len(set(hist))
    
    # --- МЕТРИКИ ---
    if unique_count == 64:
        phase = "DEEP"
        novelty_score = 0.0
    else:
        recent = list(hist)[-50:]
        novelty_score = len(set(recent)) / max(1, len(recent))
    
    is_cycle = hist.count(s) > 3
    is_stable = len(set(list(hist)[-10:])) == 1

    # --- ВІДСТЕЖЕННЯ ЗМІНИ ФАЗИ ---
    if phase != last_phase:
        print(f"\n{'='*50}\n>>> ПЕРЕХІД ФАЗИ: {last_phase} -> {phase} (крок {t})\n{'='*50}")
        last_phase = phase

    # ============================================================
    # ЛОГІКА ЕВОЛЮЦІЇ (без змін, але без continue перед друком)
    # ============================================================
    if unique_count == 64:
        # DEEP-режим
        if t % 100 == 0:
            S = mutate_rule_type(S)
            deep_count += 1
            s = random.randint(0, 63)
            if S[s] == s:
                S[s] = (s + random.randint(1, 63)) % 64
            # Не використовуємо continue, щоб друк спрацював
        elif stuck_counter > 200:
            S = mutate_rule_type(S)
            deep_count += 1
            s = random.randint(0, 63)
            if S[s] == s:
                S[s] = (s + random.randint(1, 63)) % 64
            stuck_counter = 0
        else:
            stuck_counter += 1
            if random.random() < 0.02:
                idx = random.randint(0, 63)
                S[idx] = (S[idx] + random.choice([-1, 1])) % 64
            s = S[s]
    else:
        # Стандартна еволюція
        if is_cycle:
            random.shuffle(S)
            s = random.randint(0, 63)
            if S[s] == s:
                S[s] = (s + random.randint(1, 63)) % 64
            stuck_counter = 0
        elif is_stable:
            stuck_counter += 1
            noise_rate = max(0.01, 0.05 - novelty_score * 0.3)
            if random.random() < noise_rate:
                idx = random.randint(0, 63)
                S[idx] = (S[idx] + random.choice([-1, 1])) % 64
            if stuck_counter > 100 and novelty_score < 0.05:
                unseen = list(set(range(64)) - set(hist))
                if unseen:
                    s = random.choice(unseen)
                else:
                    s = random.randint(0, 63)
                hist_str = "".join(map(str, list(hist)[-30:]))
                h = int(hashlib.md5(hist_str.encode()).hexdigest()[:6], 16) % 64
                S[h] = (S[h] + h) % 64
                stuck_counter = 0
            else:
                s = S[s]   # якщо не спрацював впорск
        else:
            # Метастабільність
            mutation_rate = 0.15 if novelty_score < 0.1 else 0.05
            if random.random() < mutation_rate:
                idx = random.randint(0, 63)
                S[idx] = (S[idx] + random.randint(1, 3)) % 64
            if t % 50 == 0 and novelty_score < 0.1:
                hist_str = "".join(map(str, list(hist)[-20:]))
                h = int(hashlib.md5(hist_str.encode()).hexdigest()[:6], 16) % 64
                S[h] = (S[h] + h) % 64
            s = S[s]

    # --- ЗБЕРЕЖЕННЯ НАЙКРАЩОГО ---
    if novelty_score > 0.2 and unique_count > len(set(best_R)):
        best_R = S.copy()

    # ============================================================
    # ВИВІД СТАТУСУ (ГАРАНТОВАНО КОЖНІ PRINT_INTERVAL КРОКІВ)
    # ============================================================
    if t % PRINT_INTERVAL == 0:
        omega = "CYC" if hist.count(s) > 3 else "STB" if is_stable else "META"
        delta = unique_count - prev_unique
        print_status(t, phase, omega, unique_count, delta, novelty_score, s, hist)
        prev_unique = unique_count

# ============================================================
# ФІНАЛЬНИЙ ЗВІТ
# ============================================================
print("\n" + "=" * 80)
print("📜 ФІНАЛЬНИЙ ЗВІТ SUBIT-nano (Еволюція)")
print("=" * 80)
print(f"   Загальна кількість кроків:     {TOTAL_STEPS}")
print(f"   Унікальних станів відвідано:   {len(set(hist))}/64")
print(f"   Фінальна фаза:                {phase}")
print(f"   Кількість змін типу правила:  {deep_count}")
print(f"   Самореференцій (хеш):         ✅ активна")

print("\n   Остання траєкторія (30 станів):")
print(f"   {format_trajectory(hist, 30)}")

print("\n   Топ-5 найчастіше відвідуваних станів:")
sorted_counts = sorted([(i, visit_counts[i]) for i in range(64)], key=lambda x: -x[1])[:5]
for i, cnt in sorted_counts:
    bar = "█" * min(30, cnt // 10)
    print(f"     Стан {i:2d} : {cnt:4d} разів {bar}")

print("\n   Фінальна теплокарта (8×8):")
print_heatmap(visit_counts)

if deep_count > 0:
    print(f"\n   ✅ Система змінила тип правила {deep_count} разів (метастабільний розвиток).")
else:
    print("\n   ❌ Система не змінювала тип правила.")

print("=" * 80)
print("✅ Експеримент завершено.")