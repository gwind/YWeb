#! /usr/bin/env python
# coding: utf-8

from yweb.conf import settings


def syncdb():

    for m in settings.INSTALLED_APPS:
        try:
            exec "from %s.models import *" % m
        except ImportError, e:
            print 'import error: %s' % e
            pass

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

