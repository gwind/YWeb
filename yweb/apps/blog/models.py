# coding: UTF-8

import datetime

from yweb.orm import ORMBase

from sqlalchemy import Column, Integer, String, Unicode, \
    Sequence, DateTime, Table, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship, backref

from yweb.utils.markup import generate_html


article__tag_table = Table(
    'blog_article__blog_tag', ORMBase.metadata,
    Column('article_id', Integer, ForeignKey('blog_article.id')),
    Column('tag_id', Integer, ForeignKey('blog_tag.id')),
    Column('user_id', Integer, ForeignKey('auth_user.id')),
    Column('created', DateTime, default=datetime.datetime.now)
)

class BlogArticle(ORMBase):

    ''' Blog 文章

    '''

    __tablename__ = 'blog_article'

    id = Column( Integer, Sequence('blog_article_id_seq'), primary_key=True )

    user_id = Column( Integer, ForeignKey('auth_user.id') )
    user = relationship("User")

    title    = Column( String(128), nullable=False )
    abstract = Column( String(1024) )
    body     = Column( Text )
    markup   = Column( Integer, default=1 )

    status = Column( Integer, default=0 )

    # 是否公开
    is_public = Column( Boolean, default=False )

    vote_up    = Column( Integer, default=0 )
    vote_down  = Column( Integer, default=0 )

    view_count = Column( Integer, default=0 )
    post_count = Column( Integer, default=0 )

    tags = relationship( 'BlogTag', secondary=article__tag_table,
                           order_by="BlogTag.id" )

    created = Column( DateTime, default=datetime.datetime.now )
    updated = Column( DateTime, default=datetime.datetime.now )


    def __init__(self, user, title, body, markup=1, abstract=None, is_public=True):

        self.user_id = user.id
        self.title = title
        self.body = body
        self.markup = markup
        if abstract:
            self.abstract = abstract
        else:
            # TODO: 生成 article 的摘要
            self.abstract = title

        self.is_public = is_public

    @property
    def body_html(self):
        return generate_html( self.body, self.markup )


class BlogPost(ORMBase):

    ''' Blog 回复

    '''

    __tablename__ = 'blog_post'

    id = Column( Integer, Sequence('blog_post_id_seq'), primary_key=True )

    article_id = Column( Integer, ForeignKey('blog_article.id') )
    article = relationship("BlogArticle", backref="posts")

    user_id = Column( Integer, ForeignKey('auth_user.id') )
    user = relationship("User")

    body = Column( Text )
    markup = Column( Integer, default=1 )

    status = Column( Integer, default=0 )

    vote_up     = Column( Integer, default=0 )
    vote_down   = Column( Integer, default=0 )

    comment_count = Column( Integer, default=0 )

    created = Column( DateTime, default=datetime.datetime.now )
    updated = Column( DateTime, default=datetime.datetime.now )

    def __init__(self, article, user, body, markup=1):

        self.article_id = article.id

        # 增加 article 的 post 统计
        if article.post_count:
            article.post_count += 1
        else:
            article.post_count = 1

        self.user_id = user.id
        self.body = body
        self.markup = markup

    @property
    def body_html(self):
        return generate_html( self.body, self.markup )


class BlogComment(ORMBase):

    ''' Blog 注释, 对 BlogPost 的回复

    1. 某回复的注释
    2. 适当降低 comment 的“价值鼓励”，引导用户少做 comment

    '''

    __tablename__ = 'blog_comment'

    id = Column( Integer, Sequence('blog_comment_id_seq'), primary_key=True )

    post_id = Column( Integer, ForeignKey('blog_post.id') )
    post = relationship("BlogPost", backref="comments")

    parent_id = Column( Integer, ForeignKey('blog_comment.id') )
    parent = relationship("BlogComment", backref="children", remote_side=[id])

    user_id = Column( Integer, ForeignKey('auth_user.id') )
    user = relationship("User")

    body = Column( Text )
    markup = Column( Integer, default=1 )

    status = Column( Integer, default=0 )

    created = Column( DateTime, default=datetime.datetime.now )
    updated = Column( DateTime, default=datetime.datetime.now )

    def __init__(self, post, user, body, markup=1, parent=None):

        self.post_id = post.id

        # 增加 post 的 comment 计数
        if post.comment_count:
            post.comment_count += 1
        else:
            post.comment_count = 1

        self.user_id = user.id
        self.body = body
        self.markup = markup

        if parent:
            self.parent_id = parent.id

    @property
    def body_html(self):
        return generate_html( self.body, self.markup )


class ArticleVote(ORMBase):

    ''' 对 Blog 文章投票

    1. 针对本文章的投票
    2. 每个用户只能投票一次
    3. 自己不能投自己

    '''

    __tablename__ = 'blog_article_vote'

    id = Column( Integer, Sequence('blog_article_vote_id_seq'), primary_key=True )

    article_id = Column( Integer ) # 投票对象 ID
    user_id = Column( Integer ) # 投票用户 ID

    # 投票值 [-1, 1]
    vote = Column( Integer, nullable=False )

    created = Column( DateTime, default=datetime.datetime.now )
    updated = Column( DateTime, default=datetime.datetime.now )

    def __init__(self, article, user, vote):

        self.article_id = article.id
        self.user_id = user.id
        self.vote = vote

        # 更新 article 的 vote_up, vote_down
        if vote > 0:
            article.vote_up += vote
        else:
            article.vote_down += vote


class PostVote(ORMBase):

    ''' 回复的投票

    1. 针对本回复的投票
    2. 每个用户只能投票一次
    3. 自己不能投自己

    '''

    __tablename__ = 'blog_post_vote'

    id = Column( Integer, Sequence('blog_post_vote_id_seq'), primary_key=True )

    post_id = Column( Integer ) # 投票对象 ID
    user_id = Column( Integer ) # 投票用户 ID

    # 投票值： 1, -1
    vote = Column( Integer, nullable=False )

    created = Column( DateTime, default=datetime.datetime.now )
    updated = Column( DateTime, default=datetime.datetime.now )

    def __init__(self, post, user, vote):

        self.post_id = post.id
        self.user_id = user.id
        self.vote = vote

        # 更新 post 的 vote_up, vote_down
        if vote > 0:
            post.vote_up += vote
        else:
            post.vote_down += vote


class BlogTag(ORMBase):

    ''' Blog 标签

    可以参考下：http://sitetag.us/

    我认为网站标签自动生成有可取的地方。

    '''

    __tablename__ = 'blog_tag'

    id = Column( Integer, Sequence('blog_tag_id_seq'), primary_key=True )

    name   = Column( String(64), nullable=False, unique=True )
    brief  = Column( String(1024) )
    detail = Column( Text )
    markup = Column( Integer, default=1 )

    # 索引值
    index = Column( Integer, default = 0 )

    created = Column( DateTime, default=datetime.datetime.now )
    updated = Column( DateTime, default=datetime.datetime.now )


    def __init__(self, name, brief='', detail='', markup=1):

        self.name   = name
        self.brief  = brief
        self.detail = detail
        self.markup = markup


class TagDiff(ORMBase):

    ''' Blog 标签编辑历史

    允许其他用户修改 tag 的介绍

    '''

    __tablename__ = 'blog_tag_diff'

    id = Column( Integer, Sequence('blog_tag_diff_id_seq'), primary_key=True )

    user_id = Column( Integer, ForeignKey('auth_user.id') )
    user = relationship("User")

    # brief, detail 与上一次版本的差异
    diff_brief  = Column( Text )
    diff_detail = Column( Text )

    created = Column( DateTime, default=datetime.datetime.now )

    def __init__(self, user, diff_brief, diff_detail):

        self.user_id = user.id
        self.diff_brief = diff_brief
        self.diff_detail = diff_detail
