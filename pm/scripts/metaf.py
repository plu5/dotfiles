#!/usr/bin/env python3
"""Recurses files under a given path saving information (metadata)
about each file to a json structure.
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


def get_file_information(path):
    # type: (str) -> dict
    c_epoch = get_file_creation_epoch(path)
    m_epoch = get_file_modification_epoch(path)
    return {
        'creation': readable_date_from_epoch(c_epoch),
        'creation_epoch': c_epoch,
        'modification': readable_date_from_epoch(m_epoch),
        'modification_epoch': m_epoch,
    }


def get_files_information_recursively(parent_path):
    # type: (str) -> dict
    files_info_dict = {}
    for root, _, files in os.walk(parent_path):
        for f in files:
            p = os.path.join(root, f)
            rel_p = p.removeprefix(parent_path + '/')
            files_info_dict[rel_p] = get_file_information(p)
    return files_info_dict


def parse_args():
    parser = argparse.ArgumentParser(prog=PROG)
    parser.add_argument('path')
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
        '-f', '--overwrite', action='store_true',
        help='Overwrite save file if it already exists. '
        'Ignored if -s/--save is not provided.')
    return parser.parse_args()


def main():
    # type: () -> None
    args = parse_args()
    parent_path = args.path

    # parent_path = '.'  # debug

    if not os.path.exists(parent_path):
        print(f'{PROG}: requires a valid path, '
              '\'{parent_path}\' doesn\'t seem to be')
        exit()

    now = time.time()
    out = {'generated': readable_date_from_epoch(now), 'generated_epoch': now,
           'files': get_files_information_recursively(parent_path)}
    dump = json.dumps(out, indent=2)

    if args.save:
        save_to = args.save_to or os.path.join(parent_path, DEFAULTSAVENAME)
        open_as = 'w' if args.overwrite else 'x'
        with open(save_to, open_as) as f:
            f.write(dump)
    else:
        print(dump)


if __name__ == '__main__':
    main()
