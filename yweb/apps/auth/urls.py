# coding: utf-8

from tornado.web import url
from . import views
from . import apis


handlers = [

    # 登录
    url( r'/auth/signin', views.SignIn,
         name='auth:signin' ),

    # 退出
    url( r'/auth/signout', views.SignOut,
         name='auth:signout' ),

    # 注册：指向步骤1
    url( r'/auth/signup', views.SignUpStep1,
         name='auth:signup' ),

    # 注册步骤1: 申请
    url( r'/auth/signup/step1', views.SignUpStep1,
         name='auth:signup:step1' ),

    # 注册步骤2: 创建新用户
    url( r'/auth/signup/step2', views.SignUpStep2,
         name='auth:signup:step2' ),

    # 密码重置：指向步骤1
    url( r'/auth/password/reset', views.PasswordResetStep1,
         name='auth:password:reset' ),

    # 密码重置步骤1：申请
    url( r'/auth/password/reset/step1', views.PasswordResetStep1,
         name='auth:password:reset:step1' ),

    # 密码重置步骤2：重置密码
    url( r'/auth/password/reset/step2', views.PasswordResetStep2,
         name='auth:password:reset:step2' ),

]

api_handlers = [

    url( r'/auth/authcode/([0-9a-zA-Z]+).gif', apis.AuthCodeImg,
         name='auth:authcode:img' ),
]
