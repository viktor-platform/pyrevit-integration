from viktor._vendor import libcst

from viktor._vendor.libcst import matchers as m

from viktor._codemod.helpers import match_controller_class


class Visitor(libcst.CSTVisitor):
    pass


class Transformer(libcst.CSTTransformer):

    def __init__(self, visitor):
        super().__init__()

        self.OptionField_ImportAlias = None

    def leave_ImportAlias_asname(self, node) -> None:
        if node.name.value == "OptionField":
            if node.asname:
                self.OptionField_ImportAlias = node.asname.name.value

    def leave_ClassDef(self, original_node, updated_node):

        if not match_controller_class(original_node):
            return updated_node

        body = updated_node.body
        new_statements = []
        for statement in body.body:
            if m.matches(statement, m.SimpleStatementLine()):
                try:
                    target = statement.body[0].targets[0].target
                    if target.value.startswith('viktor_'):
                        continue
                except AttributeError:  # 'targets' not present
                    pass

            new_statements.append(statement)

        body = body.with_changes(body=new_statements)

        return updated_node.with_changes(body=body)

    def leave_Call(self, node, updated_node):

        try:
            if node.func.value not in (self.OptionField_ImportAlias, "OptionField"):
                return updated_node
        except AttributeError:  # func may not have 'value'
            return updated_node

        new_args = []
        for arg_index, arg in enumerate(node.args):

            if arg.keyword is not None:
                if arg.keyword.value == 'autoselect_single_option' and arg.value.value == 'False':
                    continue
            new_args.append(arg)

        new_args[-1] = new_args[-1].with_changes(comma=None)

        return updated_node.with_changes(args=new_args)
