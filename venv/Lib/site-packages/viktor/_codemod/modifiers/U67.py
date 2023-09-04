from pathlib import Path

from viktor._codemod.__main__ import _prompt_user, _patch_tree, _print_diff


def specific_fix(root_dir: Path, apply: bool, keep_original: bool, patched_files: list) -> None:
    requirements_path = root_dir / 'requirements.txt'
    rel_path = requirements_path.relative_to(root_dir)

    try:
        with open(requirements_path, 'r') as f:
            source_code = f.read()
    except OSError:
        raise FileNotFoundError("No file named 'requirements.txt' found") from None

    modified_code = _get_modified_code(requirements_path)

    if source_code != modified_code:
        _print_diff(source_code, modified_code, rel_path)
        user_response = 'y' if apply else ''  # reset user input given for previous diff

        if not user_response:
            user_response = _prompt_user()

        if user_response == 'y':
            _patch_tree(source_code, modified_code, requirements_path, rel_path, keep_original)
            patched_files.append(rel_path)


def _get_modified_code(requirements_path: Path) -> str:
    modified_lines = []
    with open(requirements_path, 'r') as f:
        for line in f:
            if line.startswith("geolib"):
                line = "d-geolib==0.1.6"
            modified_lines.append(line)

    return ''.join(modified_lines)
