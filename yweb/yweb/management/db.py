#! /usr/bin/env python
# coding: UTF-8

from yweb.conf import settings
from yweb.utils.findapps import get_app_submodule

def syncdb():

    # 保证 import models 一定成功！
    for app_name in settings.INSTALLED_APPS:
        models = get_app_submodule(app_name, 'models')
        if models:
            exec "from %s.models import *" % app_name
        else:
            print 'W: no models.py, pass %s' % app_name

    from yweb.orm import create_all
    create_all(echo=True)


def dropdb():

    for m in settings.INSTALLED_APPS:
        try:
            exec "from %s.models import *" % m
        except ImportError, e:
            print 'import error: %s' % e
            pass

    from yweb.orm import drop_all
    drop_all(echo=True)

