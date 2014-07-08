# coding: utf-8

import os
import sys

from yweb.utils.translation import ugettext_lazy as _

DEBUG = True

# 相关路径
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
STATIC_PATH = os.path.join(PROJECT_ROOT, 'static')
I18N_PATH = os.path.join(PROJECT_ROOT, 'locale')

# sqlite 数据库
DB = {
    'engine': 'sqlite',
    'host': '',
    'path': 'data.db',
    'database': '',
    'username': '',
    'password': '',
}

# 启用的 apps
INSTALLED_APPS = (
    'apps.common',
    'apps.auth',
    'apps.siteconf',
    'apps.console',
    'apps.admin',
    'apps.account',
    'apps.user',
    'apps.i18n',
    'apps.home',
    'apps.blog',
)

# 系统模板路径
# 注意：app 自己目录下的 templates 子目录会自动发现
TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates'),
)

# 启用 static serve ，如果使用 nginx 提供，可以设置为 False
ENABLE_STATIC_SERVE = True

# 设置时区
TIME_ZONE = 'Asia/Shanghai'

# 安全 KEY
# 重要：修改为只有你自己知道的字符串
SECRET_KEY = 'Not set now!'
SESSION_COOKIE_SECRET = 'Not set now!'

# 用户名字黑名单文件
USERNAME_BLACKLIST_FILE=os.path.join(PROJECT_ROOT, 'data/username_blacklist')
PASSWORD_BLACKLIST_FILE=os.path.join(PROJECT_ROOT, 'data/password_blacklist')

# 示例：使用 163 邮箱发送邮件
EMAIL = {
    'adr_from': 'XXX@163.com',
    'smtp_host': 'smtp.163.com',
    'smtp_port': 25,
    'smtp_username': 'XXX@163.com',
    'smtp_password': '填写您自己的邮箱密码'
}

SITE_NAME = u"YWebDevSite"
DEFAULT_HTML_TITLE = _('YWeb -- For Best!')
AUTHCODE_IMG_FONT = os.path.join(PROJECT_ROOT, 'data/wqy-microhei.ttc')

SITE_TRANSLATION_FILES = (
    '*.py',
    'templates',
)

# 站点的 locale 目录 （除去 yweb 和 apps 的 locale）
LOCALE_PATHS = (
    os.path.join(PROJECT_ROOT, 'locale'),
)
