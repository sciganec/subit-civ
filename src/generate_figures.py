#!/usr/bin/env python3
"""Generate figures for the Caral‑Supe paper."""

import os, sys, yaml
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import sqlite3

sys.path.append('.')
from src.evolution import run_simulation
from src.rules import apply_rule, classify_omega

# Paths
CONFIG_PATH = 'config/caral_params.yaml'
DB_PATH = 'caral_facts.sqlite'
OUTPUT_DIR = 'outputs'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load params
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    params = yaml.safe_load(f)

stress_steps = params['climate_stress_steps']
def stress_func(step):
    return 1 if step in stress_steps else 0

# ========================
# Figure 1 – Architecture layers
# ========================
def plot_architecture():
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis('off')

    layers = [
        ('L-1', 'Provenance (datasets, extractions)', '#f0f0f0'),
        ('L0', 'Sources (bibliography)', '#e0e0e0'),
        ('L1', 'Archaeological Facts (sites, artifacts, radiocarbon)', '#d9ead3'),
        ('L2', 'Derived Observations (population, isotopes)', '#b6d7a8'),
        ('L3', 'SUBIT Projection (rules, states, Ω-class)', '#a4c2f4'),
        ('L4', 'Simulation (runs, trajectories)', '#9fc5e8'),
        ('L5', 'Validation (comparisons, summaries)', '#f9cb9c'),
        ('L6', 'Logical Assertions (ℒ)', '#e06666'),
    ]

    for i, (label, desc, color) in enumerate(layers):
        y = 6 - i
        rect = mpatches.FancyBboxPatch((0.5, y-0.4), 9, 0.8,
                                       boxstyle="round,pad=0.05",
                                       facecolor=color, edgecolor='grey')
        ax.add_patch(rect)
        ax.text(1, y, f'{label}: {desc}', va='center', fontsize=10, fontweight='bold')

        if i < len(layers)-1:
            ax.annotate('', xy=(5, y-0.4), xytext=(5, y-1.2),
                        arrowprops=dict(arrowstyle='->', lw=1.5, color='black'))

    plt.title('Provenance‑Aware Research Architecture', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig1_architecture.png'), dpi=200)
    plt.close()
    print('Figure 1 saved.')

# ========================
# Figure 2 – Base simulation panels
# ========================
def plot_simulation():
    traj = run_simulation(params, stress_func)
    df = pd.DataFrame(traj, columns=['step','P','M','E','rule','omega'])

    fig, axes = plt.subplots(4, 1, figsize=(10, 12), sharex=True)

    axes[0].plot(df['step'], df['P'], label='Population (thousands)', color='steelblue')
    axes[0].set_ylabel('P')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(df['step'], df['M'], label='Monument volume', color='darkorange')
    axes[1].set_ylabel('M')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(df['step'], df['E'], label='Exotic import index', color='seagreen')
    axes[2].set_ylabel('E')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)

    omega_map = {'STABLE': 0, 'METASTABLE': 1, 'CYCLIC': 2, 'CHAOTIC': 3}
    omega_num = df['omega'].map(omega_map)
    axes[3].step(df['step'], omega_num, where='mid', label='Ω class', color='firebrick')
    axes[3].set_yticks(list(omega_map.values()))
    axes[3].set_yticklabels(list(omega_map.keys()))
    axes[3].set_ylabel('Ω')
    axes[3].set_xlabel('Step (25 years)')
    axes[3].legend()
    axes[3].grid(True, alpha=0.3)

    plt.suptitle('Base Simulation of Caral‑Supe Dynamics', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig2_simulation.png'), dpi=200)
    plt.close()
    print('Figure 2 saved.')

# ========================
# Figure 3 – Counterfactual trajectories
# ========================
def plot_counterfactuals():
    # Connect to DB for observed population
    conn = sqlite3.connect(DB_PATH)
    pop_obs = pd.read_sql("SELECT * FROM observations WHERE type='population'", conn)
    conn.close()

    # Baseline
    traj_base = run_simulation(params, stress_func)
    df_base = pd.DataFrame(traj_base, columns=['step','P','M','E','rule','omega'])

    # Agricultural primacy (rule 6)
    traj_agri = run_simulation(params, stress_func, start_rule=6)
    df_agri = pd.DataFrame(traj_agri, columns=['step','P','M','E','rule','omega'])

    # Managed migration (hybrid)
    params['simulation']['steps_total'] = params['simulation']['steps']
    # First part (baseline until step 60)
    params['simulation']['steps'] = 60
    traj1 = run_simulation(params, stress_func)
    last = traj1[-1]
    P, M, E, rule, omega = last[1], last[2], last[3], last[4], last[5]
    extra = params['simulation']['steps_total'] - 60
    for step in range(60, params['simulation']['steps_total']):
        stress = stress_func(step)
        P, M, E = apply_rule(P, M, E, 10, stress, params)
        omega = classify_omega(P, M, E, 10)
        traj1.append((step, P, M, E, 10, omega))
    df_migr = pd.DataFrame(traj1, columns=['step','P','M','E','rule','omega'])
    params['simulation']['steps'] = params['simulation']['steps_total']

    # Plot
    plt.figure(figsize=(10,5))
    plt.plot(df_base['step'], df_base['P'], label='Baseline (original rules)', color='steelblue')
    plt.plot(df_agri['step'], df_agri['P'], '--', label='Agricultural primacy (ρ=6)', color='darkorange')
    plt.plot(df_migr['step'], df_migr['P'], ':', label='Managed migration (ρ=10 after step 60)', color='firebrick')

    if not pop_obs.empty:
        pop_obs['year_mean'] = (pop_obs['year_from'] + pop_obs['year_to']) / 2
        pop_obs['step'] = ((pop_obs['year_mean'] + 3500) / 25).round().astype(int)
        plt.scatter(pop_obs['step'], pop_obs['value'], color='red', s=60,
                    zorder=5, label='Archaeological estimates')

    plt.xlabel('Step (25 years)')
    plt.ylabel('Population (thousands)')
    plt.title('Counterfactual Population Trajectories vs. Observed Data')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig3_counterfactual.png'), dpi=200)
    plt.close()
    print('Figure 3 saved.')

if __name__ == '__main__':
    plot_architecture()
    plot_simulation()
    plot_counterfactuals()
    print('All figures generated in', OUTPUT_DIR)