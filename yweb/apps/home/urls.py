from tornado.web import url
from . import views

handlers = [

    # Home
    url( r'/', views.Index,
         name='home' ),

    url( r'/about', views.About,
         name='about' ),

    url( r'/contact', views.Contact,
         name='contact' ),

]
