import libcst
from _typeshed import Incomplete
from pathlib import Path
from viktor._codemod.helpers import collect_class_attributes as collect_class_attributes, match_controller_class as match_controller_class

def specific_fix(root_dir: Path, apply: bool, keep_original: bool, patched_files: list) -> None: ...

class Transformer(libcst.CSTTransformer):
    label: Incomplete
    children: Incomplete
    show_children_as: Incomplete
    def __init__(self, entity_type_info: dict) -> None: ...
    def leave_ClassDef(self, original_node, updated_node): ...
