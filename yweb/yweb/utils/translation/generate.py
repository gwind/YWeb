# coding: UTF-8

'''
创建、更新 po 文件
编绎 mo 文件
'''

import os
import logging

import yweb.utils.cmd
from yweb.conf import settings


def update_locales(orig_po, root_path, basename='yweb'):

    '''根据原始 po 文件，创建/更新指定目录中的各语言对应的 po,mo

    指定目录 root_path 下 locale 子目录应该类似这样：

    locale/en_US/LC_MESSAGES/
    locale/zh_CN/LC_MESSAGES/
    
    '''

    for LANG in settings.SUPPORTED_LANGUAGES:
        locale_path = os.path.join(
            root_path, 'locale/{0}/LC_MESSAGES/'.format(LANG) )
        po_path = os.path.join(
            locale_path, '{0}.po'.format(basename) )
        mo_path = os.path.join(
            locale_path, '{0}.mo'.format(basename) )

        # 如果目录不存在，创建目录
        if not os.path.exists(locale_path):
            os.makedirs(locale_path)

        # 如果 po 文件存在，就合并
        if os.path.exists(po_path):
            logging.debug('update {0}'.format(po_path))
            cmd = 'msgmerge {0} {1} -o new.po'.format(po_path, orig_po)
            yweb.utils.cmd.run_cmd(cmd)

            if os.path.exists('new.po'):
                cmd = '/bin/mv new.po {0}'.format(po_path)
                yweb.utils.cmd.run_cmd(cmd)
        else:
            logging.debug('generate {0}'.format(po_path))
            cmd = 'msginit --no-translator ' + \
                  '--input={0} '.format(orig_po) + \
                  ' --locale={0}.UTF-8 '.format(LANG) + \
                  '--output={0}'.format(po_path)
            yweb.utils.cmd.run_cmd(cmd)

        # 更新 mo
        logging.debug('rebuild {0}'.format(mo_path))
        cmd = 'msgfmt {0} -o {1}'.format(po_path, mo_path)
        yweb.utils.cmd.run_cmd(cmd)
