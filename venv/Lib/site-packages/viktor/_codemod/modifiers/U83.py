from viktor._vendor import libcst

from viktor._codemod.helpers import ControllerFlagTransformer


class Visitor(libcst.CSTVisitor):
    pass


class Transformer(ControllerFlagTransformer):
    controller_flag = 'viktor_enforce_field_constraints'
    controller_flag_value = True
