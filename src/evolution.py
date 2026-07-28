"""
Main simulation loop for the Caral‑Supe model.
"""

from src.rules import apply_rule, meta_evolution, classify_omega


def run_simulation(params, stress_func):
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
    rule = init['rule']
    
    trajectory = []
    # For Ω refinement we could keep a small history, but for MVP we just use current state.
    for step in range(steps):
        # Determine external stress
        stress = stress_func(step)
        # Meta‑evolution: possibly switch rule
        rule = meta_evolution(rule, P, M, E, step, stress, params)
        # Apply the active rule to get next state
        P, M, E = apply_rule(P, M, E, rule, stress, params)
        # Classify stability
        omega = classify_omega(P, M, E, rule)
        trajectory.append((step, P, M, E, rule, omega))
    
    return trajectory