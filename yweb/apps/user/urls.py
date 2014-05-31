# coding: utf-8

from tornado.web import url
from . import views


handlers = [

    # user access
    # e.g. http://www.youtube.com/user/saltstack

    # /u/ID
    # /user/USERNAME（或 slug）

    url( r'/user/([0-9]+)', views.Index, name='user' ),

]
