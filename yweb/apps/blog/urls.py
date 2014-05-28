# coding: UTF-8

from tornado.web import url
from . import views
from . import console


handlers = [

    url('/imind', views.Index, name='imind:index'),

    url('/imind/([0-9]+)', views.ImindView, name='imind:view'),

    url('/imind/new', views.ImindNew, name='imind:new'),


    # 重定向旧文章路径
    url('/imind/([0-9]+)', views.TempRedirect1),
    url('/([0-9]+)', views.TempRedirect1),
    url('/forum/t/([0-9]+)', views.TempRedirect1),
    url('/forum/t/([0-9]+).*', views.TempRedirect1),

    # 重定向旧文章列表首页
    url('/imind.*', views.TempRedirect2),
    url('/forum.*', views.TempRedirect2),
    url('/wiki.*', views.TempRedirect2),

    # console

    url( '/console/imind', console.Index,
         name='console:imind:index' ),
    url( '/console/imind/list', console.ImindList,
         name='console:imind:list' ),
    url( '/console/imind/new', console.ImindNew,
         name='console:imind:new' ),
    url( '/console/imind/([0-9]+)/edit', console.ImindEdit,
         name='console:imind:edit' ),

]
