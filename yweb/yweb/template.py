# coding: utf-8

import logging

import mako
from mako.lookup import TemplateLookup

from yweb.conf import settings
from yweb.utils.findapps import get_site_template_dirs


def get_template_lookup():

    template_dirs = get_site_template_dirs()
    logging.debug('find template dirs: {0}'.format(template_dirs))

    # 初始化 mako
    mako.runtime.UNDEFINED = '' # 未定义的变量不会出错

    lookup = TemplateLookup(template_dirs, input_encoding="utf-8")

    return lookup

