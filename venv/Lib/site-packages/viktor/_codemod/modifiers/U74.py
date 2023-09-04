from viktor._vendor import libcst

from viktor._codemod.helpers import ControllerFlagTransformer


class Visitor(libcst.CSTVisitor):
    pass


class Transformer(ControllerFlagTransformer):
    controller_flag = 'viktor_store_table_option_field_value'
    controller_flag_value = True
