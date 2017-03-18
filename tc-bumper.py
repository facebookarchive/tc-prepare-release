#!/usr/bin/env python
from __future__ import print_function

import sys
import os
import subprocess
import argparse
import random
import logging
import traceback

from utils import cd


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


def stash_stuff():
    logging.info('Stashing dirt')
    subprocess.check_output(['git', 'stash'])


def pull_repo():
    logging.info('Pulling origin/develop')
    result = subprocess.check_output(['git', 'pull', 'origin', 'develop'])
    logging.debug('Git pull output:')
    logging.debug(result)


def create_new_branch():
    logging.info('Creating branch new_release')
    try:
        branch_name = 'new_release'
        subprocess.check_output(['git', 'checkout', '-b', branch_name])
    except:
        # What could possibly go wrong v2.0
        branch_name = 'new_release_%05d' % random.randint(0, 99999)
        subprocess.check_output(['git', 'checkout', '-b', branch_name])
    logging.info('Created branch %s', branch_name)
    return branch_name


def find_and_replace(file_path, old_s, new_s):
    with open(file_path, 'r') as file:
        source = file.read()
    source = source.replace(old_s, new_s)
    with open(file_path, 'w') as file:
        file.write(source)


def update_versions(old_v, new_v):
    # TODO validate versions

    rock = 'torchcraft-%s.rockspec' % old_v

    find_and_replace(rock, old_v, new_v)
    find_and_replace('quick_setup.sh', old_v, new_v)

    find_and_replace('CMakeLists.txt',
                     old_v.replace('-', '.'), new_v.replace('-', '.'))

    new_rock = 'torchcraft-%s.rockspec' % new_v
    logging.info('Creating %s' % new_rock)
    os.rename(rock, new_rock)


def make_commit(new_v):
    logging.debug('Adding modified files...')
    subprocess.check_output(['git', 'add', 'CMakeLists.txt'])
    subprocess.check_output(['git', 'add', 'torchcraft*'])
    subprocess.check_output(['git', 'add', 'quick_setup.sh'])
    logging.info('Creating commit for version %s' % new_v)
    subprocess.check_output(
        ['git', 'commit', '-m', 'Auto: Update version files to v%s' % new_v])


def push(branch_name):
    logging.info('Pushing new branch %s' % branch_name)
    subprocess.check_output(['git', 'push', 'origin', branch_name])


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'old_version', type=str, help='Version to update TorchCraft from')
    parser.add_argument(
        'new_version', type=str, help='Version to update TorchCraft to')
    parser.add_argument(
        'tcdir',
        type=str,
        help='TorchCraft directory path (relative or absoute)')
    parser.add_argument(
        '-d', action='store_true', help='Print debug information')
    parser.add_argument(
        '-b', action='store_true', help='Backup TorchCraft directory')
    parser.add_argument(
        '-s', action='store_true', help='Stash dirt in repository')
    parser.add_argument(
        '--cheat',
        action='store_true',
        help=('CHEAT MODE (USE WITH CAUTION *AND*' +
              ' ONLY IF YOU ARE DEVELOPING TC-BUMPER)'))
    parser.add_argument(
        '--make_zip',
        action='store_true',
        help='If used, makes the script only produce a zip file.')
    args = parser.parse_args()

    if args.d:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    good_repo = False
    try:
        # May the Functional Programming God forgive me
        with cd(args.tcdir, args.b):
            has_develop()
            good_repo = True

            is_on_develop()
            if args.s:
                stash_stuff()
            pull_repo()
            branch = create_new_branch()

            update_versions(args.old_version, args.new_version)

            make_commit(args.new_version)
            push(branch)
    except:
        if args.cheat and good_repo:
            # HACK HACK HACK If you are wondering why we do this, it's because
            # it makes debugging / development easier. I'm sorry.
            with cd(args.tcdir, False):
                subprocess.check_output(['git', 'checkout', 'develop'])
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)


if __name__ == '__main__':
    main()
