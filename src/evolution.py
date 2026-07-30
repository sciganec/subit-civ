"""
Main simulation loop for the Caral‑Supe model.
"""

from src.rules import apply_rule, meta_evolution, classify_omega


def run_simulation(params, stress_func, start_rule=None):
    """
    Run the civilisation simulation and return the trajectory.
    
    Parameters
    ----------
    params : dict
        Simulation parameters (from YAML config).
    stress_func : callable
        Function that takes step (int) and returns 1 if El Niño stress is active.
    
    Returns
    -------
    list of tuples (step, P, M, E, rule, omega)
    """
    steps = params['simulation']['steps']
    init = params['simulation']['initial_state']
    P, M, E = init['P'], init['M'], init['E']
    rule = start_rule if start_rule is not None else init['rule']
    
    # Зберігаємо пікове населення для правила 10
    peak_P = P
    params['peak_population'] = peak_P  # оновлюватимемо під час симуляції
    
    trajectory = []
    for step in range(steps):
        stress = stress_func(step)
        # Якщо правило 10, не викликаємо звичайну мета-еволюцію, щоб не перемкнуло на winter
        if rule != 10:
            rule = meta_evolution(rule, P, M, E, step, stress, params)
        # Для правила 10 оновлюємо пікове населення
        if rule == 10:
            if P > params['peak_population']:
                params['peak_population'] = P
        # Застосовуємо правило
        P, M, E = apply_rule(P, M, E, rule, stress, params)
        omega = classify_omega(P, M, E, rule)
        trajectory.append((step, P, M, E, rule, omega))
    return trajectory