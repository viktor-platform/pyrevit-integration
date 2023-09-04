import importlib.util
import inspect
import sys
import json
from viktor._vendor import libcst
import re
from viktor._vendor import tomli
from viktor._vendor import tomli_w
from viktor._vendor import yaml

from pathlib import Path
from typing import Dict, Any, List, Optional

from viktor import ViktorController

from viktor._codemod.__main__ import _prompt_user, _patch_tree, _print_diff, _delete_file, _create_file
from viktor._codemod.helpers import match_controller_class, collect_class_attributes


def specific_fix(root_dir: Path, apply: bool, keep_original: bool, patched_files: list) -> None:
    manifest_path = root_dir / 'manifest' / 'manifest.yml'
    if not manifest_path.is_file():
        manifest_path = root_dir / 'manifest' / 'manifest.yaml'
        if not manifest_path.is_file():
            return

    app_init_path = root_dir / 'app' / '__init__.py'
    viktor_config_path = root_dir / 'viktor.config.toml'

    # add InitialEntity objects and renaming controllers
    entity_types_to_rename = _get_entity_types_to_rename(app_init_path)
    entities_to_convert = _get_entities_to_convert(manifest_path)
    if entity_types_to_rename or entities_to_convert:
        _patch_init(entity_types_to_rename, entities_to_convert, root_dir, app_init_path, apply, keep_original, patched_files)

    # patch controllers (add hide_editor where needed)
    entity_types_in_init = _get_entity_types_in_init(app_init_path)
    entity_types_to_convert = _get_entity_types_to_convert(manifest_path)
    if entity_types_to_convert:
        _patch_controllers(entity_types_to_convert, entity_types_in_init, root_dir, apply, keep_original, patched_files)

    # metadata to viktor.config.toml
    _patch_config(manifest_path, viktor_config_path, apply, keep_original, patched_files)

    # remove manifest and patch jsons
    _patch_manifest_jsons(entities_to_convert, root_dir, apply, keep_original, patched_files)
    _remove_manifest(manifest_path, apply, keep_original, patched_files)


############
# manifest #
############

def _patch_manifest_jsons(entities_to_convert, root_dir, apply, keep_original, patched_files):
    for entity in entities_to_convert:
        if entity.get('children'):
            _patch_manifest_jsons(entity['children'], root_dir, apply, keep_original, patched_files)

        if not isinstance(entity['params'], str):
            continue

        file_path = root_dir / 'app' / entity['params']
        rel_path = file_path.resolve().relative_to(root_dir)
        with open(file_path) as f:
            content = json.load(f)
        source = json.dumps(content, indent=2)
        content.pop('name')
        modified = json.dumps(content, indent=2)

        _print_diff(source, modified, rel_path, None)
        user_response = 'y' if apply else _prompt_user()  # reset user input given for previous diff
        if user_response == 'y':
            _patch_tree(source, modified, file_path, rel_path, keep_original)
            patched_files.append(rel_path)


def _remove_manifest(manifest_path, apply, keep_original, patched_files):
    rel_path = Path('manifest/manifest.yml')
    with open(manifest_path, 'r') as f:
        source_code = f.read()

    _print_diff(source_code, '', rel_path, None)
    user_response = 'y' if apply else _prompt_user()  # reset user input given for previous diff
    if user_response == 'y':
        _delete_file(manifest_path, rel_path=rel_path, keep_original=keep_original)
        patched_files.append(f"(removed file) {rel_path}")


############
# app init #
############

def _patch_init(entity_types_to_rename, entities_to_convert, root_path, init_path, apply, keep_original, patched_files):
    rel_path = init_path.relative_to(root_path)
    with open(init_path, 'rb') as python_file:
        python_source = python_file.read()

    # parse and transform the controller source, similar as __main__.py
    source_tree = libcst.parse_module(python_source)
    source_code = source_tree.code
    modified_tree = source_tree.visit(TransformerAppInit(entity_types_to_rename, entities_to_convert))
    modified_code = modified_tree.code

    if source_code != modified_code:
        _print_diff(source_code, modified_code, rel_path)
        user_response = 'y' if apply else _prompt_user()  # reset user input given for previous diff
        if user_response == 'y':
            _patch_tree(source_code, modified_code, init_path, rel_path, keep_original)
            patched_files.append(rel_path)


def _get_entity_types_to_rename(app_init_path: Path) -> List[str]:
    spec = importlib.util.spec_from_file_location("app", str(app_init_path))
    app = importlib.util.module_from_spec(spec)
    sys.modules["app"] = app
    spec.loader.exec_module(app)

    entity_types_to_rename = []
    for name, controller in inspect.getmembers(app):
        if inspect.isclass(controller) and issubclass(controller, ViktorController):

            if controller == ViktorController:
                continue

            entity_type = name
            if entity_type.endswith('Controller'):
                entity_types_to_rename.append(entity_type)

    return entity_types_to_rename


def _get_entities_to_convert(manifest_path: Path) -> List[dict]:
    """ Inspects the manifest and returns the entities for which InitialEntity objects should be constructed:

        [
            {
                'entity_type': 'TypeA',
                'name': 'Entity A1',
                'params': {...} | 'file/path.json',
                'children: [
                    {
                        'entity_type': 'TypeB',
                        ...
                    },
                    ...
                ]
            },
            ...
        ]

    """
    with open(manifest_path) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    def _read_entity(_entity: dict):
        entity_info = {
            'entity_type': _entity['entity_type'],
        }

        if isinstance(_entity['properties'], dict):
            entity_info['name'] = _entity['properties'].pop('name')
            entity_info['params'] = _entity['properties']
        else:  # path to .json
            file_path = manifest_path.parent / _entity['properties']
            with open(file_path) as f_:
                entity_info['name'] = json.load(f_)['name']
            entity_info['params'] = '../manifest/' + _entity['properties']  # path relative to app.__init__.py

        if 'children' in _entity:
            entity_info['children'] = [_read_entity(e) for e in _entity['children']]

        return entity_info

    return [_read_entity(entity) for entity in data.get('entities', [])]


class TransformerAppInit(libcst.CSTTransformer):

    def __init__(self, entity_types_to_rename: List[str], entities: List[dict]):
        super().__init__()
        self.entity_types_to_rename = entity_types_to_rename
        self.entities = entities

    def leave_ImportFrom(self, original_node, updated_node):
        if not self.entity_types_to_rename:
            return updated_node

        new_names = []
        for alias in updated_node.names:
            if alias.name.value in self.entity_types_to_rename:
                asname = libcst.AsName(
                    name=libcst.Name(alias.name.value.rsplit("Controller", 1)[0]),
                    whitespace_before_as=libcst.SimpleWhitespace(' '),
                    whitespace_after_as=libcst.SimpleWhitespace(' '),
                )
                new_names.append(alias.with_changes(asname=asname))
            elif alias.asname and alias.asname.name.value in self.entity_types_to_rename:
                asname = alias.asname.with_changes(
                    name=libcst.Name(alias.asname.name.value.rsplit("Controller", 1)[0])
                )
                new_names.append(alias.with_changes(asname=asname))
            else:
                new_names.append(alias)

        return updated_node.with_changes(names=new_names)

    def leave_Module(self, original_node, updated_node):

        if not self.entities:
            return updated_node

        body = list(updated_node.body)
        body.append(
            libcst.SimpleStatementLine(
                body=[
                    libcst.ImportFrom(
                        module=libcst.Name('viktor'),
                        names=[libcst.ImportAlias(name=libcst.Name('InitialEntity'))]
                    ),
                ],
                leading_lines=[libcst.EmptyLine(newline=libcst.Newline())],
                trailing_whitespace=libcst.TrailingWhitespace(
                    newline=libcst.Newline(),
                ),
            )
        )

        if self.entities:
            entity_elements = []
            number_of_elements = len(self.entities)
            for i, entity in enumerate(self.entities):
                include_comma = True
                if i + 1 == number_of_elements:
                    include_comma = False
                entity_elements.append(self._entity_to_element(entity, 4, include_comma))

            body.append(
                libcst.SimpleStatementLine(
                    body=[
                        libcst.Assign(
                            targets=[
                                libcst.AssignTarget(
                                    target=libcst.Name('initial_entities'),
                                    whitespace_before_equal=libcst.SimpleWhitespace(' '),
                                    whitespace_after_equal=libcst.SimpleWhitespace(' ')
                                ),
                            ],
                            value=libcst.List(
                                elements=entity_elements,
                                lbracket=libcst.LeftSquareBracket(
                                    whitespace_after=libcst.ParenthesizedWhitespace(
                                        first_line=libcst.TrailingWhitespace(
                                            newline=libcst.Newline(),
                                        ),
                                        last_line=libcst.SimpleWhitespace(
                                            value='    ',
                                        ),
                                    ),
                                ),
                                rbracket=libcst.RightSquareBracket(
                                    whitespace_before=libcst.ParenthesizedWhitespace(
                                        first_line=libcst.TrailingWhitespace(
                                            newline=libcst.Newline(),
                                        )
                                    ),
                                ),
                            ),
                        ),
                    ],
                    leading_lines=[libcst.EmptyLine(newline=libcst.Newline())],
                    trailing_whitespace=libcst.TrailingWhitespace(
                        newline=libcst.Newline(),
                    ),
                ),
            )

        return updated_node.with_changes(body=body)

    def _entity_to_element(self, entity: dict, leading_whitespace: int, include_comma: bool) -> libcst.Element:
        args = [
            libcst.Arg(value=libcst.SimpleString(f"'{entity['entity_type']}'")),
            libcst.Arg(
                value=libcst.SimpleString(f"'{entity['name']}'"),
                keyword=libcst.Name('name'),
                equal=libcst.AssignEqual(
                    whitespace_before=libcst.SimpleWhitespace(''),
                    whitespace_after=libcst.SimpleWhitespace(''),
                ),
            ),
        ]

        if entity.get('params'):
            if isinstance(entity.get('params'), str):  # path to .json
                args.append(
                    libcst.Arg(
                        value=libcst.SimpleString(f"'{entity['params']}'"),
                        keyword=libcst.Name('params'),
                        equal=libcst.AssignEqual(
                            whitespace_before=libcst.SimpleWhitespace(''),
                            whitespace_after=libcst.SimpleWhitespace(''),
                        ),
                    ),
                )
            else:  # dict
                args.append(
                    libcst.Arg(
                        value=libcst.Expr(libcst.parse_expression(json.dumps(entity['params']))),
                        keyword=libcst.Name('params'),
                        equal=libcst.AssignEqual(
                            whitespace_before=libcst.SimpleWhitespace(''),
                            whitespace_after=libcst.SimpleWhitespace(''),
                        ),
                    )
                )

        if entity.get('children'):
            child_elements = []
            number_of_elements = len(entity['children'])
            for i, entity in enumerate(entity['children']):
                include_comma_ = True
                if i + 1 == number_of_elements:
                    include_comma_ = False
                child_elements.append(self._entity_to_element(entity, leading_whitespace + 4, include_comma_))

            args.append(
                libcst.Arg(
                    value=libcst.List(
                        elements=child_elements,
                        lbracket=libcst.LeftSquareBracket(
                            whitespace_after=libcst.ParenthesizedWhitespace(
                                first_line=libcst.TrailingWhitespace(
                                    newline=libcst.Newline(),
                                ),
                                last_line=libcst.SimpleWhitespace(
                                    value=(leading_whitespace + 4) * ' ',
                                ),
                            ),
                        ),
                        rbracket=libcst.RightSquareBracket(
                            whitespace_before=libcst.ParenthesizedWhitespace(
                                first_line=libcst.TrailingWhitespace(
                                    newline=libcst.Newline(),
                                ),
                                last_line=libcst.SimpleWhitespace(
                                    value=leading_whitespace * ' ',
                                ),
                            ),
                        ),
                    ),
                    keyword=libcst.Name('children'),
                    equal=libcst.AssignEqual(
                        whitespace_before=libcst.SimpleWhitespace(''),
                        whitespace_after=libcst.SimpleWhitespace(''),
                    ),
                ),
            )

        if include_comma:
            return libcst.Element(
                value=libcst.Call(
                    func=libcst.Name('InitialEntity'),
                    args=args,
                ),
                comma=libcst.Comma(
                    whitespace_after=libcst.ParenthesizedWhitespace(
                        first_line=libcst.TrailingWhitespace(
                            newline=libcst.Newline(),
                        ),
                        last_line=libcst.SimpleWhitespace(
                            value=leading_whitespace * ' ',
                        ),
                    ),
                ),
            )
        else:
            return libcst.Element(
                value=libcst.Call(
                    func=libcst.Name('InitialEntity'),
                    args=args
                )
            )


################
# has_designer #
################

def _patch_controllers(entity_types_to_convert, entity_types_in_init, path, apply, keep_original, patched_files):
    for entity_type, has_designer in entity_types_to_convert.items():

        try:
            controller_path = entity_types_in_init[f'{entity_type}Controller'].replace('.', '/') + '.py'
        except KeyError:  # e.g. deleted entity type
            continue

        if controller_path.startswith('app'):
            path_ = Path(path) / controller_path
        else:  # relative path, starts with dot
            path_ = Path(path) / 'app' / controller_path[1:]

        try:
            with open(path_, 'rb') as python_file:
                python_source = python_file.read()
        except FileNotFoundError:  # might be a package with an __init__ instead of a module
            path_ = Path(str(path_)[:-3]) / '__init__.py'
            with open(path_, 'rb') as python_file:
                python_source = python_file.read()

        rel_path = path_.relative_to(path)

        # parse and transform the controller source, similar as __main__.py
        source_tree = libcst.parse_module(python_source)
        source_code = source_tree.code
        modified_tree = source_tree.visit(TransformerHasDesigner(has_designer))
        modified_code = modified_tree.code

        if source_code != modified_code:
            _print_diff(source_code, modified_code, rel_path)
            user_response = 'y' if apply else _prompt_user()  # reset user input given for previous diff
            if user_response == 'y':
                _patch_tree(source_code, modified_code, path_, rel_path, keep_original)
                patched_files.append(rel_path)


def _get_entity_types_in_init(app_init_path: Path) -> Dict[str, str]:
    """ Returns the entity-types that are imported in the app __init__.py, along with their path:

        {
            'EntityA': 'app.entity_a.controller',
            'EntityB': 'app.entity_b.controller',
            ...
        }

    """
    entity_types = {}
    with open(app_init_path) as f:
        for line in f.readlines():
            match = re.search(r'from\s+(\S+)\s+import\s+(?=Controller\s+as\s+(\w*)|(\S+Controller))', line)

            if match:
                controller_path = match.group(1)
                entity_type = match.group(2) or match.group(3)
                entity_types[entity_type] = controller_path

    return entity_types


def _get_entity_types_to_convert(manifest_path: Path) -> Dict[str, bool]:
    """ Inspects the manifest and returns the entity-types that need to be converted, with current value of has_designer

        {
            'EntityA': True,
            'EntityB': False,
            ...
        }

    """
    entity_types = {}
    with open(manifest_path) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    for entity_type, definition in data.get('entity_types', {}).items():
        if definition and 'has_designer' in definition:
            entity_types[entity_type] = definition['has_designer']

    return entity_types


class TransformerHasDesigner(libcst.CSTTransformer):

    def __init__(self, has_designer: bool):
        super().__init__()
        self.has_designer = has_designer

    def leave_ClassDef(self, original_node, updated_node):

        if self.has_designer:
            return updated_node

        if not match_controller_class(original_node):
            return updated_node

        body = updated_node.body
        class_body: list = list(body.body)
        simple_statements = collect_class_attributes(updated_node)

        if 'parametrization' in simple_statements:
            value = libcst.Name('True')
            self._add_simple_statement(class_body, 'hide_editor', value)

        body = body.with_changes(body=class_body)
        return updated_node.with_changes(body=body)

    @staticmethod
    def _add_simple_statement(body, target: str, value: Any):
        body.insert(0, libcst.SimpleStatementLine(
            body=[
                libcst.Assign(
                    targets=[
                        libcst.AssignTarget(
                            target=libcst.Name(target),
                            whitespace_before_equal=libcst.SimpleWhitespace(' '),
                            whitespace_after_equal=libcst.SimpleWhitespace(' ')
                        )
                    ],
                    value=value
                )
            ]
        ))


######################
# viktor.config.toml #
######################

def _patch_config(manifest_path: Path, viktor_config_path: Path, apply: bool, keep_original: bool,
                  patched_files: list) -> None:
    metadata = _get_metadata(manifest_path)
    welcome_text = metadata['welcome_text']
    uses_privileged_api = metadata['uses_privileged_api']

    if welcome_text is None and uses_privileged_api is None:
        return

    try:
        with open(viktor_config_path, 'r') as f:
            source_code = f.read()
    except IOError:
        source_code = ""

    modified_code = _get_modified_config(viktor_config_path, welcome_text, uses_privileged_api)

    rel_path = Path('viktor.config.toml')
    if source_code != modified_code:
        _print_diff(source_code, modified_code, rel_path)
        user_response = 'y' if apply else _prompt_user()  # reset user input given for previous diff

        if user_response == 'y':
            _create_file(viktor_config_path, '', rel_path)
            _patch_tree(source_code, modified_code, viktor_config_path, rel_path, keep_original)
            patched_files.append(rel_path)


def _get_metadata(manifest_path: Path) -> Dict[str, Optional[Any]]:
    metadata = {}
    with open(manifest_path, 'r') as f:
        s = f.read()

    metadata['welcome_text'] = _get_welcome_text(s)
    metadata['uses_privileged_api'] = _get_uses_privileged_api(s)
    return metadata


def _get_welcome_text(manifest_source: str) -> Optional[str]:
    m = re.search(r'welcome_text\s*:\s*\"([^\"]*)\"', manifest_source)
    if m is not None:
        return m.group(1).strip()

    m = re.search(r'welcome_text\s*:\s*\'([^\']*)\'', manifest_source)
    if m is not None:
        return m.group(1).strip()

    m = re.search(r'welcome_text\s*:\s*([^#\n]*)', manifest_source)
    if m is not None:
        return m.group(1).strip() # Remove spaces at start/end of filename
    return None


def _get_uses_privileged_api(manifest_source: str) -> Optional[bool]:
    m = re.search(r'uses_privileged_api\s*:\s*true', manifest_source)
    if m is not None:
        return True
    m = re.search(r'uses_privileged_api\s*:\s*false', manifest_source)
    if m is not None:
        return False


def _get_modified_config(viktor_config_path: Path, welcome_text: Optional[str],
                         uses_privileged_api: Optional[bool]) -> str:
    try:
        with open(viktor_config_path, "rb") as f:
            d = tomli.load(f)
    except IOError:
        d = {}

    if welcome_text and 'welcome_text' not in d:
        root_dir = viktor_config_path.parent.resolve()
        d['welcome_text'] = str((root_dir / 'manifest' / welcome_text).resolve().relative_to(root_dir))
    if uses_privileged_api is not None and 'enable_privileged_api' not in d:
        d['enable_privileged_api'] = uses_privileged_api

    return tomli_w.dumps(d)
