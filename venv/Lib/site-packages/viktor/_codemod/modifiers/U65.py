from viktor._vendor import libcst

from viktor._codemod.helpers import ControllerFlagTransformer


class Visitor(libcst.CSTVisitor):
    pass


class Transformer(ControllerFlagTransformer):
    controller_flag = 'viktor_convert_entity_field'
    controller_flag_value = True
