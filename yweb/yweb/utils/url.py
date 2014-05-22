import urllib, urlparse

# params is a dict: { 'key': value }
def urlupdate2(url, params):

    droped = [ k for k in params if params[k] == 'dropthis' ]
    for k in droped:
        del params[k]

    new = []

    if '?' in url:
        path, oldparams = url.split('?')
        update_keys = params.keys()

        for k, v in urlparse.parse_qsl( oldparams ):
            if k in droped: continue
            if k in update_keys:
                v = params[k]
                del params[k]
            new.append( (k, v) )
    else:
        path = url

    if params:
        for k in params.keys():
            if k not in droped:
                new.append( (k, params[k]) )

    return '?'.join([path, urllib.urlencode( new )])


def urlupdate(url, key, value=None):

    new = []

    if '?' in url:

        path, params = url.split('?')
        found = False

        for k, v in urlparse.parse_qsl( params ):
            if k == key:
                found = True
                if value:
                    new.append( (k, value) )
            else:
                new.append( (k, v) )

        if not found:
            if value:
                new.append( (key, value) )

    else:

        path = url

        if value:
            new = [(key, value)]

    if len(new):
        return '?'.join([path, urllib.urlencode(new)])
    else:
        return path


