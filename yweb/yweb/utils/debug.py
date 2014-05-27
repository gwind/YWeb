# coding: UTF-8

import logging
from traceback import extract_stack


def call_debug(msg):

    ES = extract_stack()
    level = len(ES)
    if level > 12:
        level = 12

    # -1 is this func stack
    for i in reversed( range(2, level) ):
        caller = ES[-i]
        msg += "\n  %s:%s %s" % (caller[0], caller[1], caller[2])

    logging.debug("[JL] %s" % msg)
