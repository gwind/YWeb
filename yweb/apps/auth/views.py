# coding: utf-8

import os
import json
import logging
import random
import pickle
import base64
import time
import datetime
from hashlib import sha1

from sqlalchemy import and_

from tornado.web import authenticated
from yweb.handler import RequestHandler as YwebRequestHandler
from yweb.conf import settings
from yweb.mail import sendmail
from yweb.utils.translation import ugettext_lazy as _

from apps.auth.models import User, Session, Group, \
    AuthKey, create_user, create_authkey

from .forms import SignInForm, SignUpForm, UserCreateForm, \
    PasswordResetForm, PasswordResetStep2Form
from .utils import enc_login_passwd


class RequestHandler(YwebRequestHandler):

    @property
    def host_url(self):
        return "%s://%s" % (self.request.protocol, self.request.host)

    def save_session(self, data):

        '''保存用户会话凭证

        '''

        # 得到新 key
        while True:
            skey = sha1( os.urandom(64) ).hexdigest()
            c = self.db.query(Session).filter_by(skey=skey).count()
            if not c:
                break
            
        session = Session(skey, data)
        self.db.add(session)
        self.db.commit()
        self.clear_cookie('session_key')
        self.set_secure_cookie('session_key', skey)

    def clear_session(self):

        '''删除用户会话凭证

        '''

        skey = self.get_secure_cookie('session_key')
        session = self.db.query(Session).filter_by(skey=skey).first()
        self.db.delete(session)
        self.db.commit()
        self.clear_all_cookies()


class SignIn(RequestHandler):

    '''用户登录

    '''

    def prepare(self):

        if self.current_user:
            # 如果用户己经登录
            # 方法一：重定向
            #self.redirect('/')
            # 方法二：宣传
            return self.render('auth/resignin.html')

        self.template_path = 'auth/signin.html'
        self.title =  _('Login')
        self.data = { 'form': SignInForm(self) }

    def post(self):

        # 检查 authcode
        if not self.check_authcode():
            return self.render(authcode_failed=True)

        form = self.data['form']
        if form.validate():
            user = form._user
            self.save_session({'user_id': user.id})
            user.last_login = datetime.datetime.now()
            self.db.commit()
            
            next_url = self.get_argument('next_url', '/')
            return self.redirect( next_url )

        self.render()


class SignOut(RequestHandler):

    '''用户注销/退出

    '''

    def get(self):
        if self.current_user:
            self.clear_session()
        next_url = self.get_argument('next_url', '/')
        self.redirect(next_url)


class SignUpStep1(RequestHandler):

    '''注册步骤1：申请注册

    '''

    def prepare(self):

        if self.current_user:
            # 如果用户己经登录
            # 方法一：重定向
            #self.redirect('/')
            # 方法二：宣传
            return self.render('auth/resignin.html')

        self.title = _('Sign Up')
        self.template_path = 'auth/signup_step1.html'
        self.data = { 'form': SignUpForm(self) }

    def post(self):

        # 检查 authcode
        if not self.check_authcode():
            return self.render(authcode_failed=True)
        
        form = self.data['form']

        if form.validate():

            email = form.email.data

            # 创建 authkey
            authkey = create_authkey(self.db, type_='01', email=email)

            # 发送验证邮件
            subject = _("Welcome to register %s") % settings.SITE_NAME
            text = self.render_string('auth/signup_email.html',
                                      step2_url=self.step2_url(authkey.key),
                                      settings=settings)
            emsg = sendmail(adr_to=email, subject=subject, text=text)
            if emsg:
                return self.render('auth/signup_step1_failed.html',
                                   emsg=emsg, email=email)
            else:
                return self.render('auth/signup_step1_success.html', email=email)

        self.render()

    def step2_url(self, key):
        return self.host_url + self.reverse_url('auth:signup:step2') + '?key=' + key


class SignUpStep2(RequestHandler):

    '''注册步骤1：创建新用户

    '''

    def prepare(self):

        authkey = None
        key = self.get_argument('key', None)
        if key:
            authkey = self.db.query(AuthKey).get(key)
            now = datetime.datetime.now()
            if not authkey or authkey.expire_date < now:
                authkey = None
        if not authkey:
            d = {'key': key, 'emsg': _('Registration key error.')}
            return self.render('auth/signup_step2_failed.html', **d)

        self.title = _('Create User')
        self.template_path = 'auth/signup_step2.html'

        self.data = { 'authkey': authkey,
                      'form': UserCreateForm(self) }

    def post(self):

        form = self.data['form']
        authkey = self.data['authkey']

        if form.validate():

            # 创建用户，设置为需要激活
            user, emsg = create_user( self.db,
                                      username = form.username.data,
                                      password = form.password.data,
                                      email = authkey.get('email') )

            if not user:
                d = {'key': authkey.key, 'emsg': emsg}
                return self.render('auth/signup_step2_failed.html', **d)

            # 创建用户成功
            user.last_login = datetime.datetime.now()
            self.save_session({'user_id': user.id})

            self.db.delete(authkey)
            self.db.commit()

            return self.redirect( '/' )

        self.render()


class PasswordResetStep1(RequestHandler):

    '''密码重置步骤1：申请

    '''

    def prepare(self):
        self.title = _('Password Reset')
        self.template_path = 'auth/password_reset_step1.html'
        self.data = { 'form': PasswordResetForm(self) }

    def post(self):

        # 检查 authcode
        if not self.check_authcode():
            return self.render(authcode_failed=True)

        form = self.data['form']

        if form.validate():

            email = form.email.data

            # 创建 authkey
            authkey = create_authkey(self.db, type_='02', email=email)

            # 发送验证邮件
            subject = _("Password Reset For %s") % settings.SITE_NAME
            d = { 'step2_url': self.step2_url(authkey.key),
                  'settings': settings,
                  'user': form._user }
            text = self.render_string('auth/password_reset_email.html',**d)
            emsg = sendmail(adr_to=email, subject=subject, text=text)
            if emsg:
                return self.render('auth/password_reset_step1_failed.html',
                                   emsg=emsg, email=email)
            else:
                return self.render('auth/password_reset_step1_success.html', email=email)

        self.render()

    def step2_url(self, key):
        return self.host_url + self.reverse_url('auth:password:reset:step2') + '?key=' + key


class PasswordResetStep2(RequestHandler):

    '''密码重置步骤2：重置密码

    '''

    def prepare(self):

        authkey = None
        key = self.get_argument('key', None)
        if key:
            authkey = self.db.query(AuthKey).get(key)
            now = datetime.datetime.now()
            if not authkey or authkey.expire_date < now:
                authkey = None
        if not authkey:
            d = {'key': key, 'emsg': _('Key error.')}
            return self.render('auth/password_reset_step2_failed.html', **d)

        self.title = _('Password Reset')
        self.template_path = 'auth/password_reset_step2.html'
        self.data = { 'form': PasswordResetStep2Form(self),
                      'authkey': authkey }

    def post(self):

        # 检查 authcode
        if not self.check_authcode():
            return self.render(authcode_failed=True)

        authkey = self.data['authkey']
        form = self.data['form']

        if form.validate():
            user = self.db.query(User).filter_by(
                email = authkey.get('email')).first()
            if user:
                user.password = enc_login_passwd(form.password.data)
                self.db.delete(authkey)
                self.db.commit()
                return self.render('auth/password_reset_step2_success.html',
                                   user = user)

            # 出错：根据 email 没有找到 user 
            d = {'emsg': _('No such email: %s') % authkey.get('email'),
                 'key': key}
            return self.render('auth/password_reset_step2_failed.html', **d)

        # form 验证出错
        self.render()
