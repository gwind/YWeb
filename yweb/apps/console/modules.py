# coding: UTF-8

import os
import logging

from yweb.handler import UIModule
from yweb.conf import settings


class NavBarUI(UIModule):

    '''加载 Console 的导航栏

    '''

    def render(self):
        console_urls = self.handler.settings.get('app_console_urls')
        d = {'console_urls': console_urls}
        return self.render_string('console/modules/navbar.html', **d)
