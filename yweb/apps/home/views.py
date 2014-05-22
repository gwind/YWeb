# coding: utf-8

from yweb.handler import RequestHandler


class Index(RequestHandler):
    def get(self):
        self.render('home/index.html')


class About(RequestHandler):
    def get(self):
        self.render('home/about.html')


class Contact(RequestHandler):
    def get(self):
        self.render('home/contact.html')

