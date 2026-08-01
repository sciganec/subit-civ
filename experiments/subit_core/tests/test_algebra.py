import sys
from pathlib import Path
import importlib.util

def _find_core_file(filename="s0.py"):
    here = Path(__file__).resolve()
    checked = []
    # search up to 6 levels up, in several subfolders
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
    # ensure parent in sys.path for its own imports (algebra imports s0 etc)
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
    # if already importable, return it
    try:
        return __import__(name)
    except ModuleNotFoundError:
        pass
    found, checked = _find_core_file(filename)
    if found:
        mod = _load_from_path(name, found)
        if mod:
            return mod
    # final attempt: try to import with diagnostic
    raise ModuleNotFoundError(
        f"Не знайдено {filename}. Перевірив:\n" + "\n".join(checked) +
        f"\n\nПеревір що файл {filename} лежить в C:\\...\\subit_core\\ і запусти з кореня: python -m tests.test_s0"
    )

s0 = _ensure_module("s0", "s0.py")
arith = _ensure_module("arith", "arith.py")
algebra = _ensure_module("algebra", "algebra.py")
from algebra import f_shift, g_fix, g_self, pair_to_id, id_to_pair, trajectory, build_F_table
_core_dir = Path(algebra.__file__).parent

def test_pair_encoding():
    for s in range(64):
        for rho in range(64):
            id_ = pair_to_id(s, rho)
            s2, rho2 = id_to_pair(id_)
            assert (s, rho) == (s2, rho2)

def test_F_table_size():
    table = build_F_table(f_shift, g_fix)
    assert len(table) == 4096

def test_fix_cycle():
    traj = trajectory(42, 16, 6, f_shift, g_fix)
    assert traj[0] == (42,16)
    assert traj[1] == (58,16)
    assert traj[2] == (42,16)

def test_caral_self_collapse():
    traj = trajectory(63, 1, 5, f_shift, g_self)
    assert traj[0][0] == 63
    assert traj[1][0] == 62
    assert traj[2][0] == 0

if __name__ == "__main__":
    test_pair_encoding()
    test_F_table_size()
    test_fix_cycle()
    test_caral_self_collapse()
    print(f"test_algebra OK — core at {_core_dir}")
