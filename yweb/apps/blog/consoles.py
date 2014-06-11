# coding: utf-8

import datetime

from sqlalchemy import and_, desc
from tornado.web import authenticated

from yweb.handler import RequestHandler
from yweb.utils.pagination import pagination
from yweb.utils.url import urlupdate
from yweb.utils.translation import ugettext_lazy as _

from .models import BlogArticle, BlogPost, BlogComment, \
    BlogTag
from .forms import ArticleEditForm


class Index(RequestHandler):

    '''Blog 控制台首页
    '''

    @authenticated
    def get(self):

        article_q = self.db.query(BlogArticle).filter_by(
            user_id = self.current_user.id )

        now = datetime.datetime.now()

        # this week
        dt_week = now - datetime.timedelta(days=now.isoweekday())
        this_week = article_q.filter(
            and_( BlogArticle.updated > dt_week )).count()

        dt_month = datetime.datetime( now.year, now.month, 1 )
        this_month = article_q.filter(
            and_( BlogArticle.updated > dt_month )).count()

        dt_year = datetime.datetime( now.year, 1, 1 )
        this_year = article_q.filter(
            and_( BlogArticle.updated > dt_year )).count()

        def get_months( current, how_many ):

            cur_year = current.year
            cur_month = current.month

            months = []

            while how_many > 0:

                months.append( datetime.datetime(cur_year, cur_month, 1) )

                if cur_month < 2:
                    cur_month += 12
                    cur_year -= 1

                cur_month -= 1
                how_many -= 1

            return months

        months_count = []
        end_dt = now
        for start_dt in get_months(now, 6):

            c = article_q.filter(
                and_( BlogArticle.updated > start_dt,
                      BlogArticle.updated < end_dt ) ).count()

            js_dt = u'%s/%s' % (start_dt.year, start_dt.month)

            months_count.insert(0, (js_dt, c))
            end_dt = start_dt

        d = dict(article_total = article_q.count(),
                 this_week = this_week,
                 this_month = this_month,
                 this_year = this_year,
                 months_count = months_count)

        self.render('blog/consoles/index.html', **d)


class ArticleAll(RequestHandler):

    @authenticated
    def get(self):

        cur_page, page_size, start, stop = pagination(self)

        article_q = self.db.query(BlogArticle).filter_by(
            user_id = self.current_user.id )

        # 选择本周、本月、本年？
        article_q, time = self.do_time_select( article_q )

        count = article_q.count()

        # 排序
        article_q, sortby = self.do_sort( article_q )

        article_q = article_q.slice(start, stop)

        d = { 'article_list': article_q,
              'article_total': count,
              'sortby': sortby,
              'time': time,
              'urlupdate': lambda k, v: urlupdate(self.request.uri, k, v),
        }

        self.render('blog/consoles/article_list.html', **d)


    def do_time_select(self, article_q):

        select = self.get_argument('time', 'all')

        if select:

            now = datetime.datetime.now()

            if select == 'this_week':
                dt_week = now - datetime.timedelta(days=now.isoweekday())
                article_q = article_q.filter(
                    and_(BlogArticle.updated > dt_week))

            elif select == 'this_month':
                dt_month = datetime.datetime( now.year, now.month, 1 )
                article_q = article_q.filter(
                    and_(BlogArticle.updated > dt_month))

            elif select == 'this_year':
                dt_year = datetime.datetime( now.year, 1, 1 )
                article_q = article_q.filter(
                    and_(BlogArticle.updated > dt_year))

            else:
                select = 'all'

        return article_q, select


    def do_sort(self, iminds):

        sortby = self.get_argument('sortby', 'id')

        if sortby not in ['vote_up', 'vote_down', 'visit_count', 'updated']:
            sortby = 'id'

        iminds = iminds.order_by( desc(sortby) )

        return iminds, sortby


class ArticleNew(RequestHandler):

    @authenticated
    def prepare(self):

        self.title = _('Create an new article')
        self.template_path = 'blog/consoles/basic_edit.html'

        markup = self.get_argument('markup', 1)
        try:
            markup = int(markup)
        except:
            markup = 1

        self.data = dict(markup = markup,
                         css_class = 'article-edit',
                         form = ArticleEditForm(self))

    def post(self):

        form = self.data['form']

        if form.validate():

            article = BlogArticle(
                user = self.current_user,
                title = form.title.data,
                body = form.body.data,
#                markup = form.markup.data,
                abstract = form.abstract.data,
                is_public = form.is_public.data)

            self.db.add(article)
            self.db.commit()

            url = self.reverse_url('blog:article:view', article.id)
            return self.redirect( url )

        self.render()


class ArticleEdit(RequestHandler):

    @authenticated
    def prepare(self):

        self.title = _('Edit article')
        self.template_path = 'blog/consoles/basic_edit.html'

        markup = self.get_argument('markup', 1)
        try:
            markup = int(markup)
        except:
            markup = 1

        self.data = dict(markup = markup,
                         css_class = 'article-edit',
                         form = ArticleEditForm(self))

    def get_article(self, ID):

        article = self.db.query(BlogArticle).get(ID)
        if not article:
            emsg = _('Can not find article %s') % ID
            self.send_error(404, emsg=emsg)

        return article

    def get(self, ID):

        article = self.get_article(ID)
        if not article: return

        form = self.data['form']
        form.title.data = article.title
        form.body.data = article.body
        form.abstract.data = article.abstract
        form.is_public.data = article.is_public

        self.render(article=article)

    def post(self, ID):

        article = self.get_article(ID)
        if not article: return

        form = self.data['form']

        if form.validate():

            article.title = form.title.data
            article.body = form.body.data
            article.abstract = form.abstract.data
            article.is_public = form.is_public.data
            article.updated = datetime.datetime.now()

            self.db.commit()

            url = self.reverse_url('blog:article:view', article.id)
            return self.redirect( url )

        self.render(article=article)


class ImindEdit(RequestHandler):

    @authenticated
    def prepare(self):
        self.markup = self.get_argument_int('markup', 0)

    def get(self, ID):

        I = self.get_imind( ID )
        if not I: return

        if not self.markup:
            self.markup = I.body_markup

        form = ImindEditForm( self )
        form.title.data = I.title
        form.abstract.data = I.abstract
        form.body.data = I.body
        form.ispublic.data = I.is_public

        d = { 'form': form, 'I': I }
        self.render('imind/console/imind_edit.html', **d)


    def post(self, ID):
        I = self.get_imind( ID )
        if not I: return

        form = ImindEditForm( self )

        if form.validate():

            I.title     = form.title.data
            I.abstract  = form.abstract.data
            I.body      = form.body.data
            I.is_public = form.ispublic.data
            I.updated   = datetime.datetime.now()

            self.db.commit()

            url = self.reverse_url('imind:view', I.id)
            return self.redirect( url )

        d = { 'form': form, 'I': I }
        self.render('imind/console/imind_edit.html', **d)


    def get_imind(self, ID):

        I = self.db.query( Imind ).get( ID )

        if I:
            if self.current_user.id != I.user_id:
                self.write( _('No permission!') )
                I = None

        else:
            self.page_not_found( _('Can not find imind %s') % ID )

        return I


