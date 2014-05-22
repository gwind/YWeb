# -*- coding: utf-8 -*-
# yweb.utils 模块

import pprint

# fopen 参考 salt.utils.fopen
def fopen(*args, **kwargs):
    '''
    Wrapper around open() built-in to set CLOEXEC on the fd.

    This flag specifies that the file descriptor should be closed when an exec
    function is invoked;
    When a file descriptor is allocated (as with open or dup), this bit is
    initially cleared on the new file descriptor, meaning that descriptor will
    survive into the new program after exec.

    NB! We still have small race condition between open and fcntl.
    '''
    # Remove lock from kwargs if present
    lock = kwargs.pop('lock', False)

    fhandle = open(*args, **kwargs)
    if is_fcntl_available():
        # modify the file descriptor on systems with fcntl
        # unix and unix-like systems only
        try:
            FD_CLOEXEC = fcntl.FD_CLOEXEC   # pylint: disable=C0103
        except AttributeError:
            FD_CLOEXEC = 1                  # pylint: disable=C0103
        old_flags = fcntl.fcntl(fhandle.fileno(), fcntl.F_GETFD)
        if lock and is_fcntl_available(check_sunos=True):
            fcntl.flock(fhandle.fileno(), fcntl.LOCK_SH)
        fcntl.fcntl(fhandle.fileno(), fcntl.F_SETFD, old_flags | FD_CLOEXEC)
    return fhandle


def yprint(obj):
    return pprint.PrettyPrinter().pformat( obj )

def yprint_dict( d ):

    max_klen = 0

    for k in d:
        if len(k) > max_klen:
            max_klen = len(k)

    format_s = '%%%ss : %%s\n' % max_klen
    s = ''
    for k in d:
        s += format_s % (k, d[k])

    return s.rstrip()
