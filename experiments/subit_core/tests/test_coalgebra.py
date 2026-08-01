import sys
from pathlib import Path
import importlib.util

def _find_core_file(filename="s0.py"):
    here = Path(__file__).resolve()
    checked = []
    for parent in [here.parent] + list(here.parents)[:6]:
        for sub in ["", "subit_core", "subit-core", "src", "core", "subit_core/src"]:
            base = parent / sub if sub else parent
            p = base / filename
            checked.append(str(p))
            if p.exists():
                return p, checked
    return None, checked

def _load_from_path(module_name, file_path):
    file_path = Path(file_path)
    if not file_path.exists():
        return None
    sys.path.insert(0, str(file_path.parent))
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = mod
        spec.loader.exec_module(mod)
        return mod
    return None

def _ensure_module(name, filename=None):
    filename = filename or f"{name}.py"
    try:
        return __import__(name)
    except ModuleNotFoundError:
        pass
    found, checked = _find_core_file(filename)
    if found:
        mod = _load_from_path(name, found)
        if mod:
            return mod
    raise ModuleNotFoundError(
        f"Не знайдено {filename}. Перевірив:\n" + "\n".join(checked) +
        f"\n\nПеревір що файл {filename} лежить в subit_core\\"
    )

s0 = _ensure_module("s0", "s0.py")
arith = _ensure_module("arith", "arith.py")
algebra = _ensure_module("algebra", "algebra.py")
coalgebra = _ensure_module("coalgebra", "coalgebra.py")
from algebra import f_shift, g_fix, g_self
_core_dir = Path(coalgebra.__file__).parent

def test_omega_stable():
    res = coalgebra.omega(63, 1, f_shift, g_self)
    assert res.type == "STABLE"
    assert res.attractor == 0
    assert res.period == 1

def test_omega_cyclic():
    res = coalgebra.omega(42, 16, f_shift, g_fix)
    assert res.type == "CYCLIC"
    assert res.period == 2

def test_d_omega():
    h1 = [42,58,42,58]
    h2 = [42,58,0,0]
    assert coalgebra.first_divergence(h1,h2) == 2
    assert coalgebra.d_Omega_history(h1,h2) == 0.25
    assert coalgebra.d_Omega_history(h1,h1) == 0.0

def test_sinf():
    t = coalgebra.s0_to_sinf(36)
    assert coalgebra.depth(t) == 1
    t2 = coalgebra.s0_to_sinf(37)
    assert coalgebra.d_sinf(t,t2) == 0.5

def test_omega_all_counts():
    stats = coalgebra.omega_all(f_shift, g_fix)
    assert stats["STABLE"] == 64
    assert stats["CYCLIC"] == 4032
    assert sum(stats.values()) == 4096

if __name__ == "__main__":
    test_omega_stable()
    test_omega_cyclic()
    test_d_omega()
    test_sinf()
    test_omega_all_counts()
    print(f"test_coalgebra OK — core at {_core_dir}")
