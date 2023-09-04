from viktor._vendor import tomli

from pathlib import Path

from viktor._codemod.__main__ import _prompt_user, _patch_tree, _print_diff, _create_file


def specific_fix(root_dir: Path, apply: bool, keep_original: bool, patched_files: list) -> None:
    viktor_config_path = root_dir / 'viktor.config.toml'

    try:
        with open(viktor_config_path, 'r') as f:
            source_code = f.read()
    except IOError:
        source_code = ""

    modified_code = _get_modified_config(viktor_config_path)

    rel_path = Path('viktor.config.toml')
    if source_code != modified_code:
        _print_diff(source_code, modified_code, rel_path)
        user_response = 'y' if apply else _prompt_user()  # reset user input given for previous diff

        if user_response == 'y':
            _create_file(viktor_config_path, '', rel_path)
            _patch_tree(source_code, modified_code, viktor_config_path, rel_path, keep_original)
            patched_files.append(rel_path)


def _get_modified_config(viktor_config_path: Path) -> str:
    try:
        with open(viktor_config_path, "r") as f:
            source = f.read()
        d = tomli.loads(source)
    except IOError:
        source = ""
        d = {}

    if 'app_type' not in d:
        # add `app_type = "tree"`
        if len(source) > 0 and source[-1] != '\n':
            source += "\n"
        return source + 'app_type = "tree"\n'
    return source
