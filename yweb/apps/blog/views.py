# coding: utf-8

from sqlalchemy import and_, desc

from tornado.web import authenticated
from yweb.handler import RequestHandler

from apps.imind.models import Imind
from apps.post.models import Post

from yweb.utils.pagination import pagination


class Index(RequestHandler):

    def get(self):

        p = self.get_argument_int('p', 1)
        s = self.get_argument_int('s', 12)

        i_start = (p - 1) * s
        i_end = i_start + s

        iminds = self.db.query(Imind).filter_by(
            is_public = True )

        count = iminds.count()

        # sort
        sortby = self.get_argument('sortby', 'updated')
        if sortby not in ['vote_up', 'visit_count', 'updated']:
            sortby = 'updated'

        iminds = iminds.order_by( desc(sortby) )

        iminds = iminds.slice(i_start, i_end)

        d = { 'iminds': iminds,
              'imind_total': count,
              'pagination': pagination(self.request.uri, count, s, p),
              'sortby': sortby,
        }

        self.render('imind/index.html', **d)



class ImindView(RequestHandler):

    def get(self, ID):

        cur_uid = self.current_user.id if self.current_user else 0

        I = self.db.query(Imind).get( ID )

        if not I:
            return self.page_not_found( _('Can not find imind %s') % ID )

        if not I.is_public:
            if cur_uid != I.user_id:
                return self.page_not_found( _('Mind %s is not public.') % ID )

        # get the hotest posts (12)
        posts = self.db.query(Post).filter(Post.iminds.any( id=I.id )).order_by(
            desc('vote_up'))

        post_total = posts.count()

        posts = posts.limit(12).all()

        # add visit_count
        I.visited()
        self.db.commit()

        self.render('imind/view.html', imind=I, posts=posts, post_total=post_total)


class ImindNew(RequestHandler):

    def get(self):

        d = {}
        self.render('imind/new.html', **d)





class TempRedirect1(RequestHandler):

    def get(self, ID):

        url = self.reverse_url('imind:view', ID)

        self.redirect( url , status = 301 )


class TempRedirect2(RequestHandler):

    def get(self):

        self.redirect( '/imind' , status = 301 )
