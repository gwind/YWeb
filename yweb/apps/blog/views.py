# coding: utf-8

from sqlalchemy import and_, desc

from tornado.web import authenticated
from yweb.handler import RequestHandler
from yweb.utils.pagination import pagination
from yweb.utils.translation import ugettext_lazy as _

from .models import BlogArticle, BlogPost, BlogComment, \
    BlogTag


def page_404(handler, msg=None):
    '''查找的对象不存在
    '''
    handler.set_status(404)
    handler.render("blog/404.html", msg=msg)


class Index(RequestHandler):

    '''Blog 首页
    '''

    def get(self):

        cur_page, page_size, start, stop = pagination(self)

        articles = self.db.query(BlogArticle).filter_by(
            is_public = True )

        articles = articles.order_by( desc(BlogArticle.id) )

        total = articles.count()

        articles = articles.slice(start, stop)

        d = dict(article_list = articles,
                 article_total = total)

        self.render('blog/index.html', **d)


class ArticleView(RequestHandler):

    '''查看 Blog 文章
    '''

    def get(self, ID):

        cur_uid = self.current_user.id if self.current_user else 0

        article = self.db.query(BlogArticle).get( ID )

        if not article:
            return page_404(self, _('Can not find article %s') % ID)

        if not article.is_public:
            if cur_uid != article.user_id:
                return page_404(_('Article %s is not public.') % ID)

        posts = article.posts

        # 增加查看次数
        article.view_count += 1
        self.db.commit()

        self.data = dict(article = article,
                         posts = article.posts)

        self.render('blog/article_view.html')


class TempRedirect1(RequestHandler):

    def get(self, ID):

        url = self.reverse_url('blog:article:view', ID)

        self.redirect( url , status = 301 )


class TempRedirect2(RequestHandler):

    def get(self):

        self.redirect( '/blog' , status = 301 )
