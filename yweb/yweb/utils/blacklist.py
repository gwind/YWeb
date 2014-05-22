# coding: utf-8

import re
import codecs

def has_illegal_chars(orig_string, blacklist_file):

    with codecs.open(blacklist_file, 'r', 'utf-8') as f:
        for line in f:

            line = line.strip()

            if not line or line.startswith(';'):
                continue

            L = line.split()

            for w in L:

                w = w.strip()

                if not w or w.startswith(';'):
                    continue

                if ( '.' in w or
                     '*' in w or
                     '^' in w or
                     '$' in w ):
                    match = re.findall(w, orig_string, re.IGNORECASE)
                else:
                    match = orig_string.count( w ) > 0

                if match:
#                    print 'Illegal chars: %s IN LINE "%s"' % (w, line)
                    return True, w, line

    return False, '', ''


if __name__ == '__main__':

    import sys
    blacklist_file = sys.argv[1]

    for string in [ u'中国',
                    u'诗词',
                    u'av',
                    u'千里',
                    u'great firewall',
                    u'翻墙',
                    u'日本' ]:
        r, i, m = has_illegal_chars(string, blacklist_file)
        if r:
            print 'Illegal chars: %s IN LINE "%s"' % (i, m)
        else:
            print 'safe: %s' % string

