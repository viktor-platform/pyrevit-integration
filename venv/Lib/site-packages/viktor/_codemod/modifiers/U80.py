from viktor._vendor import libcst


class Visitor(libcst.CSTVisitor):
    pass


class Transformer(libcst.CSTTransformer):

    def __init__(self, visitor):
        super().__init__()

        self.NumberField_ImportAlias = "NumberField"
        self.IntegerField_ImportAlias = "IntegerField"

    def leave_ImportAlias_asname(self, node) -> None:
        if node.name.value == "NumberField":
            if node.asname:
                self.NumberField_ImportAlias = node.asname.name.value

        if node.name.value == "IntegerField":
            if node.asname:
                self.IntegerField_ImportAlias = node.asname.name.value

    def leave_Call(self, node, updated_node):
        try:
            if node.func.value not in (self.NumberField_ImportAlias, self.IntegerField_ImportAlias):
                return updated_node
        except AttributeError:  # func may not have 'value'
            return updated_node

        new_args = [a for a in node.args if not (a.keyword and a.keyword.value in ("min_message", "max_message"))]
        new_args[-1] = new_args[-1].with_changes(comma=None)
        return updated_node.with_changes(args=new_args)
