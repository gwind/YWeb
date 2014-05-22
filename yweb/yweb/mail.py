# -*- coding: utf-8 -*-
# https://github.com/marcinc81/quemail/blob/master/quemail.py

# Updater: Jian <lijian@luoyun.co>


import os
import smtplib
import logging
import time
import pickle

from email.mime.text import MIMEText
from email.utils import make_msgid, formatdate

from yweb.conf import settings


class Email(object):
    unique = 'unique-send'
    
    def __init__(self, **props):
        '''
        @param adr_to: send to
        @param adr_from: send from
        @param subject: subject of email
        @param mime_type: plain or html - only minor mime type of 'text/*'
        @param text: text content of email
        ''' 
        self.text = props.get('text', '')
        self.subject = props.get('subject', None)
        self.adr_to = props.get('adr_to', None)
        self.adr_from = props.get('adr_from', None)
        self.mime_type = props.get('mime_type', 'plain')
        
    def __str__(self):
        return "Email to: %s, from: %s, sub: %s" % (self.adr_to, self.adr_from, self.subject)

    def as_rfc_message(self):
        '''
        Creates standardized email with valid header
        '''
        msg = MIMEText(self.text, self.mime_type, 'utf-8')
        msg['Subject'] = self.subject
        msg['From'] = self.adr_from
        msg['To'] = self.adr_to
        msg['Date'] = formatdate()
        msg['Reply-To'] = self.adr_from
        msg['Message-Id'] = make_msgid(Email.unique)
        return msg


def sendmail(adr_to, subject, text, mime_type='html'):

    data = settings.EMAIL

    adr_from = data.get('adr_from')
    smtp_host = data.get('smtp_host')
    smtp_port = data.get('smtp_port')
    smtp_username = data.get('smtp_username')
    smtp_password = data.get('smtp_password')

    if not adr_from and '@' in smtp_username:
        adr_from = smtp_username

    eml = Email( subject=subject,
                 text=text,
                 adr_to=adr_to,
                 adr_from=adr_from,
                 mime_type="html" )

    # No news is good news
    emsg = None

    smtp = None
    try:
        smtp = smtplib.SMTP()
        smtp.connect(smtp_host, smtp_port)

        # 需要登录
        if smtp_username and smtp_password:
            smtp.login(smtp_username, smtp_password)
    
        try:
            msg = eml.as_rfc_message()
            content = msg.as_string()
            smtp.sendmail(eml.adr_from, eml.adr_to, content)
            logging.debug('Send mail to %s success' % eml.adr_to)
        except Exception as e:
            logging.exception(e)
            emsg = e

    except Exception as e:
        logging.exception(e)
        emsg = e
    finally:
        if smtp:
            smtp.quit()

    return emsg
