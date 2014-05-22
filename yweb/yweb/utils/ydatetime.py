#!/usr/bin/env python
# coding: utf-8

import time, datetime, logging
from dateutil import relativedelta


def htime( t ):

    ''' return a human ago aime '''

    if not isinstance(t, datetime.datetime):
        return 'N/A'

    ago = relativedelta.relativedelta(datetime.datetime.now(), t)

    if ago.years > 0:
        s = u'%s年前' % ago.years

    elif ago.months > 0:
        s = u'%s月前' % ago.months

    elif ago.days > 0:
        s = u'%s天前' % ago.days

    elif ago.hours > 0:
        s = u'%s小时前' % ago.hours

    elif ago.minutes > 0:
        s = u'%s分钟前' % ago.minutes

    elif ago.seconds > 0:
        s = u'%s秒前' % ago.seconds

    else:
        #s = _('%s microseconds ago') % ago.microseconds
        s = u'刚刚'

    return s


def ftime(t, f='%Y-%m-%d %H:%M:%S'):

    try:
        return datetime.datetime.strftime(t, f)
    except Exception, e:
        #logging.error( 'format time "%s" failed: %s' % (t, e) )
        return 'N/A'


def after_days(days):

    '''返回指定天数后的时间

    '''

    now = datetime.datetime.now()
    return now + datetime.timedelta(days=days)
