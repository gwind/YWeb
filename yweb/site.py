#! /usr/bin/env python
# coding: utf8

# 加载 Python 内置库
import os
import sys
import logging
import signal

# 加载开发路径
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'lib'))

# 加载第三方库
import tornado
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.netutil
import tornado.locale

from yweb.conf import settings
from yweb.orm import get_db_session
from yweb.template import get_template_lookup
from yweb.utils.findapps import get_site_handlers, get_static_urls
import yweb.utils


class Application(tornado.web.Application):

    def __init__(self):

        # TODO: TEST db connect
        self.db_session = get_db_session()
        self.template_lookup = get_template_lookup()

        site_handlers = get_site_handlers()
        logging.debug('Find Handlers:\n{0}'.format(
            yweb.utils.yprint(site_handlers) ))

        tornado_settings = {
            'cookie_secret': 'MTyNwNDc3OC40MjaexynagfeA3NjgKCg==',
            'xsrf_cookies': True,
            'login_url': '/user/signin',
            'gzip': True,
            'debug': True,
            'static_path': settings.STATIC_PATH,
            'app_static_urls': get_static_urls(),
        }

        tornado.web.Application.__init__(
            self, site_handlers, **tornado_settings )


def exit_handler(_signal, frame):

    if _signal == signal.SIGINT:
        print " ... You Pressed CTL+C, exit ... "

    elif _signal == signal.SIGHUP:
        print " ... get SIGHUP, exit ... "

    if _signal == signal.SIGTERM:
        print " ... get SIGTERM, exit ... "

    sys.exit(1)


def main():

    # 监听信号
    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGHUP, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)

    # 用户配置文件模块路径
    os.environ.setdefault("YWEB_SETTINGS_MODULE", "settings")

    # 设置 options
    tornado.options.define("port", default=8888, help="listen on the give port", type=int)
    tornado.options.options.logging = "debug"
    tornado.options.parse_command_line()

    # 设置本地化语言
#    tornado.locale.load_gettext_translations(settings.I18N_PATH, "site")
#    tornado.locale.set_default_locale('zh_CN')

    logging.info("starting torando web server")

    logging.info('DB_URI = {0}'.format( settings.DB_URI ))

    # 启动 Tornado
    app = Application()
    server = tornado.httpserver.HTTPServer(app, xheaders=True)
    sockets = tornado.netutil.bind_sockets(tornado.options.options.port)
    server.add_sockets(sockets)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":

    try:
        main()
    finally:
        pass
