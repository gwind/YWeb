# coding: utf-8

from sqlalchemy import and_, desc

from yweb.handler import RequestHandler, administrator
from yweb.conf import settings
from yweb.mail import sendmail
from yweb.utils.translation import ugettext_lazy as _
from yweb.utils.filesize import size as human_size
from yweb.utils.ydatetime import ftime
from yweb.utils.pagination import pagination

from apps.auth.models import User
from apps.auth.utils import enc_login_passwd

from .utils import save_avatar
from .forms import AdminUserBasicEditForm


class Index(RequestHandler):

    @administrator
    def get(self):

        account_total = self.db.query(User).count()

        self.data = {'ftime': ftime,
                     'account_total': account_total}

        self.render('account/admins/index.html')


class AccountAll(RequestHandler):

    @administrator
    def get(self):

        cur_page, page_size, start, stop = pagination(self)
        total = self.db.query(User).count()
        accounts = self.db.query(User).order_by(
            desc(User.id)).slice(start, stop)

        self.data = {'account_list': accounts,
                     'account_total': total,
                     'ftime': ftime}

        self.render('account/admins/list.html')


class UserView(RequestHandler):

    @administrator
    def get(self, ID):

        user = self.db.query(User).get(ID)
        if user:
            self.data = {'user': user, 'ftime': ftime}
            self.render('account/admins/user_view.html')
        else:
            self.data['message'] = _('Can not find user %s') % ID
            self.render('account/consoles/failed.html')


class UserBasicEdit(RequestHandler):

    '''用户基本信息编辑

    '''

    @administrator
    def prepare(self):

        self.title = _('Edit User Basic Information')
        self.template_path = 'account/admins/basic_edit.html'
        from tornado.locale import LOCALE_NAMES
        self.L = []
        for codename in settings.SUPPORTED_LANGUAGES:
            if codename in LOCALE_NAMES:
                self.L.append( (
                    codename,
                    LOCALE_NAMES.get(codename).get('name') ) )

        self.data = {'form': AdminUserBasicEditForm(self)}

    def find_user(self, ID):
        user = self.db.query(User).get(ID)
        if user:
            return user

        self.data['message'] = _('Can not find user %s') % ID
        self.render('account/consoles/failed.html')
        return None

    def get(self, ID):

        user = self.find_user(ID)
        if not user: return

        form = self.data['form']
        form.language.choices = self.L
        form.language.default = user.language
        form.gender.choices = settings.GENDER_CHOICES
        form.gender.default = user.gender
        form.process()

        form.nickname.data = user.nickname
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name

        form.email.data = user.email

        self.render()


    def post(self, ID):

        user = self.find_user(ID)
        if not user: return

        form = self.data['form']
        form.language.choices = self.L
        form.gender.data = int(form.gender.data)
        form.gender.choices = settings.GENDER_CHOICES


        if form.validate():
            user.nickname   = form.nickname.data
            user.first_name = form.first_name.data
            user.last_name  = form.last_name.data
            user.language   = form.language.data
            user.gender     = form.gender.data
            user.email      = form.email.data

            if form.password.data:
                user.password = enc_login_passwd(form.password.data)

            if self.request.files:
                ret, emsg = save_avatar(
                    self.request.files['avatar'], user)
                if not ret:
                    self.data['message'] = emsg
                    return self.render('account/admins/failed.html')

            self.db.commit()

            url = self.reverse_url('admin:account:user:view', user.id)
            return self.redirect(url)

        self.render()

