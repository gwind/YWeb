from hashlib import md5, sha256
import crypt
import random
import time
import random
import logging
import base64
import pickle

from yweb.utils.random_ import random_ascii


def _encrypt_password(salt, raw_password):
    hsh = sha256(salt + raw_password).hexdigest()
    return hsh


def enc_login_passwd( plaintext ):
    salt = random_ascii(8)
    hsh = _encrypt_password(salt, plaintext)
    enc_password = "%s$%s" % (salt, hsh)

    return enc_password


def check_login_passwd(raw_password, enc_password):
    try:
        salt, hsh = enc_password.split('$')
    except:
        return False
    return hsh == _encrypt_password(salt, raw_password)


def enc_shadow_passwd( plaintext ):

    # get shadow passwd

    salt = crypt.crypt( str(random.random()), str(time.time()) )[:8]
    s = '$'.join( ['','6', salt,''] )
    password = crypt.crypt( plaintext, s )

    return password


def encode_data(data, skey):

    pickle_data = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)
    tamper_data = md5(pickle_data + skey).hexdigest()
    return base64.encodestring(pickle_data + tamper_data)

def decode_data(data, skey):

    data = base64.decodestring(data)
    pickle_data, tamper_data = data[:-32], data[-32:]

    if md5(pickle_data + skey).hexdigest() != tamper_data:
        logging.warn("User tampered with session cookie.")
        return None
    else:
        return pickle.loads(pickle_data)


if __name__ == '__main__':

    skey = 'testfor'

    edata = encode_data( {'user_id': 5}, skey )
    print 'edata = {0}'.format(edata)

#    skey = 'testfo'
    data = decode_data( edata, skey )
    print 'data = {0}'.format(data)
