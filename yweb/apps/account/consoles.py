# coding: utf-8

import tempfile
import Image
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
    EmailChangeStep1Form
from . import settings as opts


class Index(RequestHandler):

    @authenticated
    def get(self):

        self.data = {'ftime': ftime}

        self.render('account/consoles/index.html')


class AvatarChange(RequestHandler):

    @authenticated
    def prepare(self):

        self.title = _('Change My Avatar')
        self.template_path = 'account/consoles/avatar_change.html'
        self.data = { 'form': AvatarChangeForm(self) }

    def post(self):
        form = self.data['form']

        if self.request.files and form.validate():
            ret, emsg = self.save_avatar()
            if ret:
                self.data['message'] = _('Change Avatar Success !')
                return self.render('account/consoles/success.html')
            else:
                self.data['message'] = emsg
                return self.render('account/consoles/failed.html')

        self.render()

    def save_avatar(self):

        homedir = self.current_user.storage_path
        if not homedir:
            return False, _('User storage path is unavailable.')

        for f in self.request.files['avatar']:

            if len(f['body']) > opts.AVATAR_MAXSIZE:
                return False, _('Picture can not be greater than %s') % (
                    human_size(opts.AVATAR_MAXSIZE))

            tf = tempfile.NamedTemporaryFile()
            tf.write(f['body'])
            tf.seek(0)

            try:
                img = Image.open( tf.name )
            except Exception, emsg:
                return False, _(
                    'Process %(filename)s failed, ' + \
                    'make sure that you provide the ' + \
                    'correct image format: %(emsg)s') % {
                        'filename': f.get('filename'), 'emsg': emsg }

            try:
                U = self.current_user
                img.save(U.avatar_orig_path)
                for thumsize, path in  [
                        (opts.AVATAR_LG_SIZE, U.avatar_lg_path),
                        (opts.AVATAR_MD_SIZE, U.avatar_md_path),
                        (opts.AVATAR_SM_SIZE, U.avatar_sm_path),
                        (opts.AVATAR_XS_SIZE, U.avatar_xs_path),
                ]:
                    img.save(path)
                    img.thumbnail(thumsize, resample=1)
                tf.close()

            except Exception, emsg:
                return False, _('Save failed: %(emsg)s') % emsg

            return True, ''


class PasswordChange(RequestHandler):

    @authenticated
    def prepare(self):
        self.title = _('Change My Password')
        self.template_path = 'account/consoles/password_change.html'
        self.data = {'form': PasswordChangeForm(self)}

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
        self.template_path = 'account/consoles/email_change_step1.html'
        self.data = {'form': EmailChangeStep1Form(self)}

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
                self.data['message'] = emsg
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
