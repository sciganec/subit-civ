"""
SUBIT-∞ v5.1 — ядро
S₀=64 як TINYINT, F:4096→4096, Ω ≤4096 кроків
"""
from .s0 import (
    encode,
    decode,
    bits_str,
    code_str,
    read,
    State,
    all_states,
    s0_table,
    S0_SIZE,
    CODE_TO_IDX,
    IDX_TO_CODE,
    IDX_TO_NAME,
)
from .arith import (
    xor,
    oplus,
    w,
    d_H,
    is_neighbor,
    neighbors,
    inv,
    band,
    bor,
    ball,
    sphere,
    lex_order,
    gray_encode,
    gray_decode,
    gray_cycle,
    q6_edges,
    BALL_SIZES,
)
from .algebra import (
    pair_to_id,
    id_to_pair,
    f_shift,
    g_fix,
    g_self,
    g_adapt_slow,
    G_PRESETS,
    F,
    F_id,
    build_F_table,
    trajectory,
    trajectory_states,
)
from .coalgebra import (
    omega,
    omega_all,
    d_Omega_history,
    first_divergence,
    s0_to_sinf,
    depth,
    d_sinf,
    Leaf,
    Node,
    OmegaResult,
)

__version__ = "5.1.0"
__all__ = [
    "encode", "decode", "bits_str", "code_str", "read", "State", "all_states", "s0_table",
    "xor", "oplus", "w", "d_H", "neighbors", "inv", "ball", "gray_cycle", "q6_edges",
    "pair_to_id", "id_to_pair", "F", "build_F_table", "trajectory",
    "omega", "d_Omega_history", "s0_to_sinf", "OmegaResult",
]
