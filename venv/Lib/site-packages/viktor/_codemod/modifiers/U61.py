from viktor._vendor import libcst
import re
from viktor._vendor import yaml

from pathlib import Path
from typing import Dict, List, Any

from viktor._codemod.__main__ import _prompt_user, _patch_tree, _print_diff, _create_file, _create_dir
from viktor._codemod.helpers import match_controller_class, collect_class_attributes


def specific_fix(root_dir: Path, apply: bool, keep_original: bool, patched_files: list) -> None:
    manifest_path = root_dir / 'manifest' / 'manifest.yml'
    if not manifest_path.is_file():
        manifest_path = root_dir / 'manifest' / 'manifest.yaml'
        if not manifest_path.is_file():
            return

    app_init_path = root_dir / 'app' / '__init__.py'
    entity_types_in_init = _get_entity_types_in_init(app_init_path)
    entity_types_to_convert = _get_entity_types_to_convert(manifest_path)

    if not entity_types_to_convert:
        return

    # add entity-type controllers that are not yet defined
    _add_entity_type_controllers(entity_types_to_convert, entity_types_in_init, root_dir, apply, keep_original, patched_files)

    # patch existing entity-type controllers
    _patch_existing_entity_type_controllers(entity_types_to_convert, entity_types_in_init, root_dir, apply, keep_original, patched_files)

    # patch manifest
    _patch_manifest(manifest_path, apply, keep_original, patched_files)


def _convert_entity_type_name_to_folder(entity_type: str) -> str:
    folder = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', entity_type)
    folder = re.sub('([a-z0-9])([A-Z])', r'\1_\2', folder).lower()
    return folder


def _add_entity_type_controllers(entity_types_to_convert, entity_types_in_init, path, apply, keep_original, patched_files):
    # create entity-type controller.py
    controllers_to_add = []
    for entity_type, entity_type_info in entity_types_to_convert.items():

        if f'{entity_type}Controller' in entity_types_in_init:
            continue

        entity_type_folder = _convert_entity_type_name_to_folder(entity_type)
        entity_type_folder = Path(path) / 'app' / entity_type_folder

        init_path = entity_type_folder / '__init__.py'
        controller_path = entity_type_folder / 'controller.py'
        controller_content = _create_controller_content(entity_type, entity_type_info)

        _print_diff('', controller_content, None, controller_path.relative_to(path))
        user_response = 'y' if apply else _prompt_user()  # reset user input given for previous diff
        if user_response == 'y':
            _create_dir(entity_type_folder, rel_path=entity_type_folder.relative_to(path))
            _create_file(init_path, '', rel_path=init_path.relative_to(path))
            _create_file(controller_path, controller_content, rel_path=controller_path.relative_to(path))

            patched_files.append(f"(new file) {init_path.relative_to(path)}")
            patched_files.append(f"(new file) {controller_path.relative_to(path)}")
            controllers_to_add.append(entity_type)

    # add entity-type controller import to app init
    init_path = Path(path) / 'app' / '__init__.py'
    with open(init_path, 'r') as f:
        source_init = f.read()
    modified_init = _get_modified_init(init_path, controllers_to_add)

    rel_path = init_path.relative_to(path)

    if source_init != modified_init:
        _print_diff(source_init, modified_init, rel_path, rel_path)
        user_response = 'y' if apply else _prompt_user()  # reset user input given for previous diff
        if user_response == 'y':
            _patch_tree(source_init, modified_init, init_path, rel_path, keep_original)
            patched_files.append(rel_path)


def _patch_existing_entity_type_controllers(entity_types_to_convert, entity_types_in_init, path, apply, keep_original, patched_files):
    for entity_type, entity_type_info in entity_types_to_convert.items():

        if f'{entity_type}Controller' not in entity_types_in_init:
            continue

        controller_path = entity_types_in_init[f'{entity_type}Controller'].replace('.', '/') + '.py'

        if controller_path.startswith('app'):
            path_ = Path(path) / controller_path
        else:  # relative path, starts with dot
            path_ = Path(path) / 'app' / controller_path[1:]

        rel_path = path_.relative_to(path)
        with open(path_, 'rb') as python_file:
            python_source = python_file.read()

        # parse and transform the controller source, similar as __main__.py
        source_tree = libcst.parse_module(python_source)
        source_code = source_tree.code
        modified_tree = source_tree.visit(Transformer(entity_type_info))
        modified_code = modified_tree.code

        if source_code != modified_code:
            _print_diff(source_code, modified_code, rel_path)
            user_response = 'y' if apply else _prompt_user()  # reset user input given for previous diff
            if user_response == 'y':
                _patch_tree(source_code, modified_code, path_, rel_path, keep_original)
                patched_files.append(rel_path)


def _patch_manifest(manifest_path, apply, keep_original, patched_files):
    rel_path = Path('manifest/manifest.yml')
    with open(manifest_path, 'r') as f:
        source_manifest = f.read()
    modified_manifest = _get_modified_manifest(manifest_path)

    if source_manifest != modified_manifest:
        _print_diff(source_manifest, modified_manifest, rel_path)
        user_response = 'y' if apply else _prompt_user()  # reset user input given for previous diff
        if user_response == 'y':
            _patch_tree(source_manifest, modified_manifest, manifest_path, rel_path, keep_original)
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


def _get_entity_types_to_convert(manifest_path: Path) -> dict:
    """ Inspects the manifest and returns the entity-types of which the Controller needs to be converted:

        {
            'EntityA': {
                'label': 'label of EntityA',
                'children: ['EntityB', ...],
                'show_children_as: 'Table'
            },
            'EntityB': {...},
            ...
        }

    """
    entity_types = {}
    with open(manifest_path) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    for entity_type, definition in data.get('entity_types', {}).items():

        entity_type_info = {}
        if 'label' in definition:
            entity_type_info['label'] = definition['label']
        if 'children' in definition:
            entity_type_info['children'] = definition['children']

            if 'show_children_as' in definition:
                entity_type_info['show_children_as'] = definition['show_children_as']

        if entity_type_info:
            entity_types[entity_type] = entity_type_info

    return entity_types


def _create_controller_content(entity_type: str, entity_type_info: dict) -> str:
    label = entity_type_info['label']  # always present
    children = entity_type_info.get('children')  # may be absent
    show_children_as = entity_type_info.get('show_children_as')  # may be absent

    controller_content = f'''from viktor.core import ViktorController
from viktor.views import Summary


class {entity_type}Controller(ViktorController):
    label = '{label}'
    summary = Summary()
'''

    if children:
        controller_content += f"    children = {children}\n"

    if show_children_as:
        controller_content += f"    show_children_as = '{show_children_as}'\n"

    return controller_content


def _get_modified_init(app_init_path: Path, controllers_to_add: List[str]) -> str:
    with open(app_init_path, 'r') as f:
        modified_lines = f.readlines()

    for controller_class_name in controllers_to_add:
        entity_type_folder = _convert_entity_type_name_to_folder(controller_class_name)
        modified_lines.append(f'from .{entity_type_folder}.controller import {controller_class_name}Controller\n')

    return ''.join(modified_lines)


def _get_modified_manifest(manifest_path: Path) -> str:

    in_entity_types = False
    in_children = False

    modified_lines = []
    with open(manifest_path) as f:
        for line in f.readlines():

            if re.search(r'^\s*entities\s*:', line):
                in_entity_types = False
            if re.search(r'^\s*entity_types\s*:', line):
                in_entity_types = True

            if in_entity_types:

                if re.search(r'^\s*label\s*:', line):
                    continue
                if re.search(r'^\s*show_children_as\s*:', line):
                    continue
                if re.search(r'^\s*children\s*:', line):
                    in_children = True
                    continue

                if in_children:
                    if re.search(r'^\s*-', line):
                        continue
                    in_children = False

            modified_lines.append(line)

    return ''.join(modified_lines)


class Transformer(libcst.CSTTransformer):

    def __init__(self, entity_type_info: dict):
        super().__init__()

        self.label = entity_type_info.get('label')
        self.children = entity_type_info.get('children')
        self.show_children_as = entity_type_info.get('show_children_as')

    def leave_ClassDef(self, original_node, updated_node):

        if not match_controller_class(original_node):
            return updated_node

        if not any([self.label, self.children, self.show_children_as]):
            return updated_node

        body = updated_node.body
        class_body: list = list(body.body)
        simple_statements = collect_class_attributes(updated_node)

        if self.show_children_as and 'show_children_as' not in simple_statements:
            value = libcst.SimpleString(f"'{self.show_children_as}'")
            self._add_simple_statement(class_body, 'show_children_as', value)

        if self.children and 'children' not in simple_statements:
            value = libcst.List([libcst.Element(libcst.SimpleString(f"'{c}'")) for c in self.children])
            self._add_simple_statement(class_body, 'children', value)

        if self.label and 'label' not in simple_statements:
            value = libcst.SimpleString(f"'{self.label}'")
            self._add_simple_statement(class_body, 'label', value)

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
