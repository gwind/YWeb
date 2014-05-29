# coding: UTF-8

'''Just For Fun !

:-)

'''

import os
import random

from yweb.conf import settings


def get_hi_img():

    '''获取随机打招呼图片

    开发者可以自行放任何图片到 static/img/hi 目录下。
    '''

    os.chdir(os.path.join(settings.STATIC_PATH, 'img/hi/'))
    return 'img/hi/{0}'.format(random.choice(os.listdir('.')))

