import re
from pathlib import Path

from viktor._codemod.__main__ import _patch_tree, _print_diff, _prompt_user, _python_file_paths


def specific_fix(root_dir: Path, apply: bool, keep_original: bool, patched_files: list) -> None:
    for source_path in _python_file_paths(root_dir / 'app'):
        with open(source_path) as r:
            source_code = r.read()

        rel_path = source_path.relative_to(root_dir)

        modified_code = _get_modified_code(source_code)

        if source_code != modified_code:
            _print_diff(source_code, modified_code, rel_path)
            user_response = 'y' if apply else ''  # reset user input given for previous diff

            if not user_response:
                user_response = _prompt_user()

            if user_response == 'y':
                _patch_tree(source_code, modified_code, source_path, rel_path, keep_original)
                patched_files.append(rel_path)


def _get_modified_code(source_code: str):
    modified_code = re.sub(r'NumberField.Variant.SLIDER', "'slider'", source_code)
    return re.sub(r'NumberField.Variant.STANDARD', "'standard'", modified_code)
