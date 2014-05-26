# coding: utf-8

# Import python module
import os
import sys
import datetime

# Import third module
from mako.exceptions import RichTraceback
import tornado.web

# Import yweb module
from yweb.conf import settings

# Import my module
from apps.auth.models import User, Session


class RequestHandler(tornado.web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        super(RequestHandler, self).__init__(
            application, request, **kwargs )
        self.template_path = None
        self.title = None
        self.data = {}

    def render_string(self, template_path, **kwargs):
        '''渲染模板，返回字符串
        '''

        if not template_path:
            # 模板未指定，出错
            return u'模板名未指定！'
            
        args = dict(
            handler=self,
            request=self.request,
            current_user=self.current_user,
            locale=self.locale,
            _=self.locale.translate,
            static_url=self.static_url,
            xsrf_form_html=self.xsrf_form_html,
            reverse_url=self.reverse_url,
        )

        args.update(self.data)
        args.update(kwargs)

        # 如果标题未设置，设置一个默认值
        if self.title:
            args['title'] = self.title
        else:
            args['title'] = settings.DEFAULT_HTML_TITLE

        try:
            html = self.application.template_lookup.get_template(
                template_path).render(**args)
        except:
            html = self.application.template_lookup.get_template(
                'mako_failed.html').render(
                    traceback = RichTraceback())

        return html

    def render(self, template_path=None, **kwargs):
        '''渲染模板，直接返回给客户端
        '''

        if not template_path:
            template_path = self.template_path

        html = self.render_string(template_path, **kwargs)

        self.finish(html)

    def get_current_user(self):

        skey = self.get_secure_cookie('session_key')
        session = self.db.query(Session).filter_by(skey=skey).first()
        if not session:
            return None

        now = datetime.datetime.now()

        # Does session expired ?
        if session.expire_date < now:
            self.db.remove( session )
            self.db.commit()
            return None

        uid = session.get_uid()
        if not uid:
            return None

        user = self.db.query(User).get(uid)

        if user:
            if user.is_locked:
                return None
            else:
                user.last_active = now
                #self.db.commit()
                return user
        else:
            return None

    def get_user_locale(self):

        user_locale = self.get_cookie("user_locale")

        if user_locale:
            return tornado.locale.get(user_locale)
        else:
            # Use the Accept-Language header
            return None

    @property
    def db(self):
        return self.application.db_session()

    def on_finish(self):
        self.application.db_session.remove()

    def get(self):
        '''提供默认的 HTTP GET 请求

        Python不太爱隐藏细节，但是程序员很懒。
        '''
        self.render()

    def static_url(self, path, app=None):
        '''静态文件地址

        Tornado 的 static_url 扩展。但不计算 version，可由 nginx 提供。

        支持指定 app，获取其 static 文件 url
        '''

        if app:
            url = None
            data = self.settings.get('app_static_urls')
            if data:
                url = data.get(app)

            # 默认 url
            if not url:
                url = '/{0}/static/'.format(app)

            url += path
        else:
            url = self.settings.get('static_url_prefix', '/static/') + path

        return url


class DefaultIndexHandler(RequestHandler):
    '''默认的视图

    如果用户还没有指定自己的首页视图，就会调用这个视图
    '''

    def get(self):
#        self.write("<h1>I'm runing!</h1>")
        self.render('default_index.html')


class NotFoundHandler(RequestHandler):
    '''404错误视图

    如果用户访问的 URL 不存在，就会调用这个视图
    '''

    def prepare(self):
        self.set_status(404)
        self.render("/404.html")


class ApiRequestHandler(RequestHandler):


    def write_fail(self, message='', data=None):

        d = { 'status': 'fail', 'message': message, 'data': data }

        self.write( d )


    def write_success(self, message='', data=None):

        d = { 'status': 'success', 'message': message, 'data': data }

        self.write( d )