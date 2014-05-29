# coding: utf-8

from tornado.web import url
from . import consoles

console_handlers = [

    url( r'/console/account', consoles.Index,
         name='console:account' ),
    
    url( r'/console/account/avatar/edit', consoles.AvatarEdit,
         name='console:account:avatar:edit' ),
    
]

