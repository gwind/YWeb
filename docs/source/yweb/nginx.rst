Nginx 部署
=============

Tornado 搭配 Nginx 可以部署目前最高效的 Web Services 。

Ubuntu
--------

安装 nginx
~~~~~~~~~~~

. code-block::

  sudo aptitude install nginx

配置 nginx
~~~~~~~~~~~~~

1. 删除默认 nginx 页面配置 ::

     sudo rm /etc/nginx/sites-enabled/default

2. 编辑 **/etc/nginx/nginx.conf** 文件，根据需要修改 **user www-data;** （第一行）为你的用户角色。

3. 创建新文件 **/etc/nginx/conf.d/local.conf** ， 内容如下 ::

    upstream localsite {
        server 127.0.0.1:8888;
    }

    server {
        listen 80;

        location / {
            proxy_read_timeout 1800;
            proxy_pass_header Server;
            proxy_set_header Host $http_host;
            proxy_redirect off;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Scheme $scheme;
            proxy_pass http://localsite;
        }

        location /static/ {
            root "/data/projects/yweb/yweb/static/";
            rewrite ^/static/(.*)$  /$1 break;
        }

        location /user/static/ {
            root "/data/projects/yweb/yweb/apps/user/static/";
            rewrite ^/user/static/(.*)$ /$1 break;
        }

    }

   其中我配置了两个 static 路径。

   .. note:

      其实 Tornado 中的 static_url 方法不需要用。开发时，不在意文件缓存效率。生产中，又使用 Nginx 等自动实现缓存。




