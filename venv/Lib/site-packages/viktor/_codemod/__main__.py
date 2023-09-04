# When dataclasses is installed within an app, importing libcst raises a
# "module 'typing' has no attribute '_ClassVar'" error, which has to do
# with a combination of python>=3.7 and dataclasses: https://stackoverflow.com/a/58067012
# This is fixed by overruling _is_classvar with the python 3.6 implementation.

def _is_classvar36(a_type, typing):  # https://libcst.readthedocs.io/en/latest/_modules/dataclasses.html
    # This test uses a typing internal class, but it's the best way to
    # test if this is a ClassVar.
    return (a_type is typing.ClassVar
            or (type(a_type) is typing._GenericAlias
                and a_type.__origin__ is typing.ClassVar))

import dataclasses
dataclasses._is_classvar = _is_classvar36

import argparse
import difflib
import importlib
from viktor._vendor import libcst
import os
import re
import shutil
import sys
import traceback

from pathlib import Path
from typing import Iterable, Tuple, Type, List


U_MIN = 87  # to be updated every major with the first UXX fix for the current major!


class PrintStyle:
    RED = '\033[31m'
    GREEN = '\033[32m'
    BOLD = '\033[1m'
    END = '\033[0m'


def fix(root_dir: Path, upgrades: List[int], apply: bool, keep_original: bool):
    """ Initiates the codemod for specified upgrade id.

    :param root_dir: path to the app's root directory.
    :param upgrades: Upgrade IDs to be fixed.
    :param apply: If True, user prompt is skipped and all diffs are applied.
    :param keep_original: If True, the source of modified files is stored in the corresponding .orig.py files.
    """
    for upgrade_id in upgrades:
        print(f"Starting fix U{upgrade_id}")

        patched_files = []
        try:
            fix_upgrade(root_dir, upgrade_id, apply, keep_original, patched_files)
        except Exception:
            print(f"Could not apply fix U{upgrade_id} because of an error:\n\n{traceback.format_exc()}")
        else:
            if patched_files:
                print(f'The following files are modified to fix U{upgrade_id}:')
                for file in patched_files:
                    print(f'  - {file}')
            else:
                print(f'Nothing to fix for U{upgrade_id}')

        print(f"Finished fix U{upgrade_id}")


def fix_upgrade(root_dir: Path, upgrade_id: int, apply: bool, keep_original: bool, patched_files: list) -> None:
    if upgrade_id == 61:
        from viktor._codemod.modifiers.U61 import specific_fix
        specific_fix(root_dir, apply, keep_original, patched_files)
    elif upgrade_id == 66:
        from viktor._codemod.modifiers.U66 import specific_fix
        specific_fix(root_dir, apply, keep_original, patched_files)
    elif upgrade_id == 67:
        from viktor._codemod.modifiers.U67 import specific_fix
        specific_fix(root_dir, apply, keep_original, patched_files)
    elif upgrade_id == 71:
        from viktor._codemod.modifiers.U71 import specific_fix
        specific_fix(root_dir, apply, keep_original, patched_files)
    elif upgrade_id == 77:
        from viktor._codemod.modifiers.U77 import specific_fix
        specific_fix(root_dir, apply, keep_original, patched_files)
    elif upgrade_id == 78:
        from viktor._codemod.modifiers.U78 import specific_fix
        specific_fix(root_dir, apply, keep_original, patched_files)
    else:
        _fix(root_dir, upgrade_id, apply, keep_original, patched_files)


def _fix(root_dir: Path, upgrade_id: int, apply: bool, keep_original: bool, patched_files: list):

    visitor, transformer = _retrieve_modifier(upgrade_id)

    for path_ in _python_file_paths(root_dir / 'app'):
        rel_path = path_.relative_to(root_dir)
        with open(path_, 'rb') as python_file:
            python_source = python_file.read()

        try:
            source_tree = libcst.parse_module(python_source)

            visitor_ = visitor()
            source_tree.visit(visitor_)
            transformer_ = transformer(visitor_)
            modified_tree = source_tree.visit(transformer_)
        except Exception:
            print(f'Something went wrong while attempting to apply fix U{upgrade_id} on {rel_path}')
            continue

        source_code = source_tree.code
        modified_code = modified_tree.code

        if source_code != modified_code:
            _print_diff(source_code, modified_code, rel_path)
            user_response = 'y' if apply else ''  # reset user input given for previous diff

            if not user_response:
                user_response = _prompt_user()

            if user_response == 'y':
                _patch_tree(source_code, modified_code, path_, rel_path, keep_original)
                patched_files.append(rel_path)


def _python_file_paths(path: Path) -> Iterable[Path]:
    """ Walks through the main path and yields .py files (except .orig.py). """
    for dirpath, _, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith('.py') and not filename.endswith('.orig.py'):
                yield Path(dirpath) / filename


def _retrieve_modifier(upgrade_id: int) -> Tuple[Type[libcst.CSTVisitor], Type[libcst.CSTTransformer]]:
    """ Returns the modifier objects (Visitor + Transformer) corresponding to the upgrade id. """
    try:
        module = importlib.import_module(f'viktor._codemod.modifiers.U{upgrade_id}')
    except ModuleNotFoundError:
        sys.exit(f"No fix found for U{upgrade_id}")
    return getattr(module, 'Visitor'), getattr(module, 'Transformer')


def _prompt_user() -> str:
    """ Prompt the user whether he / she wants to apply the diff. """
    while True:
        result = input("Do you want to apply this diff? [y/N]").strip().lower() or 'n'

        if len(result) == 1 and result in {'y', 'n'}:
            return result
        elif result:
            print(f'Invalid response "{result}", please choose either one of [y/n]')


def _patch_tree(source_code: str, modified_code: str, path: Path, rel_path: Path, keep_original: bool) -> None:
    """ Given the file path of the source file, this file is overwritten with the modified tree.

    The 'keep_original' flag can be used to store the original source (source_tree).
    """
    if keep_original:
        orig_path = path.with_suffix(f'.orig{path.suffix}')
        _create_file(orig_path, source_code, rel_path)

    with open(path, 'wb') as f:
        f.write(modified_code.encode('utf-8'))

    print('Applying diff')


def _create_dir(path: Path, rel_path: Path) -> None:
    if os.path.exists(path):
        return

    # directory will be created by the root instead of the user
    # make sure to correctly set the permissions such that the directory can be modified by the user
    os.mkdir(path)
    os.chmod(path, mode=0o777)

    print(f'Created directory: {rel_path}')


def _create_file(path: Path, file_content: str, rel_path: Path) -> None:
    if os.path.exists(path):
        return

    with open(path, 'wb') as f:
        f.write(file_content.encode('utf-8'))

    # file will be created by the root instead of the user
    # make sure to correctly set the permissions such that the file can be modified by the user
    os.chmod(path, mode=0o646)

    print(f'Created file: {rel_path}')


def _delete_file(path: Path, rel_path: Path, keep_original: bool) -> None:
    if keep_original:
        orig_path = path.with_suffix(f'.orig{path.suffix}')
        shutil.copyfile(path, orig_path)

    os.remove(path)

    print(f'Removed file: {rel_path}')


def _terminal_supports_ansi() -> bool:
    """ Returns True if the system's terminal supports ANSI characters, used for coloring.

    Based on django: https://github.com/django/django/blob/master/django/core/management/color.py
    """
    supported_platform = sys.platform != 'win32' or 'ANSICON' in os.environ
    is_a_tty = getattr(sys.stdout, 'isatty', False)
    return supported_platform and is_a_tty


def _print_diff(source_code: str, modified_code: str, old_path: Path = None, new_path: Path = None) -> None:
    """ Prints the diff between source and modified code. """
    diff = difflib.unified_diff(source_code.splitlines(1), modified_code.splitlines(1), str(old_path or ''), str(new_path or old_path))
    for line in diff:
        if _terminal_supports_ansi():
            print(_format_line(line))
        else:
            print(line)


def _format_line(line: str) -> str:
    """ Returns the formatted line based on whether it consists of an addition (+ / +++) or deletion (- / ---). """
    if line.startswith("---"):
        return f"{PrintStyle.RED}{PrintStyle.BOLD}{line.rstrip()}{PrintStyle.END}"
    elif line.startswith("+++"):
        return f"{PrintStyle.GREEN}{PrintStyle.BOLD}{line.rstrip()}{PrintStyle.END}"
    elif line.startswith("-"):
        return f"{PrintStyle.RED}{line.rstrip()}{PrintStyle.END}"
    elif line.startswith("+"):
        return f"{PrintStyle.GREEN}{line.rstrip()}{PrintStyle.END}"
    else:
        return line.rstrip()


if __name__ == '__main__':
    """ This is called from the viktor-cli.

    Possible flags are:
        - `--upgrade` <int>         : denotes the upgrade to be applied
        - `--apply`                 : skip user prompt and apply all diffs
        - `--keep-original`         : store the original .py file as .orig.py
    
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'source_path',
        type=str,
        nargs='+'
    )
    parser.add_argument(
        '--upgrade',
        type=int,
        action='append'
    )
    parser.add_argument(
        '--apply',
        action='store_true'
    )
    parser.add_argument(
        '--keep-original',
        action='store_true'
    )
    args = parser.parse_args()

    # If None upgrades selected, apply all
    if args.upgrade is None:
        _codemods = (Path(__file__).parent / 'modifiers').glob("U[0-9]*.py")
        _upgrades = sorted(i for i in [int(re.search("U([0-9]+)", c.name).group(1)) for c in _codemods] if i >= U_MIN)
    else:
        _upgrades = args.upgrade

    # CLI passes individual folder/files for venv isolation mode. Extract the root_dir from it.
    directories = [Path(path).parent if os.path.isfile(path) else Path(path) for path in args.source_path]
    _root_dir = Path(os.path.commonpath(directories)) if len(directories) > 1 else directories[0]

    fix(_root_dir, _upgrades, args.apply, args.keep_original)
