# coding: UTF-8

from yweb.conf import settings


def pagination(handler):

    try:
        cur_page  = int(handler.get_argument('p', 1))
        page_size = int(handler.get_argument(
            'sepa', settings.DEFAULT_PAGE_SIZE))
    except:
        cur_page  = 1
        page_size = settings.DEFAULT_PAGE_SIZE

    if cur_page <= 0:
        cur_page = 1
    if page_size <= 1:
        page_size = settings.DEFAULT_PAGE_SIZE

    start = (cur_page - 1) * page_size
    stop = start + page_size

    return (cur_page, page_size, start, stop)
