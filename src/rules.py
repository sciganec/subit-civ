"""
Caral‑Supe civilisation rules (ρ₁–ρ₄), meta‑evolution (g), and Ω‑classifier.
"""

def apply_rule(P, M, E, rule, stress, params):
    """
    Apply the active rule to the current state and return the next state (P, M, E).
    
    Parameters
    ----------
    P, M, E : float
        Current population (thousands), monument volume, exotic import index.
    rule : int
        Active rule (1, 2, 3, or 4).
    stress : int
        1 if El Niño stress is active this step, else 0.
    params : dict
        The full simulation parameter dictionary (from YAML).
    """
    r = params['rules']
    if rule == 1:          # SPRING – irrigation growth
        P_next = P * (1 + r['spring']['r'] * (1 - P / r['spring']['K']))
        M_next = M * (1 - r['spring']['M_decay']) + r['spring']['M_growth'] * P
        E_next = 0.0
    elif rule == 2:        # SUMMER – monumental cooperation
        P_next = P * (1 + r['summer']['r'] * (1 - P / r['spring']['K']) - r['summer']['cost_M'] * M)
        M_next = M * (1 - r['summer']['M_decay']) + r['summer']['M_growth'] * P
        E_next = max(0.0, E + r['summer']['E_inflow'] * (P / 20.0) - r['summer']['E_decay'])
    elif rule == 3:        # AUTUMN – trade compensation under stress
        decay_P = r['autumn']['base_decay_P'] + r['autumn']['stress_impact_P'] * stress
        P_next = P * (1 - decay_P)
        M_next = M * (1 - r['autumn']['M_decay'])
        E_next = max(0.0, E + r['autumn']['E_inflow'] * (P / 20.0) - r['autumn']['E_stress_loss'] * stress)
    else:                  # WINTER – collapse
        P_next = P * (1 - r['winter']['collapse_rate'])
        M_next = 0.0
        E_next = 0.0
    return P_next, M_next, E_next


def meta_evolution(rule, P, M, E, step, stress, params):
    """
    Decide whether to switch to a different rule (g‑function).
    
    Returns the new rule (may be the same as the input).
    """
    t = params['transitions']
    # SPRING → SUMMER when population threshold is reached
    if rule == 1 and P >= t['spring_to_summer_P']:
        return 2
    # SUMMER → AUTUMN when monument volume exceeds sustainable max OR external stress hits
    if rule == 2 and (M > t['summer_to_autumn_M'] or stress == 1):
        return 3
    # AUTUMN → WINTER when exotic trade collapses
    if rule == 3 and E < t['autumn_to_winter_E']:
        return 4
    return rule


def classify_omega(P, M, E, rule, prev_state=None):
    """
    Assign an Ω‑stability class based on the current state and trajectory.
    
    Simplified version:
    - WINTER rule → CHAOTIC
    - population below 5 → CHAOTIC
    - otherwise → METASTABLE (or could be refined to STABLE if changes very small)
    """
    if rule == 4 or P < 5.0:
        return "CHAOTIC"
    # Could add STABLE if changes are tiny over several steps; for MVP just METASTABLE
    return "METASTABLE"