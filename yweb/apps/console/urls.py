# coding: UTF-8

from tornado.web import url
from . import views
from . import modules

handlers = [

    # Home
    url( r'/console', views.Index,
         name='console' ),

]

ui_modules = {
    'console-navbar': modules.NavBarUI,
}
