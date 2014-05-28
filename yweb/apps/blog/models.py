# coding: utf-8

import datetime

from yweb.orm import ORMBase

from sqlalchemy import Column, Integer, String, Unicode, \
    Sequence, DateTime, Table, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship, backref

from apps.post.models import Post
from apps.tag.models import UTag

from yweb.utils.markup import generate_html

imind__utag_table = Table(
    'imind__utag', ORMBase.metadata,
    Column('imind_id', Integer, ForeignKey('imind.id')),
    Column('utag_id', Integer, ForeignKey('utag.id')),
    Column('user_id', Integer, ForeignKey('auth_user.id')),
    Column('created', DateTime, default=datetime.datetime.now)
)

imind__post_table = Table(
    'imind__post', ORMBase.metadata,
    Column('imind_id', Integer, ForeignKey('imind.id')),
    Column('post_id', Integer, ForeignKey('post.id')),
    Column('user_id', Integer, ForeignKey('auth_user.id')),
    Column('created', DateTime, default=datetime.datetime.now)
)


class Imind(ORMBase):

    ''' 我思 - 自由地记录自己的想法、笔记等

    1. 短的内容，只用 body。
    2. 长的内容，用 title, abstract, body

    '''

    __tablename__ = 'imind'

    id = Column( Integer, Sequence('imind_id_seq'), primary_key=True )

    user_id = Column( Integer, ForeignKey('auth_user.id') )
    user = relationship("User")

    title       = Column( String(128), nullable=False )
    abstract    = Column( String(1024) )
    body        = Column( Text )
    body_markup = Column( Integer, default=1 )

    status = Column( Integer, default=0 )

    # 是否公开
    is_public = Column( Boolean, default=False )

    # 是否为短文章
    is_short = Column( Boolean, default=True )

    vote_up     = Column( Integer, default=0 )
    vote_down   = Column( Integer, default=0 )

    visit_count = Column( Integer, default=0 )
    post_count  = Column( Integer, default=0 )

    posts = relationship( 'Post', secondary=imind__post_table,
                          backref='iminds',
                          order_by = "Post.vote_up" )

    utags = relationship( 'UTag', secondary=imind__utag_table,
                           order_by = "UTag.id" )

    created = Column( DateTime, default=datetime.datetime.now )
    updated = Column( DateTime, default=datetime.datetime.now )


    def __init__(self, user, body, body_markup=1, title=None, abstract=None):

        self.user_id = user.id
        self.body = body
        self.body_markup = body_markup

        if title:
            self.title = title
            self.is_short = False

        if abstract:
            self.abstract = abstract

    @property
    def body_html(self):
        return generate_html( self.body, self.body_markup )

    def visited(self):
        if self.visit_count:
            self.visit_count += 1
        else:
            self.visit_count = 1


class ImindVote(ORMBase):

    ''' 我思投票

    1. 针对本文章的投票
    2. 每个用户只能投票一次
    3. 自己不能投自己

    '''

    __tablename__ = 'imind_vote'

    id = Column( Integer, Sequence('imind_vote_id_seq'), primary_key=True )

    oid = Column( Integer ) # 投票对象 ID
    uid = Column( Integer ) # 投票用户 ID

    v = Column( Integer, nullable=False )

    created = Column( DateTime, default=datetime.datetime.now )
    updated = Column( DateTime, default=datetime.datetime.now )


    def __init__(self, oid, uid, v):

        self.oid = oid
        self.uid = uid
        self.v = v

