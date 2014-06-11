安装 YWeb
===============


CentOS 6
-------------

系统基本包 ::

  yum install nginx postgresql-server python-psycopg2 python-imaging python-dateutil

数据库
~~~~~~~~~

初始化 postgresql ::

  /etc/init.d/postgresql initdb

启动 postgresql ::

/etc/init.d/postgresql start

创建用户 ::

  # su - postgres
  -bash-4.1$ psql 
  psql (8.4.20)
  Type "help" for help.

  postgres=# CREATE USER yweb WITH PASSWORD 'yweb';
  CREATE ROLE
  postgres=# CREATE DATABASE yweb;
  CREATE DATABASE
  postgres=# GRANT ALL PRIVILEGES ON DATABASE yweb to yweb;
  GRANT
  postgres=# 
  postgres=# \q
  -bash-4.1$ exit
  logout

修改 /var/lib/pgsql/data/pg_hba.conf 中的配置 ::

  # IPv4 local connections:
  host    all         all         127.0.0.1/32          ident

为 ::

  # IPv4 local connections:
  host    all         all         127.0.0.1/32          password

重启 postgresql ::

  # /etc/init.d/postgresql restart

登录用户验证 ::

  # psql -h 127.0.0.1 -d yweb -U yweb -W
  Password for user yweb: 
  psql (8.4.20)
  Type "help" for help.

  yweb=>

正确验证!


Web Site
~~~~~~~~~~~

初始化数据库 ::

  # python manage.py syncdb

添加用户 ::

  # python manage.py adduser admin 123456 admin@ooctech.com

运行 site ::

  # python site.py --port=8081
  [I 140606 20:03:46 site:103] torando web server is running

正确！

