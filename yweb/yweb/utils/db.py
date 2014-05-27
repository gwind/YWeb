# coding: utf-8

import os
from yweb.conf import settings


def get_db_uri():

    '''获取数据库访问接口

    '''

    DB = settings.DB
    engine = DB.get('engine')    

    if engine == 'sqlite':
        path = DB.get('path')
        if not path:
            path = 'data.db'

        if not os.path.isabs(path):
            path = os.path.join(
                settings.PROJECT_ROOT, path)

        DB['path'] = path
        DB_URI = '{engine}:///{path}'

    elif engine == 'postgresql+psycopg2':
        DB_URI = '{engine}://{username}:{password}' + \
                 '@{host}/{database}'

    else:
        raise YwebDBError

    return DB_URI.format(**settings.DB)
