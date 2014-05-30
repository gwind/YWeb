# coding: utf-8

from yweb.handler import RequestHandler


class SetLocale(RequestHandler):

    def get(self, locale):

        # 检查 locale 有效性
        if locale not in ['zh_CN', 'en_US']:
            locale = 'en_US'

        # 设置 cookie
        self.set_cookie("user_locale", locale)

        url = self.get_argument('next', '/')
        self.redirect(url)
