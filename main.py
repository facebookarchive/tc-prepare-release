import sys
import os
import subprocess
from distutils import dir_util

import argparse
import random
import logging
import traceback


class cd:
    '''Context manager for changing the current working directory'''

    def __init__(self, newPath, with_backup):
        self.newPath = os.path.expanduser(newPath)
        self.with_backup = with_backup

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)
        logging.info('Entering %s' % self.newPath)

        if self.with_backup:
            self.__backup_dir()

    def __exit__(self, etype, value, tb):
        os.chdir(self.savedPath)

    def __backup_dir(self):
        # what could possibly go wrong...
        dest = '../TC_BACKUP_' + ('%05d' % random.randint(0, 99999))
        logging.info('Backing up directory into %s' % dest)
        dir_util.copy_tree(self.newPath, dest)
        logging.info('Done')


def has_develop():
    logging.debug('Checking whether develop branch exists...')
    results = subprocess.check_output(['git', 'branch'])
    return 'develop' in results.decode('utf-8')


def check_repo():
    logging.debug('Checking for develop branch...')
    branch = subprocess.check_output(
        ['git', 'symbolic-ref', '--short', 'HEAD'])
    branch = branch[:-1]  # remove newline
    logging.debug('Found branch %s' % branch.decode('utf-8'))
    assert branch == b'develop', 'Current branch is not develop'


def pull_repo():
    logging.info('Pulling origin/develop...')
    result = subprocess.check_output(['git', 'pull', 'origin', 'develop'])
    logging.debug('Git pull output:')
    logging.debug(result)
    logging.info('Done')


def create_new_branch():
    logging.info('Creating branch new_release...')
    try:
        branch_name = 'new_release'
        subprocess.check_output(['git', 'checkout', '-b', branch_name])
    except:
        # What could possibly go wrong v2.0
        branch_name = 'new_release_%05d' % random.randint(0, 99999)
        subprocess.check_output(['git', 'checkout', '-b', branch_name])
    logging.info('Created branch %s', branch_name)


def update_versions():
    pass


def make_commit():
    pass


def push():
    pass


def create_zip():
    pass


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'tcdir',
        type=str,
        help='TorchCraft directory path (relative or absoute)')
    parser.add_argument(
        '-d', action='store_true', help='Print debug information')
    parser.add_argument(
        '-b', action='store_true', help='Backup TorchCraft directory')
    args = parser.parse_args()

    if args.d:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    good_repo = False
    try:
        with cd(args.tcdir, args.b):
            # Side effects ftw
            has_develop()
            good_repo = True
            check_repo()
            pull_repo()
            create_new_branch()
            update_versions()
            make_commit()
            push()
            create_zip()
    except:
        if good_repo:
            # HACK HACK HACK If you are wondering why we do this, it's because
            # it makes debugging / development easier. I'm sorry.
            with cd(args.tcdir, False):
                subprocess.check_output(['git', 'checkout', 'develop'])
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)


if __name__ == '__main__':
    main()
