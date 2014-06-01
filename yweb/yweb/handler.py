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
from apps.auth.models import User, Session, AuthCode
from yweb.utils.translation import trans_real
from yweb.utils.translation import ugettext_lazy
_ = ugettext_lazy


class RequestHandler(tornado.web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        super(RequestHandler, self).__init__(
            application, request, **kwargs )
        self.template_path = None
        self.title = None
        self.data = {}

        # TODO: hack django 的 lazy translation 机制
        trans_real._default = trans_real.translation(self.locale_code)

    def render_string(self, template_path, **kwargs):
        '''渲染模板，返回字符串
        '''
        if not template_path:
            # 模板未指定，出错
            return _('No template!')
            
        args = dict(
            handler=self,
            request=self.request,
            current_user=self.current_user,
#            locale=self.locale,
#            _=self.locale.translate,
            _=ugettext_lazy,
            static_url=self.static_url,
            xsrf_form_html=self.xsrf_form_html,
            reverse_url=self.reverse_url,
            module=self.load_module,
            s=lambda x: u"\"{0}\"".format(x),
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
    def locale_code(self):
        '''获取 language code

        为了使用 Django 的翻译机制
        '''

        user_locale = self.get_cookie("user_locale")
        if user_locale:
            return user_locale
        else:
            return 'zh_CN'

    @property
    def db(self):
        return self.application.db_session()

    def on_finish(self):
        self.application.db_session.remove()

    def get(self):
        '''提供默认的 HTTP GET 请求

        Python不太爱隐藏细节，但是程序员很懒。
        '''
        if self.template_path:
            self.render()
        else:
            # 可能 Handler 没有提供 get 方法
            raise tornado.web.HTTPError(405)

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
                url = '/static/{0}/'.format(app)

            url += path
        else:
            url = self.settings.get('static_url_prefix', '/static/') + path

        return url

    def load_module(self, module_name, *args, **kwargs):
        '''加载 ui module
        '''

        ui_modules = self.settings['y_ui_modules']

        if module_name not in ui_modules.keys():
            return '<p class="text-danger">' + \
            'Can not find module "{0}"</p>'.format(module_name)

        # TODO：保存该 module 为激活的，在 render 时可以像 tornado
        # 里一样，加载 html, css, js 内容

        Module = ui_modules.get(module_name)

        return Module(self).render(*args, **kwargs)

    def check_authcode(self):
        '''检查 authcode 安全
        '''

        authcode_key = self.get_argument('authcode_key', None)
        authcode_code = self.get_argument('authcode_code', None)
        if not (authcode_key and authcode_code):
            return False

        ac = self.db.query(AuthCode).get(authcode_key)
        if ac and ac.code.lower() == authcode_code.lower():
            self.db.delete(ac)
            self.db.commit()
            return True

        return False


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


# 参考 tornado/web.py:UIModule
class UIModule(object):
    """A re-usable, modular UI unit on a page.

    UI modules often execute additional queries, and they can include
    additional CSS and JavaScript that will be included in the output
    page, which is automatically inserted on page render.
    """
    def __init__(self, handler):
        self.handler = handler
        self.request = handler.request
        self.ui = handler.ui
        self.locale = handler.locale

    @property
    def current_user(self):
        return self.handler.current_user

    def render(self, *args, **kwargs):
        """Overridden in subclasses to return this module's output."""
        raise NotImplementedError()

    def embedded_javascript(self):
        """Returns a JavaScript string that will be embedded in the page."""
        return None

    def javascript_files(self):
        """Returns a list of JavaScript files required by this module."""
        return None

    def embedded_css(self):
        """Returns a CSS string that will be embedded in the page."""
        return None

    def css_files(self):
        """Returns a list of CSS files required by this module."""
        return None

    def html_head(self):
        """Returns a CSS string that will be put in the <head/> element"""
        return None

    def html_body(self):
        """Returns an HTML string that will be put in the <body/> element"""
        return None

    def render_string(self, path, **kwargs):
        """Renders a template and returns it as a string."""
        return self.handler.render_string(path, **kwargs)

import functools
import urlparse
from urllib import urlencode

def administrator(method):
    """需要管理权限的装饰器
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.current_user:
            if self.current_user.is_superuser:
                return method(self, *args, **kwargs)

            # 用户不是管理员
            self.write('No Permissions!')
            return

        # 用户没有登录,且请求为 GET, HEAD
        if self.request.method in ("GET", "HEAD"):
            url = self.get_login_url()
            if "?" not in url:
                if urlparse.urlsplit(url).scheme:
                    # if login url is absolute, make next absolute too
                    next_url = self.request.full_url()
                else:
                    next_url = self.request.uri
                url += "?" + urlencode(dict(next=next_url))
            self.redirect(url)
            return

        # 出错
        raise HTTPError(403)

    return wrapper
