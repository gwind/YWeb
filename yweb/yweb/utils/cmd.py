# coding: UTF-8

import os
import logging
import subprocess  


def run_cmd(cmd_string):

    '''运行 CMD

    '''

#    logging.debug('PWD: {0}'.format(os.getcwd()))
    
    ret = subprocess.call(cmd_string.split())
    if ret != 0:
        logging.error('CMD failed: {0}'.format(cmd_string))

    return ret


def find_files(path, suffixes=[]):

    files = []

    bakdir = os.getcwd()
    os.chdir(path)

    def _checked(filename):
        for s in suffixes:
            if filename.endswith(s):
                return True

        return False

    for f in os.listdir('.'):

        if f in ['.', '..']:
            continue

        if os.path.isdir(f):
            for x in find_files(f, suffixes):
                files.append( os.path.join(path, x) )
        else:
            if _checked(f):
                files.append( os.path.join(path, f) )

    os.chdir(bakdir)
    return files
