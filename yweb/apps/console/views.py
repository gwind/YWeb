# coding: UTF-8

from tornado.web import authenticated
from yweb.handler import RequestHandler


class Index(RequestHandler):

    @authenticated
    def get(self):

        d = {'user': self.current_user,}

        self.render('console/index.html', **d)

