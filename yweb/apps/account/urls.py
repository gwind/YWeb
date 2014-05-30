# coding: utf-8

from tornado.web import url
from . import consoles

console_handlers = [

    url( r'/console/account', consoles.Index,
         name='console:account' ),
    
    url( r'/console/account/avatar/change', consoles.AvatarChange,
         name='console:account:avatar:change' ),

    url( r'/console/account/password/change', consoles.PasswordChange,
         name='console:account:password:change' ),
   
    url( r'/console/account/email/change', consoles.EmailChangeStep1,
         name='console:account:email:change' ),
    url( r'/console/account/email/change/step1', consoles.EmailChangeStep1,
         name='console:account:email:change:step1' ),
    

    url( r'/console/account/email/change/step2', consoles.EmailChangeStep2,
         name='console:account:email:change:step2' ),

    url( r'/console/account/basicinfo/edit', consoles.BasicInfoEdit,
         name='console:account:basicinfo:edit' ),
    
]

