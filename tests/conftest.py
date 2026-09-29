import types
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_script(module_name: str, filename: str) -> types.ModuleType:
    """Load a hyphenated executable script (e.g. check-free-space) as a module."""
    code = (REPO_ROOT / filename).read_text(encoding="utf-8")
    module = types.ModuleType(module_name)
    module.__file__ = str(REPO_ROOT / filename)
    # Make sibling modules importable the same way as running ./script from the repo dir.
    import sys

    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    exec(code, module.__dict__)
    return module


check_free_space = _load_script("check_free_space", "check-free-space")
disk_utilization = _load_script("disk_utilization", "disk-utilization")
disk_utilization_gatherer = _load_script(
    "disk_utilization_gatherer", "disk-utilization-gatherer"
)