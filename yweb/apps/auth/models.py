# coding: utf-8

import os
import random
import json
import datetime
import time
import logging
from hashlib import sha256, sha1

from sqlalchemy import Column, Integer, String, \
    Sequence, DateTime, Table, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship, backref

import yweb.utils.ydatetime
from yweb.orm import ORMBase
from yweb.utils.random_ import random_ascii
from yweb.conf import settings

from .utils import enc_login_passwd, check_login_passwd, \
    encode_data, decode_data

from . import settings as auth_settings


user_groups = Table('user_groups', ORMBase.metadata,
    Column('id', Integer, Sequence('user_groups_id_seq'), primary_key=True),
    Column('user_id', Integer, ForeignKey('auth_user.id')),
    Column('group_id', Integer, ForeignKey('auth_group.id'))
)


group_permissions = Table('group_permissions', ORMBase.metadata,
    Column('id', Integer, Sequence('group_permissions_id_seq'), primary_key=True),
    Column('group_id', Integer, ForeignKey('auth_group.id')),
    Column('permission_id', Integer, ForeignKey('auth_permission.id')),
)


class Group(ORMBase):

    __tablename__ = 'auth_group'

    id = Column(Integer, Sequence('auth_group_id_seq'), primary_key=True)
    name = Column( String(30) )
    description = Column( Text() )


    def __init__(self, name, description = None):
        self.name = name
        if description:
            self.description = description


    def __unicode__(self):
        return _("Group <%s>") % self.name


class User(ORMBase):

    '''用户数据模型

    定义一个 uid 字段，类似QQ号码，用户可以登录

    用户的ID给用户有几点不好：
    
    1. 网站内部信息过多暴露给他人
    2. 根据《影响力》，一开始ID的低，容易让跟随着却步

    '''

    __tablename__ = 'auth_user'

    id = Column(Integer, Sequence('auth_user_id_seq'), primary_key=True)
    uid      = Column( Integer, unique = True )
    username = Column( String(30), unique = True )
    password = Column( String(128) )
    email    = Column( String(64), unique = True )

    first_name = Column( String(30) )
    last_name  = Column( String(30) )
    nickname   = Column( String(30) )
    gender     = Column( Boolean )

    is_active    = Column( Boolean, default = True )
    is_staff     = Column( Boolean, default = False )
    is_superuser = Column( Boolean, default = False )
    is_locked    = Column( Boolean, default = False )

    language    = Column( String(12) , default = 'zh_CN' )

    last_active = Column( DateTime() )
    last_login  = Column( DateTime() )
    date_joined = Column( DateTime(), default=datetime.datetime.now )

    groups = relationship( 'Group', secondary=user_groups, backref='users' )

    def __init__(self, uid, username, password, email = None, language=None):
        self.uid = uid
        self.username = username
        self.nickname = username
        self.password = enc_login_passwd( password )
        self.email = email
        if language:
            self.language = language # TODO: test language valid

    def __unicode__(self):
        return 'User <%s>' % self.username

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = u'%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """

        return check_login_passwd(raw_password, self.password)

    @property
    def storage_path(self):

        '''获取用户个人存储路径

        '''

        if hasattr(auth_settings, 'STATIC_PATH'):
            static_path = auth_settings.STATIC_PATH
        else:
            static_path = 'static'

        # 用户个人存储路径
        storage_path = os.path.join(
            settings.PROJECT_ROOT, 'apps/auth', static_path,
            'data', str(self.uid))

        if not os.path.exists( storage_path ):
            try:
                os.makedirs( storage_path )
            except Exception, emsg:
                logging.error('Create storage path (%s) failed: %s' % (
                    storage_path, emsg))
                return None

        return storage_path

    @property
    def avatar_path(self):
        avatar_path = os.path.join(self.storage_path, 'avatar')
        if not os.path.exists( avatar_path ):
            try:
                os.makedirs( avatar_path )
            except Exception, emsg:
                logging.error('Create avatar path (%s) failed: %s' % (
                    avatar, emsg))
                return None

        return avatar_path

    @property
    def avatar_orig_path(self):
        return os.path.join( self.avatar_path,
                             '{0}-orig.png'.format(self.uid) )

    @property
    def avatar_lg_path(self):
        return os.path.join( self.avatar_path,
                             '{0}-lg.png'.format(self.uid) )
    @property
    def avatar_xs_path(self):
        return os.path.join( self.avatar_path,
                             '{0}-xs.png'.format(self.uid) )

    @property
    def avatar_sm_path(self):
        return os.path.join( self.avatar_path,
                             '{0}-sm.png'.format(self.uid) )

    @property
    def avatar_md_path(self):
        return os.path.join( self.avatar_path,
                             '{0}-md.png'.format(self.uid) )

    @property
    def avatar_url_prefix(self):
        prefix = os.path.join('/auth/static', 'data',
                              str(self.uid), 'avatar')
        return prefix

    @property
    def avatar_default_url(self):
        return '/static/img/icon-user-default.png'

    @property
    def avatar_lg_url(self):
        if os.path.exists(self.avatar_lg_path):
            url = os.path.join( self.avatar_url_prefix,
                                '{0}-lg.png'.format(self.uid) )
        else:
            url = self.avatar_default_url

        return url


class Permission(ORMBase):

    __tablename__ = 'auth_permission'

    id       = Column( Integer, primary_key=True )
    name     = Column( String(80) )
    codename = Column( String(100), unique = True )

    groups = relationship( "Group", secondary=group_permissions,
                           backref="permissions" )


    def __init__(self, name, codename):
        self.name = name
        self.codename = codename

    def __unicode__(self):
        return _("Permission <%s>") % self.name


class Session(ORMBase):

    __tablename__ = 'auth_session'

    id = Column(Integer, Sequence('auth_session_id_seq'), primary_key=True)
    skey  = Column( String(40) )
    data = Column( Text() )
    expire_date  = Column( DateTime() )

    def __init__(self, skey, data):
        self.skey = skey
        self.data = encode_data(data, settings.SESSION_COOKIE_SECRET)
        age = settings.SESSION_COOKIE_AGE
        self.expire_date = yweb.utils.ydatetime.after_days(age)

    def __unicode__(self):
        return 'Session <%s>' % self.session_key

    def get_uid(self):
        data = decode_data(self.data, settings.SESSION_COOKIE_SECRET)
        uid = data.get('user_id', 0)
        return uid


OpenID_TYPE = (
    (1, 'QQ'),
    )

class OpenID(ORMBase):

    __tablename__ = 'auth_openid'

    id = Column( Integer, Sequence('auth_openid_id_seq'), primary_key=True )

    user_id  = Column( Integer, ForeignKey('auth_user.id') )
    user     = relationship("User",backref=backref( 'openid', order_by=id) )

    oid      = Column( String(256) )
    oid_type = Column( Integer )

    created  = Column( DateTime, default=datetime.datetime.now )
    updated  = Column( DateTime, default=datetime.datetime.now )

    # Other data
    data = Column( Text() )


    def __init__(self, oid, oid_type):
        self.oid = oid
        self.oid_type = oid_type


    def __unicode__(self):

        return 'OpenID <%s>' % self.id


class AuthKey(ORMBase):

    '''验证操作的 Key

    '''

    __tablename__ = 'auth_key'
    key = Column( String(16), unique = True, primary_key=True )
    data = Column( String(1024) )
    expire_date = Column( DateTime() )

    def __init__(self, key, expire_seconds=None, **kwargs):
        self.key = key
        if not expire_seconds:
            expire_seconds = 3600 * 2
        now = datetime.datetime.now()
        self.expire_date = now + datetime.timedelta(seconds=expire_seconds)

        self.data = json.dumps(kwargs)

    def get(self, attr):
        _data = json.loads(self.data)
        if attr in _data:
            return _data.get(attr)
        else:
            return None

    def set(self, attr, value):
        _data = json.loads(self.data)
        _data[attr] = value
        self.data = json.dumps(_data)

    def __unicode__(self):

        return 'AuthKey <%s>' % self.id


class AuthCode(ORMBase):

    '''验证码表

    在需要验证码的地方：
    1. 给定一个字符串表示 key
    2. 给出一个些 key 对应的 code 的图片

    用户上传操作数据时，需要上传：
    1. key
    2. code 的字符串形式（人工输入）

    后台：
    1. 比对 code 与 key 是否匹配
    2. 检查有效期
    
    '''

    __tablename__ = 'auth_code'
    key = Column( String(16), unique = True, primary_key=True )
    code = Column( String(32) )
    expire_date = Column( DateTime() )

    def __init__(self, key, code):
        self.key = key
        self.code = code
        expire_seconds = 60 * 2 # 默认2分钟有效期
        now = datetime.datetime.now()
        self.expire_date = now + datetime.timedelta(
            seconds=expire_seconds)

    def __unicode__(self):

        return 'AuthCode <%s>' % self.id

    @classmethod
    def new(cls, db):

        # TODO:
        # 清理过期的 code
        for ac in db.query(cls).filter(
                cls.expire_date <= datetime.datetime.now()):
            db.delete(ac)

        while True:
            key = random_ascii(16)
            if not db.query(cls).get(key):
                break

        code = random_ascii(4, drops='oO01lLiI')
        authcode = cls(key, code)
        db.add( authcode )
        db.commit()

        return authcode


class UserID(ORMBase):

    '''存放系统 UID 使用情况

    创建用户时从此表里选取一个 UID 值，并删除该记录。
    '''

    __tablename__ = 'auth_uid'

    id = Column(Integer, Sequence('auth_uid_seq'), primary_key=True)
    uid = Column( Integer )

    def __init__(self, uid):
        self.uid = uid


def get_available_uid(db):

    '''获取一个可用的 UID

    '''

    retry = 100

    while retry > 0:

        if db.query(UserID).count() <= 0:
            logging.debug('Gen new uids ...')
            # UserID 表中己经没有可用的 uid ，创建它
            from .settings import DEFAULT_UID_START
            from apps.siteconf.models import SiteConfig
            start = SiteConfig.get(db, 'apps_auth.uid_start', DEFAULT_UID_START, int)
            end = start + 10000
            uids = range(start, end)
            random.shuffle(uids)
            for uid in uids:
                db.add( UserID(uid) )
            db.commit()
            SiteConfig.set(db, 'apps_auth.uid_start', end)
            logging.debug('Gen new uids done: {0} -> {1}'.format(start, end))
      
        userid = db.query(UserID).order_by(UserID.id).first()
        if not userid:
            continue  # 不知道为什么，为了保险

        uid = userid.uid

        # 不管什么情况，该 UID 记录都应被删除
        db.delete(userid)
        db.commit()

        # 还是为了保险，测试该 UID 是否被占用
        user = db.query(User).filter_by(uid=uid).first()
        if user:
            logging.error('Something was wrong, get used uid {0}, retry.'.format(uid))
            retry -= 1
        else:
            logging.debug('Get new uid {0}'.format(uid))
            return uid

    # 不应该到这里
    logging.error('Important !!! UID generating was failed.')
    return 0


def create_user(db, username, password, email):

    # check username
    user = db.query(User).filter_by(username=username).first()
    if user:
        return None, _('Username already exists')

    # check email
    user = db.query(User).filter_by(email=email).first()
    if user:
        return None, _('E-mail address already exists')

    # TODO: check password

    # generate uid
    uid = get_available_uid(db)

    try:
        user = User( uid = uid,
                     username = username,
                     password = password,
                     email = email )

        db.add( user )
        db.commit()

    except Exception, emsg:
        return None, emsg

    # Good !
    return user, ''


def guess_user(db, ID):

    '''测试指定标识符的用户是否存在

    参数 ID 可能是“用户名|邮件|UID”

    '''

    ID = ID.strip()

    # 如果“像”邮件地址，就测试 email
    if '@' in ID:
        user = db.query(User).filter_by(email=ID).first()
        if user:
            return user

    # 如果是整数，就测试 uid
    if ID.isdigit():
        user = db.query(User).filter_by(uid=int(ID)).first()
        if user:
            return user

    # 最后测试用户名匹配
    user = db.query(User).filter_by(username=ID).first()
    if user:
        return user

    return None


def create_authkey(db, type_='00', **kwargs):


    while True:
        key = type_ + random_ascii(14)
        if not db.query(AuthKey).get(key):
            break

    authkey = AuthKey(key, **kwargs)
    db.add( authkey )
    db.commit()

    return authkey
