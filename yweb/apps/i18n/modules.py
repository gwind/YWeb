# coding: utf-8

import os
import logging

from yweb.handler import UIModule
from yweb.conf import settings


class SetLang(UIModule):

    '''加载 SetLang 模块

    '''

    def render(self):
        return self.render_string('i18n/modules/setlang.html')
