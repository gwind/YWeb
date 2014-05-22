# coding: utf-8

import os
import time
import random
from hashlib import sha1

char_alphabet = "abcdefghijklmnopqrstuvwxyz"
char_digit = "0123456789"

def random_ascii(length, digit=True, ignorecase=False, drops=None ):

    global char_alphabet, char_digit

    chars = char_alphabet
    if digit:
        chars += char_digit
    if not ignorecase:
        chars += char_alphabet.upper()

    if isinstance(drops, str):
        L = list(chars)
        for drop in drops:
            if drop in L:
                L.remove(drop)
        chars = ''.join(L)

    if length < len(chars):
        return ''.join(random.sample(chars, length))
    else:
        r_list = []
        for i in xrange(length):
            r_list.append(random.choice(chars))

        return ''.join(r_list)


def random_sha1():
    s = sha1( os.urandom(256) )
    s.update( str(time.time()) )
    s.update( str(random.randrange(1, 100000000)) )
    key = s.hexdigest()
    return key


if __name__ == '__main__':

    print 'random_sha1()    : %s' % random_sha1()
    print 'random_ascii(40) : %s' % random_ascii(40)

