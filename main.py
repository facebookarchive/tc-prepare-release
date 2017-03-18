from __future__ import print_function

import sys
import os
import subprocess
from distutils import dir_util

import argparse
import random
import logging
import traceback


class cd:
    def __init__(self, new_path, with_backup):
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


def stash_stuff():
    logging.info("Stashing dirt")
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
    find_and_replace('CMakeLists.txt',
                     old_v.replace('-', '.'), new_v.replace('-', '.'))
    find_and_replace('quick_setup.sh', old_v, new_v)

    new_rock = 'torchcraft-%s.rockspec' % new_v
    logging.info("Creating %s" % new_rock)
    os.rename(rock, new_rock)


def make_commit(new_v):
    logging.debug("Adding modified files...")
    subprocess.check_output(['git', 'add', 'CMakeLists.txt'])
    subprocess.check_output(['git', 'add', 'torchcraft*'])
    subprocess.check_output(['git', 'add', 'quick_setup.sh'])
    logging.info("Creating commit for version %s" % new_v)
    subprocess.check_output([
        'git', 'commit', '-m', 'Auto: Update version files to v%s' % new_v
    ])


def push(branch_name):
    logging.info("Pushing new branch %s" % branch_name)
    subprocess.check_output([
        'git', 'push', 'origin', branch_name])


def create_zip():
    pass


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
            create_zip()
    except:
        if good_repo:
            # HACK HACK HACK If you are wondering why we do this, it's because
            # it makes debugging / development easier. I'm sorry.
            with cd(args.tcdir, False):
                subprocess.check_output(['git', 'checkout', 'develop'])
                subprocess.check_output(['git', 'checkout', 'develop'])
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)


if __name__ == '__main__':
    main()
