# coding: utf-8

import os
import logging
import StringIO

import Image
import ImageFont
import ImageDraw

from yweb.handler import RequestHandler
from yweb.conf import settings

from .models import AuthCode


class AuthCodeImg(RequestHandler):

    '''获取指定Key的验证码图片

    1. 用 key 在 AuthCode 表中查找记录
    2. 用该记录的 code 字符串生成验证码图片
    3. 返回图片到用户请求页面

    '''

    def get(self, key):

        authcode = self.db.query(AuthCode).get(key)
        if not authcode:
            return self.redirect('/404')

        output = StringIO.StringIO()

        text = authcode.code
        im = Image.new("RGB",(130,35), (255, 255, 255))
        dr = ImageDraw.Draw(im)
        font = ImageFont.truetype(settings.AUTHCODE_IMG_FONT, 24)
        dr.text((10, 5), text, font=font, fill="#000000")
        im.save(output,"GIF")
        img_data = output.getvalue()
        output.close()
        self.set_header('Content-Type', 'image/gif')
        self.write(img_data)
