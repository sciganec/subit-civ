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
_core_dir = Path(arith.__file__).parent

def test_group():
    for s in range(64):
        assert arith.xor(s,0) == s
        assert arith.xor(s,s) == 0

def test_w_dH():
    assert arith.w(0b000000) == 0
    assert arith.w(0b111111) == 6
    assert arith.w(0b101010) == 3
    assert arith.d_H(0b101010, 0b111010) == 1
    assert arith.d_H(0b000000, 0b111111) == 6

def test_ball_sizes():
    assert arith.BALL_SIZES == [1,7,22,42,57,63,64]
    assert len(arith.ball(0,1)) == 7
    assert len(arith.ball(0,2)) == 22

def test_q6():
    assert len(arith.q6_edges()) == 192
    for s in range(64):
        assert len(arith.neighbors(s)) == 6

def test_gray():
    cycle = arith.gray_cycle()
    assert len(cycle) == 64
    for i in range(64):
        assert arith.d_H(cycle[i], cycle[(i+1)%64]) == 1

if __name__ == "__main__":
    test_group()
    test_w_dH()
    test_ball_sizes()
    test_q6()
    test_gray()
    print(f"test_arith OK — core at {_core_dir}")
