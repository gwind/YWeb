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

from .forms import AvatarForm
from . import settings as opts


class Index(RequestHandler):

    @authenticated
    def get(self):

        self.data = {'ftime': ftime}

        self.render('account/consoles/index.html')


class AvatarEdit(RequestHandler):

    @authenticated
    def prepare(self):

        self.template_path = 'account/consoles/avatar_edit.html'
        self.title = _('Edit My Avatar')
        self.data = { 'form': AvatarForm(self) }

    def post(self):
        form = self.data['form']

        if self.request.files and form.validate():
            ret, emsg = self.save_avatar()
            if ret:
                url = self.reverse_url('console:account')
                return self.redirect(url)
            else:
                form.avatar.errors.append( emsg )

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
