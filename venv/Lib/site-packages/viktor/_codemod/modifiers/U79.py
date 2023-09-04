from viktor._vendor import libcst


class Visitor(libcst.CSTVisitor):
    pass


class Transformer(libcst.CSTTransformer):

    def __init__(self, visitor):
        super().__init__()

        self.color_already_imported = False
        self.requires_conversion = False

    def visit_ImportFrom(self, node):
        try:
            if node.module.value.value == 'viktor':
                for n in node.names:
                    if n.name.value == 'Color':
                        self.color_already_imported = True
        except AttributeError:
            pass

    def leave_Call(self, node, updated_node):
        try:
            if node.func.value not in ('hex_to_rgb', 'rgb_to_hex'):
                return updated_node
        except AttributeError:  # func may not have 'value'
            return updated_node

        self.requires_conversion = True

        new_func = libcst.Attribute(
            value=libcst.Name('Color'),
            attr=node.func
        )

        new_args = []
        for arg in node.args:
            if arg.keyword and arg.keyword.value == 'red':
                new_args.append(arg.with_changes(keyword=libcst.Name('r')))
            elif arg.keyword and arg.keyword.value == 'blue':
                new_args.append(arg.with_changes(keyword=libcst.Name('b')))
            elif arg.keyword and arg.keyword.value == 'green':
                new_args.append(arg.with_changes(keyword=libcst.Name('g')))
            else:
                new_args.append(arg)

        return updated_node.with_changes(func=new_func, args=new_args)

    def leave_Module(self, original_node, updated_node):
        if not self.requires_conversion:
            return updated_node
        if self.color_already_imported:
            return updated_node

        body = list(updated_node.body)
        body.insert(0, libcst.SimpleStatementLine(
            body=[
                libcst.ImportFrom(
                    module=libcst.Attribute(
                        value=libcst.Name('viktor'),
                        attr=libcst.Name('core'),
                    ),
                    names=[
                        libcst.ImportAlias(
                            name=libcst.Name('Color'),
                        )
                    ],
                )
            ]
        ))
        return updated_node.with_changes(body=body)

    def leave_ImportFrom(self, original_node, updated_node):
        new_names = []
        for n in updated_node.names:
            if n.name.value in ('hex_to_rgb', 'rgb_to_hex'):
                continue
            new_names.append(n)

        if new_names:
            return updated_node.with_changes(names=new_names)

        return libcst.RemovalSentinel.REMOVE
