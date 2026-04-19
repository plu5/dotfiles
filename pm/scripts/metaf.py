#!/usr/bin/env python3
# metaf
# 2026-01-23 19:32
"""Recurses files under a given path saving information (metadata)
about each file to a json structure.

Example usage:
metaf.py . -s
"""
import os
import json
import time
import argparse
import platform
import subprocess
from datetime import datetime

PROG = 'metaf'
DEFAULTSAVENAME = 'metaf.json'
DATEFORMAT = '%F %T'

FORMATOPTIONS = {
    'C': 'creation', 'c': 'creation epoch',
    'M': 'modification', 'm': 'modification epoch',
    't': 'type',
}
DEFAULTFORMATOPTIONS = 'CcMm'

QUIET = False


def msg(text):
    # type: (str) -> None
    """Utility for logs/errors, could be replaced with proper logging"""
    if not QUIET:
        print(f'{PROG}: {text}')


def get_file_modification_epoch(path):
    # type: (str) -> float
    return os.path.getmtime(path)


def get_ext4_file_creation_epoch(path):
    # type: (str) -> float
    c = subprocess.run([
        'stat', path, '--format', '%W'
    ], capture_output=True)
    return float(c.stdout.decode())


def get_ntfs3g_file_creation_epoch(path):
    # type: (str) -> float
    c = subprocess.run([
        'getfattr', '--only-values', '--name=system.ntfs_crtime', path
    ], capture_output=True)
    return int.from_bytes(c.stdout, 'little')/10000000-11644473600


def get_file_creation_epoch(path):
    # type (str) -> float
    """Try to get the right file creation epoch time
    for the operating system and filesystem
    """
    # Mark Amery https://stackoverflow.com/a/39501288/18396947
    if platform.system() == 'Windows':
        return os.path.getctime(path)
    else:
        stat = os.stat(path)
        try:
            return stat.st_birthtime
        except AttributeError:
            c_epoch = get_ext4_file_creation_epoch(path)
            if not c_epoch:
                c_epoch = get_ntfs3g_file_creation_epoch(path)
            return c_epoch


def readable_date_from_epoch(epoch):
    # type: (float) -> str
    return datetime.fromtimestamp(epoch).strftime(DATEFORMAT)


def get_file_type(path):
    # type: (str) -> str
    c = subprocess.run([
        'file', '--mime-type', path
    ], capture_output=True)
    return c.stdout.decode().split()[-1]


def fields_to_update(path, fmt, existing):
    # type: (str, str, dict) -> str
    ret = []
    m = existing.get(FORMATOPTIONS['m'])
    if not m:
        msg(f"{path} no modification date in data, updating all fields.")
        return fmt              # update everything
    new_m = get_file_modification_epoch(path)
    if new_m < m:               # older
        msg(f"{path} new modification date is older than existing one. How is "
            f"this possible? ({new_m} < {m}). Keeping data as is.")
    elif new_m > m:             # newer
        msg(f"File {path} changed ({new_m} > {m})")
        return fmt              # update everything
    else:                       # equal
        # check if there are new fields in fmt
        for k, v in FORMATOPTIONS.items():
            if k in fmt and v not in existing:
                ret.append(k)
        if len(ret):
            msg(f"File {path} hasn't changed, but new fields requested {ret}")
    return ''.join(ret)


def get_file_information(path, fmt, existing=None):
    # type: (str, str, dict | None) -> dict
    """Get information about file in PATH. FMT defines which
    information to get. EXISTING files data can be provided from a
    previous run to update it if FMT contain fields not there or if
    the data contains a modification date older than the file has on
    disk, otherwise return it as is.
    """
    res = {}

    if existing:
        fmt = fields_to_update(path, fmt, existing)
        if not fmt:
            return existing
        res = existing

    c = get_file_creation_epoch(path) if 'c' in fmt.lower() else None
    m = get_file_modification_epoch(path) if 'm' in fmt.lower() else None

    dispatch = {
        'c': lambda: c,
        'm': lambda: m,
        'C': lambda: readable_date_from_epoch(c),
        'M': lambda: readable_date_from_epoch(m),
        't': lambda: get_file_type(path),
    }

    for char in fmt:
        opt = FORMATOPTIONS.get(char)
        if not opt or char not in dispatch:
            continue
        res[opt] = dispatch[char]()

    return res


def get_files_information_recursively(
        parent_path, fmt, include_subdirs=False, existing=None):
    # type: (str, str, bool, dict | None) -> dict
    """Recurse PARENT_PATH and get information recursively about each
    file. FMT defines which information to get about each file. If
    INCLUDE_SUBDIRS, get information about subdirectories
    too. EXISTING files data can be provided from a previous run to
    use existing data unless there is a modification date listed and
    it is older than the file has on disk, or FMT includes fields not
    in the data.
    """
    files_info_dict = {}

    def process_file_or_subdir(root, name, is_subdir=False):
        # type: (str, str, bool) -> None
        p = os.path.join(root, name)
        rel_p = p.removeprefix(parent_path + '/')
        e = existing.get(rel_p) if existing else None
        if existing and not e:
            msg(f"File {p} is new")
        try:
            files_info_dict[rel_p] = get_file_information(p, fmt, e)
        except FileNotFoundError as e:
            if is_subdir:
                raise e
            else:
                msg(f'{p} not found - broken symlink? Exception: {e}'
                    '\nSkipping.')

    for root, subdirs, files in os.walk(parent_path):
        if include_subdirs:
            for f in subdirs:
                process_file_or_subdir(root, f, is_subdir=True)
        for f in files:
            process_file_or_subdir(root, f)

    return files_info_dict


def read_existing(path):
    # type: str -> dict | None
    existing = None
    with open(path, "r") as f:
        existing = json.load(f)
    return existing


def parse_args():
    parser = argparse.ArgumentParser(prog=PROG)
    parser.add_argument('path')
    parser.add_argument(
        '-q', '--quiet', action='store_true',
        help='Suppress messages in output.')
    parser.add_argument(
        '-f', '--format', default=DEFAULTFORMATOPTIONS,
        help='Which metadata fields to include and in which order. '
        f'Default: {DEFAULTFORMATOPTIONS}. '
        'Options: '
        f'{", ".join([f"{k} ({v})" for k, v in FORMATOPTIONS.items()])}.')
    parser.add_argument(
        '--sort', choices=[x for k in FORMATOPTIONS for x in (k, k + 'r')],
        help='Sort by a given metadata field. Options are the same as for '
        '-f/--format, or followed by r for reverse order. '
        '(Example: cr -> sort by creation epoch, reverse order.)')
    parser.add_argument(
        '-a', '--all', action='store_true',
        help='Include metadata for directories too.')
    parser.add_argument(
        '-s', '--save', action='store_true',
        help='Save output to file instead of printing to stdout. '
        f'Will save to PATH/{DEFAULTSAVENAME} unless a different path '
        'is provided with the -t/--save-to option.')
    parser.add_argument(
        '-t', '--save-to',
        help='Path to save output to. '
        'Ignored if -s/--save is not provided.')
    parser.add_argument(
        '-o', '--overwrite', action='store_true',
        help='Overwrite save file if it already exists. '
        'Ignored if -s/--save is not provided.')
    parser.add_argument(
        '-u', '--update', action='store_true',
        help='Update save file if it already exists. '
        'This will add new items and update items whose modification date has '
        'changed. '
        'Ignored if -s/--save is not provided. If both -o/--overwrite '
        'and -u/--update are provided, overwrite will take precedence.')
    # REMARK(plu5): Maybe add "exists" field on items so that when
    # using --update, items that no longer exist on disk can have
    # their "exists" field set to False.
    return parser.parse_args()


def main():
    # type: () -> None
    global QUIET

    args = parse_args()
    QUIET = args.quiet
    parent_path = args.path

    # parent_path = '.'  # debug

    if not os.path.exists(parent_path):
        msg(f'requires a valid path, \'{parent_path}\' doesn\'t seem to be')
        exit()

    existing = None             # existing files data

    # Fail fast if save file already exists and overwrite is False
    # unless update is True
    if args.save and not args.overwrite:
        save_to = args.save_to or os.path.join(parent_path, DEFAULTSAVENAME)
        if os.path.exists(save_to):
            if not args.update:
                msg(f'Save file \'{save_to}\' already exists. '
                    'Run with -u/--update if you wish to update it. '
                    'Run with -o/--overwrite if you wish to overwrite it. '
                    'Run with -t/--save-to to specify a different save file.')
                exit()
            # update
            existing = read_existing(save_to)
            try:
                existing = existing['files']
            except KeyError:
                msg('Invalid existing data; expected key "files" in',
                    existing)
                exit()

    now = time.time()

    d = get_files_information_recursively(
        parent_path, args.format, args.all, existing)

    def sort_key(item):
        key, value = item
        k = FORMATOPTIONS[args.sort[0]]
        data_to_sort_by = value.get(k, None)
        if data_to_sort_by is None:
            msg(f"{k} not in file data, can't sort by it")
            data_to_sort_by = False
        # REMARK(plu5): I set it ^ to False because one can't compare
        # None to None, but comparing booleans is fine. If we get None
        # for one element, we should get None for all of them, as all
        # data for each file should have the same keys.
        return data_to_sort_by

    if args.sort:
        reverse = True if len(args.sort) > 1 and args.sort[1] == 'r' else False
        d = dict(sorted(d.items(), key=sort_key, reverse=reverse))

    out = {'generated': readable_date_from_epoch(now), 'generated_epoch': now,
           'files': d}
    dump = json.dumps(out, indent=2)

    if args.save:
        save_to = args.save_to or os.path.join(parent_path, DEFAULTSAVENAME)
        open_as = 'w' if args.overwrite or args.update else 'x'
        with open(save_to, open_as) as f:
            f.write(dump)
    else:
        print(dump)


if __name__ == '__main__':
    main()
