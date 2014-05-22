# coding: utf-8
#
# 用户操作：创建/删除/查询
#
# 依赖 apps.auth

from yweb.conf import settings
from yweb.orm import get_db_session

from apps.auth.models import User, create_user

def adduser(username, password, email):

    db = get_db_session()
    user, emsg = create_user( db,
                        username = username,
                        password = password,
                        email = email )
    if user:
        print 'Create user "{0}" success.'.format(username)
    else:
        print 'Create user failed: {0}'.format(emsg)

    db.remove()

