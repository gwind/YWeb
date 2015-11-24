# Y Web Framework

**注意** 本项目做为学习 Python / Tornado Web 开发有参考价值.随着后来经验增加,当前我倾向这样的 Web 开发:

1. api 层(RESTFul风格): 使用 golang + sqlx + postgresql 或 python + sqlalchemy
2. UI 层 golang / python / nodejs / ... + (semanti ui + react) 

愿诸君以开放的心态拥抱技术开放的时代吧! :-)

YWeb ( YLinux Web Framework ) -- The First Choice For Your Great Site.

基于 Python, Tornado, SQLAlchemy, Mako, WTForms 提供一整套 Web 开发环境与流程。

![YWeb Home Index](https://raw.githubusercontent.com/gwind/YWeb/master/docs/source/_static/screenshots/yweb-home-index.png)
![YWeb Console Account](https://raw.githubusercontent.com/gwind/YWeb/master/docs/source/_static/screenshots/yweb-console-account.png)
![YWeb Admin Account](https://raw.githubusercontent.com/gwind/YWeb/master/docs/source/_static/screenshots/yweb-admin-account.png)


## 组件

### Python

开发语言


### Tornado

轻量级、灵活性、高效率的 Python Web 开发基础平台。


### SQLAlchemy

Python 下优秀的 ORM 、数据库操作绑定库，可以很方便地与其他组件合作。


### Mako

基于 Python 语言的模板解释器。号称速度最优。


### WTForms

灵活的表单处理组件。


## 目标

用 Tornado 这种松耦合的工具开发 Web ，容易不停地造轮子。而选择太多常意味着烦恼也很多。

本项目的目标：

- 总结“最好”的 Python + Tornado 开发项目的流程/方法/架构/结构
- 分享我们造的“轮子”（我们称之为app），希望今后能做到通过用这些 app 搭积木，就可以“开发”一个 Web 平台。


# 如何在本地部署 YWeb 开发

太简单了！

## 准备工作

### Debian/Ubuntu/Linux Mint 系统

安装软件包：

    sudo apt-get install git python-dateutil python-imaging

### CentOS/RHEL/Fedora 系统

安装软件包：

    yum install git python-backports

## 部署 YWeb

    git clone https://github.com/gwind/YWeb.git
    cd YWeb/yweb/
    wget http://dl.ylinux.org/yweb/tools/YWeb_dev_third_lib-20140531.tar.bz2
    tar xf YWeb_dev_third_lib-20140531.tar.bz2
    cp default_settings.py settings.py
    python manage.py syncdb
    python manage.py adduser admin 123456 XXX@163.com
    python site.py

访问 http://127.0.0.1:8888 即可 ！


# 联系我们

- 社区： http://ylinux.org
- 邮件： info@ylinux.org
- QQ群： Linux与云计算 232629450

![扫描二维码](http://ylinux.org/static/img/join-qq-qun232629450.png)

