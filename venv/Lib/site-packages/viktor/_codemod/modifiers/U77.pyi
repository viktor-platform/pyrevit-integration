import libcst
from _typeshed import Incomplete
from pathlib import Path
from typing import List
from viktor import ViktorController as ViktorController
from viktor._codemod.helpers import collect_class_attributes as collect_class_attributes, match_controller_class as match_controller_class

def specific_fix(root_dir: Path, apply: bool, keep_original: bool, patched_files: list) -> None: ...

class TransformerAppInit(libcst.CSTTransformer):
    entity_types_to_rename: Incomplete
    entities: Incomplete
    def __init__(self, entity_types_to_rename: List[str], entities: List[dict]) -> None: ...
    def leave_ImportFrom(self, original_node, updated_node): ...
    def leave_Module(self, original_node, updated_node): ...

class TransformerHasDesigner(libcst.CSTTransformer):
    has_designer: Incomplete
    def __init__(self, has_designer: bool) -> None: ...
    def leave_ClassDef(self, original_node, updated_node): ...
