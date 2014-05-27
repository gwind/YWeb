#! /usr/bin/env python
# coding: UTF-8 

# 加载 Python 内置库
import os
import sys
import logging
import signal

# 加载开发路径
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'lib'))

def main():

    if len(sys.argv) < 2:
        print 'Usage: {0} opt'.format(sys.argv[0])
        print '''
    syncdb
    dropdb
    adduser
'''
        sys.exit(1)

    # 用户配置文件模块路径
    os.environ.setdefault("YWEB_SETTINGS_MODULE", "settings")

    import tornado.options
    tornado.options.options.logging = "debug"
    tornado.options.parse_command_line()

    opt = sys.argv[1]

    if opt == 'syncdb':
        import yweb.management.db
        yweb.management.db.syncdb()

    elif opt == 'dropdb':
        import yweb.management.db
        yweb.management.db.dropdb()

    elif opt == 'adduser':
        if len(sys.argv) != 5:
            print 'Usage: {0} adduser username password email'.format(sys.argv[0])
            sys.exit(1)
        else:
            username = sys.argv[2]
            password = sys.argv[3]
            email = sys.argv[4]
            import yweb.management.user
            yweb.management.user.adduser(username, password, email)

    else:
        print 'unknown opt: {0}'.format(opt)

if __name__ == '__main__':
    main()
