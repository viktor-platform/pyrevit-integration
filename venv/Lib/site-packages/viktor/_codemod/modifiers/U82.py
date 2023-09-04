from viktor._vendor import libcst

from viktor._vendor.libcst import matchers as m


_VIEWS = {
    "PNGView",
    "JPGView",
    "SVGView",
}

_VIEWS_DATA = {
    "PNGAndDataView",
    "JPGAndDataView",
    "SVGAndDataView",
}

_VIEW_RESULTS = {
    "PNGResult",
    "JPGResult",
    "SVGResult",
}

_VIEW_RESULTS_DATA = {
    "PNGAndDataResult",
    "JPGAndDataResult",
    "SVGAndDataResult",
}


class Visitor(libcst.CSTVisitor):
    pass


class Transformer(libcst.CSTTransformer):

    def __init__(self, visitor):
        super().__init__()

        self.ImageView_imported = False
        self.ImageAndDataView_imported = False
        self.ImageResult_imported = False
        self.ImageAndDataResult_imported = False

    def leave_ImportFrom(self, original_node, updated_node):
        new_names = []
        for n in updated_node.names:
            if n.name.value in _VIEWS:
                if self.ImageView_imported:
                    continue
                n = n.with_changes(name=libcst.Name("ImageView"))
                if n.asname is None:
                    self.ImageView_imported = True

            if n.name.value in _VIEWS_DATA:
                if self.ImageAndDataView_imported:
                    continue
                n = n.with_changes(name=libcst.Name("ImageAndDataView"))
                if n.asname is None:
                    self.ImageAndDataView_imported = True

            if n.name.value in _VIEW_RESULTS:
                if self.ImageResult_imported:
                    continue
                n = n.with_changes(name=libcst.Name("ImageResult"))
                if n.asname is None:
                    self.ImageResult_imported = True

            if n.name.value in _VIEW_RESULTS_DATA:
                if self.ImageAndDataResult_imported:
                    continue
                n = n.with_changes(name=libcst.Name("ImageAndDataResult"))
                if n.asname is None:
                    self.ImageAndDataResult_imported = True

            new_names.append(n)

        if new_names:
            new_names[-1] = new_names[-1].with_changes(comma=None)
            return updated_node.with_changes(names=new_names)
        return libcst.RemovalSentinel.REMOVE

    def leave_Decorator(self, original_node, updated_node):
        try:
            view_name = updated_node.decorator.func.value
            if (view_name not in _VIEWS) and (view_name not in _VIEWS_DATA):
                return updated_node
        except AttributeError:  # func may not have 'value'
            return updated_node

        d = updated_node.decorator.with_changes(func=libcst.Name("Image" + view_name[3:]))  # strip 'PNG' / 'JPG' / 'SVG'
        return updated_node.with_changes(decorator=d)

    def leave_Call(self, node, updated_node):
        func = node.func
        if m.matches(func, m.Name()):
            view_result_name = func.value
            if (view_result_name in _VIEW_RESULTS) or (view_result_name in _VIEW_RESULTS_DATA):
                new_func = func.with_changes(value="Image" + view_result_name[3:])  # strip 'PNG' / 'JPG' / 'SVG'
                return updated_node.with_changes(func=new_func)
        elif m.matches(func, m.Attribute(value=m.Name())):
            view_result_name = func.value.value
            if (view_result_name in _VIEW_RESULTS) or (view_result_name in _VIEW_RESULTS_DATA):
                new_func = func.with_changes(value=libcst.Name("Image" + view_result_name[3:]))  # strip 'PNG' / 'JPG' / 'SVG'
                return updated_node.with_changes(func=new_func)

        return updated_node
