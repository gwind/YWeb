from tornado.web import url
from . import views
from . import modules

handlers = [

    # Home
    url( r'/i18n/setlang/([a-zA-Z_]+)', views.SetLocale,
         name='i18n:setlang' ),

]

ui_modules = {
    'setlang': modules.SetLang,
}
