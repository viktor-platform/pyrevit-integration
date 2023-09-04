from viktor._vendor import libcst


class Visitor(libcst.CSTVisitor):
    pass


class Transformer(libcst.CSTTransformer):

    def __init__(self, visitor):
        super().__init__()

        self.ImportAlias = "CircularExtrusion"

    def leave_ImportAlias_asname(self, node) -> None:
        if node.name.value == "CircularExtrusion":
            if node.asname:
                self.ImportAlias = node.asname.name.value

    def leave_Call(self, node, updated_node):
        try:
            if node.func.value != self.ImportAlias:
                return updated_node
        except AttributeError:  # func may not have 'value'
            return updated_node

        new_args = []
        for arg in node.args:
            new_arg = arg
            if arg.keyword is not None:
                if arg.keyword.value == 'open_ends':
                    if arg.value.value == 'False':
                        new_arg = arg.with_changes(
                            keyword=libcst.Name('shell_thickness'),
                            value=libcst.Name('None'),
                        )
                    if arg.value.value == 'True':
                        new_arg = arg.with_changes(
                            keyword=libcst.Name('shell_thickness'),
                            value=libcst.Integer('0'),
                        )
            new_args.append(new_arg)

        return updated_node.with_changes(args=new_args)
