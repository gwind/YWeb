# coding: UTF-8

import os
import logging

from yweb.handler import UIModule
from yweb.conf import settings


class NavBarUI(UIModule):

    '''加载 Admin 的导航栏

    '''

    def render(self):
        admin_urls = self.handler.settings.get('app_admin_urls')
        d = {'admin_urls': admin_urls}
        return self.render_string('admin/modules/navbar.html', **d)
