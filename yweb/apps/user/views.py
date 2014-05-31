# coding: UTF-8

from tornado.web import authenticated

from yweb.handler import RequestHandler
from yweb.utils.translation import ugettext_lazy as _
from yweb.utils.ydatetime import ftime

from apps.auth.models import User


class Index(RequestHandler):

    @authenticated
    def get(self, UID):

        user = self.db.query(User).filter_by(uid=UID).first()
        if not user:
            self.data['message'] = _('Can not find user %s') % UID
            return self.render('user/failed.html')

        d = dict(user=user, ftime=ftime)
        self.render('user/index.html', **d)

