from viktor._vendor import libcst


class Visitor(libcst.CSTVisitor):
    pass


class Transformer(libcst.CSTTransformer):

    def __init__(self, visitor):
        super().__init__()

        self.OptionField_ImportALIAS = None
        self.Table_ImportALIAS = None
        self.within_table = False
        self.tables = []

    def leave_ImportAlias_asname(self, node) -> None:
        if node.name.value == "OptionField":
            if node.asname:
                self.OptionField_ImportALIAS = node.asname.name.value
        elif node.name.value in ("Table", "TableInput"):
            if node.asname:
                self.Table_ImportALIAS = node.asname.name.value

    def visit_SimpleStatementLine(self, node):

        param_path_list = []

        def get_param_path_recursive(attribute_: libcst.Attribute):
            # Recursively get the param path as list, i.e. the left hand side of the equation.
            # For example, if the target is 'tab.section.table', param_path will be ['tab', 'section', 'table']
            if type(attribute_.value) is libcst.Attribute:
                get_param_path_recursive(attribute_.value)
            elif type(attribute_.value) is libcst.Name:
                param_path_list.append(attribute_.value.value)
            elif type(attribute_.value) is str:
                param_path_list.append(attribute_.value)

            param_path_list.append(attribute_.attr.value)

        try:
            target = node.body[0].targets[0]
            func_value = node.body[0].value.func.value
        except AttributeError:
            return

        if func_value in (self.Table_ImportALIAS, 'Table', 'TableInput'):
            if type(target.target) is libcst.Name:  # singular target e.g. table = Table(...)
                table_path = target.target.value
            else:  # dotted path e.g. tab.section.table = Table(...)
                get_param_path_recursive(target.target)  # tab + section
                table_path = '.'.join(param_path_list)
            self.tables.append(table_path)
        elif func_value in (self.OptionField_ImportALIAS, 'OptionField'):
            if type(target.target) is libcst.Name:  # direct target e.g. options = OptionField(...)
                pass
            else:  # dotted path, e.g. tab.section.table.options = OptionField(...)
                get_param_path_recursive(target.target)
                table_path = '.'.join(param_path_list[:-1])  # exclude last item e.g. 'options'
                if table_path in self.tables:
                    self.within_table = True

    def leave_SimpleStatementLine(self, original_node, updated_node):
        self.within_table = False
        return updated_node

    def leave_Call(self, node, updated_node):
        if self.within_table:
            return updated_node

        try:
            if node.func.value not in (self.OptionField_ImportALIAS, "OptionField"):
                return updated_node
        except AttributeError:  # func may not have 'value'
            return updated_node

        new_args = []
        add_kwarg = True
        for arg_index, arg in enumerate(node.args):

            if arg.keyword is not None:
                if arg.keyword.value == 'autoselect_single_option':
                    add_kwarg = False
            new_args.append(arg)

        if add_kwarg:
            arg = libcst.Arg(
                keyword=libcst.Name('autoselect_single_option'),
                value=libcst.Name('True'),
                equal=libcst.AssignEqual(
                    whitespace_before=libcst.SimpleWhitespace(value=''),
                    whitespace_after=libcst.SimpleWhitespace(value=''),
                )
            )

            new_args.append(arg)
            new_args[-1] = new_args[-1].with_changes(comma=None)

        return updated_node.with_changes(args=new_args)
