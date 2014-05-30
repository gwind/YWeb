# coding: UTF-8

import os
import logging
import re
import urlparse
import urllib

from yweb.handler import UIModule
from yweb.conf import settings


def pagination( url, total, sepa, cur, list_size=5,
                sepa_range=[] ):

    if total <= sepa:
        return {}

    sepa_range = [x for x in sepa_range if x < total]

    page_sum = total / sepa
    if ( total % sepa ): page_sum += 1

    notexist_p = page_sum + 1

    last_p = page_sum
    start = ( cur / (list_size + 1) ) * list_size + 1
    end = start + list_size
    if end > last_p: end = last_p

    plist = range(start, end + 1)

    if end < last_p:
        plist.extend( [notexist_p, last_p] )

    if cur > list_size:
        plist.insert(0, notexist_p)
        plist.insert(0, 1)

    def _page_url(cur):
        return page_url(url, cur)

    d = { 'total': total, 'plist': plist,  'sepa': sepa,
          'cur_page': cur, 'page_sum': page_sum,
          'notexist_page': notexist_p,
          'page_url': _page_url }

    if sepa_range:
        def _psize_url(cur):
            return psize_url(url, cur)
        d['psize_url'] = _psize_url
        d['sepa_range'] = sepa_range

    return d


def page_url(uri, cur):

    if '?' not in uri:
        return uri + '?p=%s' % cur

    path, params = uri.split('?')
    new = []
    find_p = False
    for k, v in urlparse.parse_qsl( params ):
        if k == 'p':
            v = cur
            find_p = True
        new.append( (k, v) )

    if not find_p:
        new.append( ('p', cur) )

    return '?'.join([path, urllib.urlencode(new)])


def psize_url(uri, cur):

    if '?' not in uri:
        return uri + '?sepa=%s' % cur

    path, params = uri.split('?')
    new = []
    find_sepa = False
    for k, v in urlparse.parse_qsl( params ):
        if k == 'sepa':
            v = cur
            find_sepa = True
        if k == 'p':
            v = 1
        new.append( (k, v) )

    if not find_sepa:
        new.append( ('sepa', cur) )

    return '?'.join([path, urllib.urlencode(new)])


class PaginationUI(UIModule):

    '''提供分页功能的 UI

    '''

    def render(self, total, list_size=5, sepa_range=[]):
        url = self.handler.request.uri
        try:
            sepa = int(self.handler.get_argument(
                'sepa', settings.DEFAULT_PAGE_SIZE))
            cur = int(self.handler.get_argument('p', 1))
        except:
            cur = 1
            sepa = settings.DEFAULT_PAGE_SIZE
        d = pagination(url, total, sepa, cur, list_size, sepa_range)
        if d:
            return self.render_string('common/modules/pagination.html', **d)
        else:
            return ''
