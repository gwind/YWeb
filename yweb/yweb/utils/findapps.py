# coding: utf-8

import os
import logging

import tornado.web

import yweb.utils.cmd
from yweb.conf import settings
from yweb.utils.importlib import import_module
from yweb.utils.module_loading import module_has_submodule
from yweb.utils.translation.generate import update_locales


def get_app_abspath(app_name):
    '''获取 app 的决对路径
    '''
    app_module = import_module(app_name)
    return os.path.dirname(os.path.realpath( app_module.__file__ ))


def get_app_submodule(app_name, module_name):
    '''获取 app settings 模块
    '''
    app_module = import_module(app_name)
    try:
        submodule = import_module('{0}.{1}'.format(app_name, module_name))
    except ImportError:
        if not module_has_submodule(app_module, module_name):
            return None

        else:
            raise

    return submodule


def get_app_static_path( app_name ):
    '''获取 app 的 static 目录全路径名
    '''
    
    app_path = get_app_abspath( app_name )
    static_path = os.path.join(app_path, 'static')

    if os.path.isdir( static_path ):
        return static_path
    else:
        return None


def get_site_handlers():
    '''发现所有的己安装 APP 提供的 handler

    '''

    handlers = []

    for app_name in settings.INSTALLED_APPS:
        app_urls = get_app_submodule( app_name, 'urls' )
        if app_urls:
            if hasattr(app_urls, 'handlers'):
                handlers.extend( app_urls.handlers )
            if hasattr(app_urls, 'admin_handlers'):
                handlers.extend( app_urls.admin_handlers )
            if hasattr(app_urls, 'api_handlers'):
                handlers.extend( app_urls.api_handlers )

        # 是否启动 static 服务。生产环境中，通常由 nginx 等提供该服务
        if settings.ENABLE_STATIC_SERVE:
            # 为该 app 增加默认的 static URL，对应目录为其子目录 static/
            static_path = get_app_static_path( app_name )
            if static_path:
                app_settings = get_app_submodule( app_name, 'settings' )
                if hasattr(app_settings, 'STATIC_PREFIX'):
                    static_prefix = app_settings.STATIC_PREFIX
                else:
                    static_prefix = app_name.split('.')[-1]

                handlers.append(
                    tornado.web.url( r"/{0}/static/(.*)".format( static_prefix ),
                                     tornado.web.StaticFileHandler,
                                     {"path": static_path} )
                )

    from yweb.handler import NotFoundHandler, DefaultIndexHandler

    # 如果默认的主页不存在，就添加一个
    home_exists = False
    for spec in handlers:
        match = spec.regex.match('/')
        if match:
            home_exists = True
            break
    if not home_exists:
        handlers.extend([
            ('/', DefaultIndexHandler)
        ])

    # 添加其他 handler
    handlers.extend([
        (r'/404', NotFoundHandler),
        (r'/(.*)', NotFoundHandler)
    ])

    return handlers


def get_site_template_dirs():
    '''发现所有的己安装 APP 的模板目录

    '''

    dirs = list(settings.TEMPLATE_DIRS)

    for app_name in settings.INSTALLED_APPS:
        app = App(app_name)
        # 默认是 app settings 所在目录下的 templates 子目录
        tdir = 'templates'

        app_settings = get_app_submodule( app_name, 'settings' )
        if app_settings:
            if hasattr(app_settings, 'TEMPLATE_DIR'):
                tdir = app_settings.TEMPLATE_DIR

        dirs.append( os.path.join(app.abspath, tdir) )

    return dirs


class App(object):

    def __init__(self, fullname):

        self.fullname = fullname
        self.basename = self.get_basename()
        self.abspath = get_app_abspath(self.fullname)

        self.__app_settings = {
            'APP_NAME': self.basename,
            'STATIC_PATH': 'static',
            'TEMPLATE_PATH': 'templates',
            'LOCALE_PATH': 'locale',
        }

        self.init_attrs()

    def get_basename(self):
        return self.fullname.split('.')[-1]

    def init_attrs(self):

        app_settings = get_app_submodule(self.fullname, 'settings')
        if app_settings:
            for attr in dir(app_settings):
                if attr.startswith('_'):
                    continue
                self.__app_settings[attr] = getattr(app_settings, attr)

        for attr in self.__app_settings:
            if attr in ['STATIC_PATH', 'TEMPLATE_PATH', 'LOCALE_PATH']:
                v = self.__app_settings[attr]
                self.__app_settings[attr] = v.strip('/')

    def __getattr__(self, attr):
        return self.__app_settings.get(attr, '')

    @property
    def static_url(self):
        return '/{0}/{1}/'.format(self.basename, self.STATIC_PATH)


def get_static_urls():
    '''发现所有的己安装 APP 的 static URL

    '''

    static_urls = {}

    for app_name in settings.INSTALLED_APPS:
        app = App(app_name)
        static_urls[app.basename] = app.static_url

    return static_urls


def get_ui_modules():
    '''发现所有的己安装 APP 的 ui modules

    '''

    ui_modules = {}

    for app_name in settings.INSTALLED_APPS:
        app_urls = get_app_submodule( app_name, 'urls' )
        if app_urls:
            if hasattr(app_urls, 'ui_modules'):
                ui_modules.update( app_urls.ui_modules )

    return ui_modules


def update_apps_locale():

    backdir = os.getcwd()

    for app_name in settings.INSTALLED_APPS:
        app = App(app_name)

        root_path = app.abspath

        logging.debug('GO=> {0}'.format(root_path))
        os.chdir(root_path)

        # 生成新 yweb.po 文件
        files = yweb.utils.cmd.find_files('.', ['py', 'html'])
        cmd = 'xgettext --from-code=UTF-8 -L python -k=_ ' + \
              ' -o yweb.po ' + ' '.join(files)
        yweb.utils.cmd.run_cmd(cmd)

        # 测试文件是否正确生成
        if not os.path.exists('yweb.po'):
            logging.debug('pass {0}'.format(root_path))
            continue

        # 更新 locale 目录中所有语言的 po, mo 文件
        update_locales('yweb.po', root_path)

        # 删除 yweb.po
        os.unlink('yweb.po')


