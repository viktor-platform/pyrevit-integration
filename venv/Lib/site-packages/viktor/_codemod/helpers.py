from viktor._vendor import libcst

from viktor._vendor.libcst import matchers as m
from typing import List


##########
# MATCHERS
##########

def match_controller_class(node) -> bool:
    matcher = m.ClassDef(bases=[
        m.ZeroOrMore(m.DoNotCare()),  # do not care about potential preceding base-classes
        m.Arg(value=m.Name('ViktorController')),
        m.ZeroOrMore(m.DoNotCare()),  # do not care about potential succeeding base-classes
    ])
    return m.matches(node, matcher)


############
# COLLECTORS
############

def collect_class_attributes(node) -> List[str]:
    body = node.body.body

    simple_statements = []
    for statement in body:
        if m.matches(statement, m.SimpleStatementLine()):
            if m.matches(statement.body[0], m.Assign()):
                simple_statements.extend([s.target.value for s in statement.body[0].targets])
            elif m.matches(statement.body[0], m.AnnAssign()):
                simple_statements.append(statement.body[0].target.value)

    return simple_statements


##############
# TRANSFORMERS
##############

class ControllerFlagTransformer(libcst.CSTTransformer):
    controller_flag: str
    controller_flag_value: bool

    def __init__(self, visitor):
        super().__init__()

    def leave_ClassDef(self, original_node, updated_node):

        if not match_controller_class(original_node):
            return updated_node

        body = original_node.body
        class_body: list = list(body.body)
        simple_statements = collect_class_attributes(updated_node)

        if self.controller_flag not in simple_statements:

            class_body[0] = class_body[0].with_changes(leading_lines=[libcst.EmptyLine()])

            class_body.insert(0, libcst.SimpleStatementLine(
                body=[
                    libcst.Assign(
                        targets=[
                            libcst.AssignTarget(
                                target=libcst.Name(self.controller_flag),
                                whitespace_before_equal=libcst.SimpleWhitespace(' '),
                                whitespace_after_equal=libcst.SimpleWhitespace(' ')
                            )
                        ],
                        value=libcst.Name(str(self.controller_flag_value))
                    )
                ],
                leading_lines=[libcst.EmptyLine()]
            ))

            body = body.with_changes(body=class_body)
            return updated_node.with_changes(body=body)

        return updated_node
