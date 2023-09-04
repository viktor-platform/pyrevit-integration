from viktor._vendor import libcst

from viktor._codemod.helpers import ControllerFlagTransformer


class Visitor(libcst.CSTVisitor):
    pass


class Transformer(ControllerFlagTransformer):
    controller_flag = 'viktor_name_filename_in_params'
    controller_flag_value = False
