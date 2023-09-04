import re
from viktor._vendor import yaml
from pathlib import Path

from viktor._codemod.__main__ import _prompt_user, _patch_tree, _print_diff


_KEYS = [
    'background_image',
    'logo_primary',
    'logo_light',
    'logo_white',
    'primary_color',
    'secondary_color',
    'favicon',
    'title'
]


def specific_fix(root_dir: Path, apply: bool, keep_original: bool, patched_files: list) -> None:
    manifest_path = root_dir / 'manifest' / 'manifest.yml'
    if not manifest_path.is_file():
        manifest_path = root_dir / 'manifest' / 'manifest.yaml'
        if not manifest_path.is_file():
            return

    rel_path = manifest_path.relative_to(root_dir)

    with open(manifest_path, 'r') as f:
        source_code = f.read()

    modified_code = _get_modified_code(manifest_path)

    if source_code != modified_code:
        _print_diff(source_code, modified_code, rel_path)
        user_response = 'y' if apply else ''  # reset user input given for previous diff

        if not user_response:
            user_response = _prompt_user()

        if user_response == 'y':
            _patch_tree(source_code, modified_code, manifest_path, rel_path, keep_original)
            patched_files.append(rel_path)


def _get_modified_code(source_path: Path) -> str:

    with open(source_path) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    metadata = data.get('metadata', {})
    for key_ in _KEYS:
        if key_ in metadata:
            del metadata[key_]

    remove_metadata = False
    if not metadata:
        remove_metadata = True

    modified_lines = []
    with open(source_path, 'r') as f:
        for line in f.readlines():
            if remove_metadata and re.search(r'^\s*metadata\s*:', line):
                continue
            if any(re.search(rf'^\s*{key_}\s*:', line) for key_ in _KEYS):
                continue
            modified_lines.append(line)
    return ''.join(modified_lines)
