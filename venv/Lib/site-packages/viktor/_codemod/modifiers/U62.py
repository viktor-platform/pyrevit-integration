from viktor._vendor import libcst
from viktor._vendor.libcst import matchers as m


class Visitor(libcst.CSTVisitor):
    pass


class Transformer(libcst.CSTTransformer):

    def __init__(self, visitor):
        super().__init__()

    def leave_Call(self, original_node: "Call", updated_node: "Call") -> "BaseExpression":
        if m.matches(updated_node.func, m.Attribute(attr=m.Name('threejs_visualisation'))):
            attr = updated_node.func.attr.with_changes(value="visualize_geometry")
            func = updated_node.func.with_changes(attr=attr)
            return updated_node.with_changes(func=func)
        return updated_node
