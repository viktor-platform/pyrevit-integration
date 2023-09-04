from viktor._vendor import libcst

_OBJECTS = {
    "GeometryResult",
    "GeometryAndDataResult"
}


class Visitor(libcst.CSTVisitor):
    pass


class Transformer(libcst.CSTTransformer):

    def __init__(self, visitor):
        super().__init__()

        self.ImportALIAS = _OBJECTS

    def leave_ImportAlias_asname(self, node) -> None:
        if node.name.value in _OBJECTS:
            if node.asname:
                self.ImportALIAS.remove(node.name.value)
                self.ImportALIAS.add(node.asname.name.value)

    def leave_Call(self, node, updated_node):
        try:
            if node.func.value not in self.ImportALIAS:
                return updated_node
        except AttributeError:  # func may not have 'value'
            return updated_node

        new_args = []
        for arg in node.args:
            new_arg = arg
            if arg.keyword is not None:
                if arg.keyword.value == 'visualization_group':
                    new_arg = arg.with_changes(keyword=libcst.Name('geometry'))
            new_args.append(new_arg)

        return updated_node.with_changes(args=new_args)