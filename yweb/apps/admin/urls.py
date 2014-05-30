from tornado.web import url
from . import views
from . import modules

handlers = [

    # Home
    url( r'/admin', views.Index,
         name='admin' ),

]

ui_modules = {
    'admin-navbar': modules.NavBarUI,
}
