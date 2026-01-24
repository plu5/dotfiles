#!/usr/bin/env python3
import os
import json
import time
import argparse
import platform
import subprocess
from datetime import datetime

PROG = 'metaf'
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


def get_file_information_dict(path):
    # type: (str) -> dict
    c_epoch = get_file_creation_epoch(p)
    m_epoch = get_file_modification_epoch(p)
    return {
        'creation': readable_date_from_epoch(c_epoch),
        'creation_epoch': c_epoch,
        'modification': readable_date_from_epoch(m_epoch),
        'modification_epoch': m_epoch,
    }


parser = argparse.ArgumentParser(prog=PROG)
parser.add_argument('path')
parser.add_argument('-s', '--save')
args = parser.parse_args()
parent_path = args.path
save_path = args.save

# TEMP DEBUG
# parent_path = '.'

if not os.path.exists(parent_path):
    print(f'{PROG}: requires a valid path, '
          '\'{parent_path}\' doesn\'t seem to be')
    exit()

files_info_dict = {}
for root, _, files in os.walk(parent_path):
    for f in files:
        p = os.path.join(root, f)
        rel_p = p.removeprefix(parent_path + '/')
        files_info_dict[rel_p] = get_file_information_dict(p)

now = time.time()
out = {'generated': readable_date_from_epoch(now), 'generated_epoch': now,
       'files': files_info_dict}
dump = json.dumps(out, indent=2)
print(dump)  # temp

# if save_path:
#     if os.path.exists(save_path):

# else:
#     print()
