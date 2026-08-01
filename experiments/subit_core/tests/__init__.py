"""tests package — bootstrap core modules"""
import sys
from pathlib import Path

def _bootstrap():
    here = Path(__file__).resolve()
    for parent in [here.parent] + list(here.parents)[:6]:
        for sub in ["", "subit_core", "subit-core", "src", "core"]:
            p = (parent / sub / "s0.py") if sub else (parent / "s0.py")
            if p.exists():
                sys.path.insert(0, str(p.parent))
                return p.parent
    return None

_bootstrap()
