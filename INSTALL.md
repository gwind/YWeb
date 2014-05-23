# 部署 YWeb 开发

太简单了！

## 最基本

    git clone https://github.com/jianlee/YWeb.git
    cd YWeb/yweb/
    cp default_settings.py settings.py
    python manage.py syncdb
    python manage.py adduser admin 123456 XXX@163.com
    python site.py

访问 http://127.0.0.1:8888 即可 ！

## 手动安装第三方库

### 方法一

安装发行版仓库中的软件包

### 方法二

在 http://pan.baidu.com/s/1c01TAFY 下载 YWeb_local_lib.tar.bz2 软件包，
解压后是一个 lib 目录，移动到 YWeb/yweb 目录即可。

    cd YWeb/yweb/
    tar xf YWeb_local_lib.tar.bz2

