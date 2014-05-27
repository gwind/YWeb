# coding: utf-8

import os
import logging

from yweb.handler import UIModule
from yweb.conf import settings

from .models import AuthCode


class AuthCodeUI(UIModule):

    '''加载 AuthCode 模块

    '''

    def render(self, authcode_failed):

        d = {'authcode': AuthCode.new(self.handler.db),
             'authcode_failed': authcode_failed}
        return self.render_string('auth/modules/authcode.html',**d)
