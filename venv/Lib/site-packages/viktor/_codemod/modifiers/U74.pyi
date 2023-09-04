import libcst
from viktor._codemod.helpers import ControllerFlagTransformer as ControllerFlagTransformer

class Visitor(libcst.CSTVisitor): ...

class Transformer(ControllerFlagTransformer):
    controller_flag: str
    controller_flag_value: bool
