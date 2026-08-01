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
_core_dir = Path(s0.__file__).parent

def test_encode_decode():
    for i in range(64):
        who, where, when = s0.decode(i)
        j = s0.encode(who, where, when)
        assert i == j

def test_examples():
    assert s0.encode(0,0,0) == 0
    assert s0.encode("Я","ЗАХІД","ЗИМА") == 36
    assert s0.bits_str(36) == "100100"
    assert s0.encode(3,3,3) == 63

def test_table_size():
    assert len(s0.all_states()) == 64
    assert len(s0.s0_table()) == 64

if __name__ == "__main__":
    test_encode_decode()
    test_examples()
    test_table_size()
    print(f"test_s0 OK — core at {_core_dir}")
