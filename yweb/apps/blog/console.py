# coding: utf-8

import datetime

from sqlalchemy import and_, desc

from tornado.web import authenticated
from yweb.handler import RequestHandler

from apps.imind.models import Imind
from apps.post.models import Post

from yweb.utils.pagination import pagination
from yweb.utils.url import urlupdate

from apps.imind.forms import ImindEditForm


class Index(RequestHandler):

    @authenticated
    def get(self):

        iminds = self.db.query( Imind ).filter_by(
            user_id = self.current_user.id )

        now = datetime.datetime.now()

        # this week
        dt_week = now - datetime.timedelta(days=now.isoweekday())
        this_week = self.db.query( Imind ).filter(
            and_( Imind.updated > dt_week )).count()

        dt_month = datetime.datetime( now.year, now.month, 1 )
        this_month = self.db.query( Imind ).filter(
            and_( Imind.updated > dt_month )).count()

        dt_year = datetime.datetime( now.year, 1, 1 )
        this_year = self.db.query( Imind ).filter(
            and_( Imind.updated > dt_year )).count()

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

            c = self.db.query(Imind).filter(
                and_( Imind.updated > start_dt,
                      Imind.updated < end_dt ) ).count()

            js_dt = u'%s/%s' % (start_dt.year, start_dt.month)

            months_count.insert(0, (js_dt, c))
            end_dt = start_dt

        d = { 'imind_count': iminds.count(),
              'this_week': this_week,
              'this_month': this_month,
              'this_year': this_year,
              'months_count': months_count }

        self.render('imind/console/index.html', **d)



class ImindList(RequestHandler):

    @authenticated
    def get(self):

        p = self.get_argument_int('p', 1)
        s = self.get_argument_int('s', 12)

        i_start = (p - 1) * s
        i_end = i_start + s

        iminds = self.db.query( Imind ).filter_by(
            user_id = self.current_user.id )

        # 选择本周、本月、本年？
        iminds, time = self.do_time_select( iminds )

        count = iminds.count()

        # 排序
        iminds, sortby = self.do_sort( iminds )

        iminds = iminds.slice(i_start, i_end)

        d = { 'iminds': iminds,
              'imind_total': count,
              'pagination': pagination(self.request.uri, count, s, p),
              'sortby': sortby,
              'time': time,
              'urlupdate': lambda k, v: urlupdate(self.request.uri, k, v),
        }

        self.render('imind/console/imind_list.html', **d)


    def do_time_select(self, iminds):

        select = self.get_argument('time', 'all')

        if select:

            now = datetime.datetime.now()

            if select == 'this_week':
                dt_week = now - datetime.timedelta(days=now.isoweekday())
                iminds = iminds.filter(
                    and_( Imind.updated > dt_week ))

            elif select == 'this_month':
                dt_month = datetime.datetime( now.year, now.month, 1 )
                iminds = iminds.filter(
                    and_( Imind.updated > dt_month ))

            elif select == 'this_year':
                dt_year = datetime.datetime( now.year, 1, 1 )
                iminds = iminds.filter(
                    and_( Imind.updated > dt_year ))

            else:
                select = 'all'

        return iminds, select


    def do_sort(self, iminds):

        sortby = self.get_argument('sortby', 'id')

        if sortby not in ['vote_up', 'vote_down', 'visit_count', 'updated']:
            sortby = 'id'

        iminds = iminds.order_by( desc(sortby) )

        return iminds, sortby



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


class ImindNew(RequestHandler):

    @authenticated
    def prepare(self):
        self.markup = self.get_argument_int('markup', 0)

    def get(self):

        form = ImindEditForm( self )
        d = { 'form': form }
        self.render('imind/console/imind_new.html', **d)

    def post(self):

        form = ImindEditForm( self )

        if form.validate():

            I = Imind( user        = self.current_user,
                       body        = form.body.data,
                       body_markup = 1,
                       title       = form.title.data,
                       abstract    = form.abstract.data )

            I.is_public = form.ispublic.data

            self.db.add(I)
            self.db.commit()

            url = self.reverse_url('imind:view', I.id)
            return self.redirect( url )

        d = { 'form': form }
        self.render('imind/console/imind_new.html', **d)
