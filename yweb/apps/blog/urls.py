# coding: UTF-8

from tornado.web import url
from . import views
from . import consoles


handlers = [

    url('/blog', views.Index, name='blog:index'),

    url('/blog/article/([0-9]+)', views.ArticleView,
        name='blog:article:view'),

    url('/blog/article/([0-9]+)/post/all', views.ArticlePostAll,
        name='blog:article:post:all'),

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

#    url( '/console/imind/list', console.ImindList,
#         name='console:imind:list' ),
#    url( '/console/imind/new', console.ImindNew,
#         name='console:imind:new' ),
#    url( '/console/imind/([0-9]+)/edit', console.ImindEdit,
#         name='console:imind:edit' ),

]

console_handlers = [

    url( '/console/blog', consoles.Index,
         name='console:blog' ),

    url( '/console/blog/article/all', consoles.ArticleAll,
         name='console:blog:article:all' ),

    url( '/console/blog/article/new', consoles.ArticleNew,
         name='console:blog:article:new' ),

    url( '/console/blog/article/([0-9]+)/edit', consoles.ArticleEdit,
         name='console:blog:article:edit'),

]
