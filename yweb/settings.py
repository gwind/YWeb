# coding: utf-8

import os
import sys


DEBUG = True

SECRET_KEY = 'abc'
SERVER_EMAIL = 'admin@ooctech.com'

# 相关路径
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
STATIC_PATH = os.path.join(PROJECT_ROOT, 'static')

#DB_URI = 'sqlite:///{0}'.format(
#    os.path.join( PROJECT_ROOT, 'data.db' ))
DB_URI = 'postgresql+psycopg2://yweb:yweb@127.0.0.1/yweb'

INSTALLED_APPS = (
    'apps.auth',
    'apps.siteconf',
    'apps.user',
    'apps.home',
)

TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates'),
)

# the custom authkey type
authkey_kind = {
    'signup': 1,
}

ENABLE_STATIC_SERVE = False

# 安全 KEY
SESSION_COOKIE_SECRET = '8fb9affd1d3d0f04553bab437d99c0f2e1f31c94b87485c909cf148a931763bb'

# 用户名字黑名单文件
USERNAME_BLACKLIST_FILE=os.path.join(PROJECT_ROOT, 'data/username_blacklist')
PASSWORD_BLACKLIST_FILE=os.path.join(PROJECT_ROOT, 'data/password_blacklist')

# AuthKey 类型
AUTH_KEY_TYPE = {
    'signup': 1,
    'email.verification': 2,
}

EMAIL = {
    'adr_from': 'ooctechs@163.com',
    'smtp_host': 'smtp.163.com',
    'smtp_port': 25,
    'smtp_username': 'ooctechs@163.com',
    'smtp_password': 'hssmy+2750@D$'
}

SITE_NAME = u"晓风"
AUTHCODE_IMG_FONT = os.path.join(PROJECT_ROOT, 'data/wqy-microhei.ttc')
