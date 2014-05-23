# coding: utf-8

import os
import sys

DEBUG = True

# 相关路径
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
STATIC_PATH = os.path.join(PROJECT_ROOT, 'static')

# sqlite 数据库
DB_URI = 'sqlite:///{0}'.format(
    os.path.join( PROJECT_ROOT, 'data.db' ))
# PostgreSQL 数据库
#DB_URI = 'postgresql+psycopg2://yweb:yweb@127.0.0.1/yweb'

# 启用的 apps
INSTALLED_APPS = (
    'apps.auth',
    'apps.siteconf',
    'apps.user',
    'apps.home',
)

# 系统模板路径
# 注意：app 自己目录下的 templates 子目录会自动发现
TEMPLATE_DIRS = (
    os.path.join(PROJECT_ROOT, 'templates'),
)

# 启用 static serve ，如果使用 nginx 提供，可以设置为 False
ENABLE_STATIC_SERVE = True

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
AUTHCODE_IMG_FONT = os.path.join(PROJECT_ROOT, 'data/wqy-microhei.ttc')
