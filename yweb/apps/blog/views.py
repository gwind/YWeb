# coding: utf-8

from sqlalchemy import and_, desc, asc

from tornado.web import authenticated
from yweb.handler import RequestHandler
from yweb.utils.pagination import pagination
from yweb.utils.translation import ugettext_lazy as _
from yweb.utils.ydatetime import ftime
from yweb.utils.url import urlupdate, urlupdate2

from .models import BlogArticle, BlogPost, BlogComment, \
    BlogTag, Article_Tag

from .utils import page_404


def get_post_order(handler):

    ascending = handler.get_argument('asc', None)
    _by = handler.get_argument('order_by', 'id')
    if _by not in ['id', 'updated', 'created', 'vote_up', 'vote_down']:
        _by = 'id'

    order_by = asc(_by) if ascending else desc(_by)

    return order_by


class Index(RequestHandler):

    '''Blog 首页
    '''

    def get(self):

        def update_ylinux_db():
            from apps.auth.models import get_available_uid, User
            for user in self.db.query(User).all():
                if not user.uid:
                    user.uid = get_available_uid(self.db)
                if user.nickname:
                    L = user.nickname.split('@')
                    if len(L) > 1:
                        user.nickname = L[0]
                else:
                    user.nickname = user.username
    
            self.db.commit()
    
            from yweb.utils import fopen
            with fopen('/tmp/imind__post.sql', 'r') as fp_:
                for line in fp_:
                    article_id, post_id = line.split()
                    article = self.db.query(BlogArticle).get(article_id)
                    post = self.db.query(BlogPost).get(post_id)
                    if article and post:
                        if post.article_id != article_id:
                            post.article_id = article_id
    
            self.db.commit()
    
            with fopen('/tmp/imind__utag.sql', 'r') as fp_:
                for line in fp_:
                    article_id, tag_id = line.split()
                    article = self.db.query(BlogArticle).get(article_id)
                    tag = self.db.query(BlogTag).get(tag_id)
                    if article and tag:
                        a = Article_Tag()
                        a.article_id = article_id
                        a.tag = tag
                        a.user = self.current_user
                        print 'article.tags = ', article.tags
                        if a not in article.tags:
                            article.tags.append(a)
    
            self.db.commit()

        # 更新 ylinux 数据库
#        update_ylinux_db()
        a = self.db.query(BlogArticle).get(407)
        print 'a.tags = ', a.tags
        print 'dir(a.tags) = ', dir(a.tags)

    
        cur_page, page_size, start, stop = pagination(self)

        articles = self.db.query(BlogArticle).filter_by(
            is_public = True )

        articles = articles.order_by( desc(BlogArticle.id) )

        total = articles.count()

        articles = articles.slice(start, stop)

        d = dict(article_list = articles,
                 article_total = total,
                 ftime = ftime)

        self.render('blog/index.html', **d)


class ArticleView(RequestHandler):

    '''查看 Blog 文章
    '''

    def get(self, article_id):

        cur_uid = self.current_user.id if self.current_user else 0

        article = self.db.query(BlogArticle).get( article_id )

        if not article:
            return page_404(self, _('Can not find article %s') % article_id)

        if not article.is_public:
            if cur_uid != article.user_id:
                return page_404(_('Article %s is not public.') % article_id)

        cur_page, page_size, start, stop = pagination(self)

        post_q = self.db.query(BlogPost).filter_by(
            article_id = article_id)
        post_total = post_q.count()

        posts = post_q.order_by(
            get_post_order(self)).slice(start, stop)

        # 增加查看次数
        article.view_count += 1
        self.db.commit()

        self.data = dict(article = article,
                         post_total = post_total,
                         posts = posts,
                         ftime = ftime,
                         urlupdate = urlupdate,
                         urlupdate2 = urlupdate2)

        self.render('blog/article_view.html')


class ArticlePostAll(RequestHandler):

    '''查看 Blog 文章的所有回复
    '''

    def get(self, article_id):

        cur_uid = self.current_user.id if self.current_user else 0

        article = self.db.query(BlogArticle).get( article_id )

        if not article:
            return page_404(self, _('Can not find article %s') % article_id)

        if not article.is_public:
            if cur_uid != article.user_id:
                return page_404(_('Article %s is not public.') % article_id)

        cur_page, page_size, start, stop = pagination(self)

        post_q = self.db.query(BlogPost).filter_by(
            article_id = article_id)
        post_total = post_q.count()

        posts = post_q.order_by(
            get_post_order(self)).slice(start, stop)

        self.data = dict(article = article,
                         post_list = posts,
                         post_total = post_total,
                         ftime = ftime,
                         urlupdate = urlupdate,
                         urlupdate2 = urlupdate2)

        self.render('blog/article_post_all.html')


class TempRedirect1(RequestHandler):

    def get(self, ID):

        url = self.reverse_url('blog:article:view', ID)

        self.redirect( url , status = 301 )


class TempRedirect2(RequestHandler):

    def get(self):

        self.redirect( '/blog' , status = 301 )
