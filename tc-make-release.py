#!/usr/bin/env python
from __future__ import print_function

import os
import sys
import subprocess
from distutils import dir_util
from shutil import copyfile

import argparse
import random
import logging


class cd:
    def __init__(self, new_path, with_backup=False):
        self.new_path = os.path.expanduser(new_path)
        self.with_backup = with_backup

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.new_path)
        logging.info('Entering %s' % self.new_path)
        if self.with_backup:
            self.__backup_dir()

    def __exit__(self, et, val, tb):
        os.chdir(self.savedPath)

    def __backup_dir(self):
        # what could possibly go wrong...
        dest = '../TC_BACKUP_' + ('%05d' % random.randint(0, 99999))
        logging.info('Backing up directory into %s' % dest)
        dir_util.copy_tree(self.new_path, dest)


def has_develop():
    logging.debug('Checking whether develop branch exists...')
    results = subprocess.check_output(['git', 'branch'])
    return 'develop' in results.decode('utf-8')


def is_on_develop():
    logging.debug('Checking for develop branch...')
    branch = subprocess.check_output(
        ['git', 'symbolic-ref', '--short', 'HEAD'])
    branch = branch[:-1]  # remove newline
    logging.debug('Found branch %s' % branch.decode('utf-8'))
    assert branch == b'develop', 'Current branch is not develop'


def copy_files(c_pwd, new_v):
    v = 'torchcraft-v%s' % new_v
    s = '%s/out/%s' % (c_pwd, v)

    dir_util.mkpath(s)

    dest = s + '/maps'
    dir_util.copy_tree('./maps/', dest)
    dest = s + '/config'
    dir_util.copy_tree('./config/', dest)
    dest = s + '/bin'
    dir_util.copy_tree('./BWEnv/bin/', dest)


def make_zip(new_v):
    s = 'torchcraft-v%s' % new_v

    if sys.platform in ['win32', 'cygwin']:
        raise NotImplementedError
    else:
        zip_foo = 'zip -r %s.zip %s/' % (s, s)

    copyfile('BWEnv.dll', s + '/BWEnv.dll')
    copyfile('BWEnv.exe', s + '/BWEnv.exe')

    subprocess.check_output(zip_foo.split(' '))


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'new_version', type=str, help='Version to update TorchCraft to')
    parser.add_argument(
        'tcdir',
        type=str,
        help='TorchCraft directory path (relative or absoute)')
    parser.add_argument(
        '-d', action='store_true', help='Print debug information')
    args = parser.parse_args()

    if args.d:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    c_pwd = os.getcwd()
    with cd(args.tcdir):
        has_develop()
        is_on_develop()
        copy_files(c_pwd, args.new_version)
    with cd('./out/'):
        make_zip(args.new_version)


if __name__ == '__main__':
    main()
