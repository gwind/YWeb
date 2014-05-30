# coding: UTF-8

import tempfile
import Image

from . import settings as opts


def save_avatar(filedata, user):

    homedir = user.storage_path
    if not homedir:
        return False, _('User storage path is unavailable.')

    for f in filedata:

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
            img.save(user.avatar_orig_path)
            for thumsize, path in  [
                    (opts.AVATAR_LG_SIZE, user.avatar_lg_path),
                    (opts.AVATAR_MD_SIZE, user.avatar_md_path),
                    (opts.AVATAR_SM_SIZE, user.avatar_sm_path),
                    (opts.AVATAR_XS_SIZE, user.avatar_xs_path),
            ]:
                img.save(path)
                img.thumbnail(thumsize, resample=1)
            tf.close()

        except Exception, emsg:
            return False, _('Save failed: %(emsg)s') % emsg

        return True, ''
