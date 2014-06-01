# coding: UTF-8

import difflib


def diff(a, b):

    '''比较两字符串差异

    返回差异值
    '''

    a = a.splitlines()
    b = b.splitlines()

    diff = difflib.ndiff(a, b)

    return list(diff)


def restore_diff(diff, obj=1):
    orig = difflib.restore(diff, obj)
    return '\n'.join(orig)


def page_404(handler, msg=None):
    '''查找的对象不存在
    '''
    handler.set_status(404)
    handler.render("blog/404.html", msg=msg)

