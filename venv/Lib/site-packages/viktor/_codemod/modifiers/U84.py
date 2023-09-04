from viktor._vendor import libcst


class Visitor(libcst.CSTVisitor):
    pass


class Transformer(libcst.CSTTransformer):

    def __init__(self, visitor):
        super().__init__()

    def leave_Call(self, node, updated_node):
        try:
            if node.func.value == 'UserException':
                return updated_node.with_changes(func=libcst.Name('UserError'))
        except AttributeError:  # func may not have 'value'
            return updated_node
        return updated_node

    def leave_ImportFrom(self, original_node, updated_node):
        new_names = []
        for n in updated_node.names:
            if n.name.value == 'UserException':
                n = n.with_changes(name=libcst.Name("UserError"))
            new_names.append(n)
        return updated_node.with_changes(names=new_names)
