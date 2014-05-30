# coding: UTF-8

from tornado.web import authenticated
from yweb.handler import RequestHandler, administrator
import yweb.utils.fun


class Index(RequestHandler):

    @administrator
    def get(self):

        hi_img_url = self.static_url(yweb.utils.fun.get_hi_img())
        d = { 'user': self.current_user,
              'hi_img_url': hi_img_url }

        self.render('admin/index.html', **d)

