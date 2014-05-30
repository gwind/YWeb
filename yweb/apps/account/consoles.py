# coding: utf-8

import datetime

from sqlalchemy import and_, desc
from tornado.web import authenticated

from yweb.handler import RequestHandler
from yweb.conf import settings
from yweb.mail import sendmail
from yweb.utils.translation import ugettext_lazy as _
from yweb.utils.filesize import size as human_size
from yweb.utils.ydatetime import ftime

from apps.auth.utils import enc_login_passwd
from apps.auth.models import User, AuthKey, create_authkey

from .forms import AvatarChangeForm, PasswordChangeForm, \
    EmailChangeStep1Form, BasicInfoEditForm
from .utils import save_avatar


class Index(RequestHandler):

    @authenticated
    def get(self):

        self.data = {'ftime': ftime}

        self.render('account/consoles/index.html')


class AvatarChange(RequestHandler):

    @authenticated
    def prepare(self):

        self.title = _('Change My Avatar')
        self.template_path = 'account/consoles/basic_edit.html'
        self.data = { 'form': AvatarChangeForm(self) }

    def post(self):
        form = self.data['form']

        if self.request.files and form.validate():
            ret, emsg = save_avatar(self.request.files['avatar'],
                                    self.current_user)
            if ret:
                self.data['message'] = _('Change Avatar Success !')
                return self.render('account/consoles/success.html')
            else:
                self.data['message'] = emsg
                return self.render('account/consoles/failed.html')

        self.render()



class PasswordChange(RequestHandler):

    @authenticated
    def prepare(self):
        self.title = _('Change My Password')
        self.template_path = 'account/consoles/basic_edit.html'
        self.data = {'form': PasswordChangeForm(self),
                     'authcode_needed': True}

    def post(self):

        # 检查 authcode
        if not self.check_authcode():
            return self.render(authcode_failed=True)

        form = self.data['form']

        if form.validate():
            self.current_user.password = enc_login_passwd(form.password.data)
            self.db.commit()
            self.data['message'] = _('Change Password Success !')
            return self.render('account/consoles/success.html')

        self.render()


class EmailChangeStep1(RequestHandler):

    '''修改我的邮箱地址：步骤一，验证邮箱

    '''

    @authenticated
    def prepare(self):
        self.title = _('Change My E-mail')
        self.template_path = 'account/consoles/basic_edit.html'
        self.data = {'form': EmailChangeStep1Form(self),
                     'authcode_needed': True}

    def post(self):

        # 检查 authcode
        if not self.check_authcode():
            return self.render(authcode_failed=True)

        form = self.data['form']

        if form.validate():
            email = form.email.data

            # 创建 authkey
            authkey = create_authkey(self.db, type_='03', email=email, user_id=self.current_user.id)

            # 发送验证邮件
            subject = _("[%s] Change User E-mail") % settings.SITE_NAME
            text = self.render_string(
                'account/consoles/email_change_sendmail.html',
                step2_url=self.step2_url(authkey.key),
                settings=settings)
            emsg = sendmail(adr_to=email, subject=subject, text=text)
            if emsg:
                self.data['message'] = _('Send mail failed, please try again later.')
                return self.render('account/consoles/failed.html')
            else:
                self.data['message'] = _('A email have send to %(email)s, please check you inbox.') % {'email': email }
                return self.render('account/consoles/success.html')

        self.render()

    def step2_url(self, key):
        host = "%s://%s" % ( self.request.protocol,
                             self.request.host )
        x = self.reverse_url('console:account:email:change:step2')
        return '%s%s?key=%s' % (host, x, key)


class EmailChangeStep2(RequestHandler):

    '''修改我的邮箱地址：步骤二，完成验证

    '''

    @authenticated
    def get(self):

        ret, emsg = self.check_key()

        if ret:
            self.data['message'] = _('Your E-mail have changed to %s') % self.current_user.email
            self.render('account/consoles/success.html')
        else:
            self.data['message'] = emsg
            self.render('account/consoles/failed.html')

    def check_key(self):

        # 请求中是否存在 key 值
        key = self.get_argument('key', None)
        if not key:
            return False, _('Have not found key.')

        # 验证 key 是否存在
        authkey = self.db.query(AuthKey).get(key)
        if not authkey:
            return False, _('Invalid key: %s') % key

        # 验证 key 是否失效
        if authkey.expire_date < datetime.datetime.now():
            return False, _('Key is timeout')

        # 验证用户是否匹配
        user_id = authkey.get('user_id')

        if user_id != self.current_user.id:
            return False, _('User mismatch.') % key

        # 验证邮件是否被占用
        email = authkey.get('email')
        user = self.db.query(User).filter_by(email=email).first()
        if user:
            return False, _('Email %s exist.') % email

        # 修改用户 email
        self.current_user.email = email

        # 删除 authkey
        self.db.delete( authkey )

        self.db.commit()
        return True, None


class BasicInfoEdit(RequestHandler):

    '''用户基本信息编辑

    '''

    @authenticated
    def prepare(self):

        self.title = _('Edit My Basic Information')
        self.template_path = 'account/consoles/basic_edit.html'
        from tornado.locale import LOCALE_NAMES
        self.L = []
        for codename in settings.SUPPORTED_LANGUAGES:
            if codename in LOCALE_NAMES:
                self.L.append( (
                    codename,
                    LOCALE_NAMES.get(codename).get('name') ) )

        self.data = {'form': BasicInfoEditForm(self)}

    def get(self):

        form = self.data['form']
        form.language.choices = self.L
        form.language.default = self.current_user.language
        form.gender.choices = settings.GENDER_CHOICES
        form.gender.default = self.current_user.gender
        form.process()

        form.nickname.data = self.current_user.nickname
        form.first_name.data = self.current_user.first_name
        form.last_name.data = self.current_user.last_name

        self.render()


    def post(self):
        form = self.data['form']
        form.language.choices = self.L
        form.gender.data = int(form.gender.data)
        form.gender.choices = settings.GENDER_CHOICES


        if form.validate():
            user = self.current_user
            user.nickname   = form.nickname.data
            user.first_name = form.first_name.data
            user.last_name  = form.last_name.data
            user.language   = form.language.data
            user.gender     = form.gender.data
            self.db.commit()

            self.data['message'] = _('Save basic information success !')
            return self.render('account/consoles/success.html')

        self.render()

