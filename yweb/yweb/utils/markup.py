# coding: utf-8

from markdown import Markdown
import docutils.core

# 系统中要安装 python-pygments

YMK = Markdown( extensions=['fenced_code', 'tables', 'codehilite'],
                extension_configs={
                    'codehilite': [
#                        ('force_linenos', True),
                    ],
                },
                safe_mode='escape' )


def rst2html(body):

    '''
    http://stackoverflow.com/questions/6654519/parsing-restructuredtext-into-html
    publish_string, publish_parts
    
    >>> from docutils.core import publish_string
    >>> publish_string("*anurag*",writer_name='html')

    >>> print publish_parts("*anurag*",writer_name='html')['html_body']
    <p><em>anurag</em></p>
    '''

    return docutils.core.publish_parts(body, writer_name='html')['html_body']


def generate_html(body, markup_language=1):

    if markup_language == 1: # Markdown
        return YMK.convert( body )
    elif markup_language == 2: # reStructuredText
        return rst2html( body )
    else:
        return body
    
