# coding: utf-8

from sqlalchemy import and_, desc, asc

from tornado.web import authenticated, HTTPError
from yweb.handler import RequestHandler
from yweb.utils.pagination import pagination
from yweb.utils.translation import ugettext_lazy as _
from yweb.utils.ydatetime import ftime
from yweb.utils.url import urlupdate, urlupdate2

from .models import BlogArticle, BlogPost, BlogComment, \
    BlogTag, Article_Tag

from .forms import PostEditForm


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
            emsg = _('Can not find article %s') % article_id
            return self.send_error(404, emsg=emsg)

        if not article.is_public:
            if cur_uid != article.user_id:
                emsg = _('Article %s is not public.') % article_id
                return self.send_error(404, emsg=emsg)

        cur_page, page_size, start, stop = pagination(self)

        post_total = article.post_count

        posts = self.db.query(BlogPost).filter_by(
            article_id = article_id).order_by(
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
            emsg = _('Can not find article %s') % article_id
            return self.send_error(404, emsg=emsg)

        if not article.is_public:
            if cur_uid != article.user_id:
                emsg = _('Article %s is not public.') % article_id
                return self.send_error(404, emsg=emsg)

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


class PostNew(RequestHandler):

    @authenticated
    def prepare(self):

        self.title = _('Reply Article')
        self.template_path = 'blog/post_new.html'
        self.data = dict(form = PostEditForm(self),
                         ftime = ftime)

    def get(self, article_id):

        article = self.get_article(article_id)
        if not article: return

        self.render()

    def post(self, article_id):

        article = self.get_article(article_id)
        if not article: return

        form = self.data['form']

        if form.validate():

            post = BlogPost(article = article,
                            user    = self.current_user,
                            body    = form.body.data,
                            markup  = 1)

            self.db.add(post)
            self.db.commit()

            url = self.reverse_url('blog:article:view', article.id)
            return self.redirect( url )

        self.render()

    def get_article(self, ID):

        article = self.db.query(BlogArticle).get(ID)
        self.data['article'] = article
        # TODO: 文章的回复权限
        if not article:
            emsg = _('Can not find article %s') % ID
            self.send_error(404, emsg=emsg)

        return article


class TempRedirect1(RequestHandler):

    def get(self, ID):

        url = self.reverse_url('blog:article:view', ID)

        self.redirect( url , status = 301 )


class TempRedirect2(RequestHandler):

    def get(self):

        self.redirect( '/blog' , status = 301 )
