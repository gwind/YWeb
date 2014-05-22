# coding: utf-8

from markdown import Markdown

# 系统中要安装 python-pygments

YMK = Markdown( extensions=['fenced_code', 'tables', 'codehilite'],
                extension_configs={
                    'codehilite': [
#                        ('force_linenos', True),
                    ],
                },
                safe_mode='escape' )


def generate_html(body, markup_language=1):

    if markup_language == 1: # Markdown
        return YMK.convert( body )
    else:
        return body
    
