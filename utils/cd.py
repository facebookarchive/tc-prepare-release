import os
from distutils import dir_util
import logging
import random


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
