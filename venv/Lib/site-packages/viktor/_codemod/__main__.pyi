from pathlib import Path
from typing import List

U_MIN: int

class PrintStyle:
    RED: str
    GREEN: str
    BOLD: str
    END: str

def fix(root_dir: Path, upgrades: List[int], apply: bool, keep_original: bool): ...
def fix_upgrade(root_dir: Path, upgrade_id: int, apply: bool, keep_original: bool, patched_files: list) -> None: ...
