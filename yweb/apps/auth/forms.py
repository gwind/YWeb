# coding: utf-8

import re
import codecs

from yweb.forms import Form
from yweb.utils.i18n import ugettext as _
from wtforms import BooleanField, StringField, \
    validators, DateTimeField, TextAreaField, IntegerField, \
    PasswordField, FileField, SelectField, HiddenField
from wtforms.validators import ValidationError

from apps.auth.models import User, AuthCode, guess_user

from yweb.conf import settings
import yweb.utils.blacklist 
import yweb.utils.password


def validate_password(form, field):

    '''验证新密码是否合理

    '''

    password = field.data

    if len(password) < 6:
        raise ValidationError(_('Password must be greater than 6 characters.'))

    if len(password) > 64:
        raise ValidationError(_('Password must be less than 64 characters.'))

    # 如果密码太简单，不容许通过
    if settings.PASSWORD_BLACKLIST_FILE:
        if yweb.utils.password.is_too_simple(
                password, settings.PASSWORD_BLACKLIST_FILE):
            raise ValidationError(_("Password is too simple"))


def check_authcode(form, field):

    '''检查验证码

    '''
    code = field.data

    if len(code) >= 4: # 验证码不少于4

        key = form.authcode_key.data
        authcode = form._handler.db.query(AuthCode).get(key)

        if authcode and authcode.code.lower() == code.lower():
            form._handler.db.delete(authcode)
            form._handler.db.commit()
            return

    raise ValidationError( _("Authcode does not match.") )


class SignInForm(Form):

    '''用户登录表单

    '''

    user = StringField( _('User'), default='' )
    password = PasswordField( _('Password'), default='' )
    authcode_key = HiddenField( _("Authcode Key") )
    authcode_code = StringField( _("Authcode Code"), [check_authcode] )

    def validate_user(form, field):

        if len(field.data) == 0:
            raise ValidationError(_('Username is empty.'))

        user = guess_user(form._handler.db, field.data)
        if not user:
            raise ValidationError( _('The user does not exist.') )

        if user.is_locked:
            raise ValidationError( _('You have been locked.') )

        if not user.check_password( form.password.data ):
            raise ValidationError( _('Password is incorrect.') )

        if not user.is_active:
            raise ValidationError( _('Your are inactive now.') )
                
        form.__dict__['_user'] = user


class EmailValidationForm(Form):
    email = StringField( _('Email Address'), [validators.Length(min=6, max=35), validators.Email()])


class SignUpForm(Form):

    '''用户注册表单

    '''

    email = StringField(_('Email Address'), [
        validators.Length(min=6, max=35), validators.Email()])

    authcode_key = HiddenField( _("Authcode Key") )
    authcode_code = StringField( _("Authcode Code"), [check_authcode] )

    def validate_email(form, field):
        user = form._handler.db.query(User).filter_by(email=field.data).first()
        if user:
            raise ValidationError(_('Email address is exist.'))


class PasswordResetForm(Form):

    '''重置用户密码表单

    '''

    email = StringField(_('Email Address'), [
        validators.Length(min=6, max=35), validators.Email()])

    authcode_key = HiddenField( _("Authcode Key") )
    authcode_code = StringField( _("Authcode Code"), [check_authcode] )

    def validate_email(form, field):

        # 用户邮箱是否存在
        user = form._handler.db.query(User).filter_by(email=field.data).first()
        if not user:
            raise ValidationError(_('Email address is not exist.'))

        form.__dict__['_user'] = user


class PasswordResetStep2Form(Form):

    '''密码重置步骤2表单：重置密码

    '''

    password = PasswordField(_('Password'), [
        validate_password,
        validators.Required(),
        validators.EqualTo('confirm', message=_('Passwords must match'))
    ], default='')
    confirm = PasswordField(_('Confirm'), default='')
    authcode_key = HiddenField( _("Authcode Key"))
    authcode_code = StringField(_("Authcode Code"), [check_authcode])


class UserCreateForm(Form):

    '''用户注册表单

    '''

    username = StringField(_('Username'))
    password = PasswordField( _('Password'), [
        validators.Required(),
        validators.EqualTo('confirm', message=_('Passwords must match'))
    ])
    confirm = PasswordField(_('Password Confirm'))
    accept_tos = BooleanField(_('I accept the TOS'), [
        validators.Required()])

    def validate_username(form, field):

        username = field.data

        ## 检查用户名规范

        # 不能是数字（与UID有冲突）
        if username.isdigit():
            raise ValidationError(_('Username can not be a number.'))

        # 用户名太短
        if len(username) < 2:
            raise ValidationError(_('Username less than 2 characters.'))

        # 用户名太长
        if len(username) > 16:
            raise ValidationError(_('Username greater than 16 characters.'))            

        # 非常乱的用户名合理性检查
        import yweb.utils.ystr
        en_count, zh_count = yweb.utils.ystr.count_chars_en_zh(username)
        if zh_count < 2:
            # 汉字数少于2
            if en_count < 4:
                # 英语字符数也不能少于4
                raise ValidationError(_('English username less than 4 characters.'))
        else:
            # 汉字数不应大于8个
            if zh_count > 8:
                raise ValidationError(_('Chinese username greater than 6 characters.'))

        # 检查用户名是否存在
        user = guess_user(form._handler.db, field.data)
        if user:
            raise ValidationError(_('Username occupied.'))

        # 使用一个不可以使用的名字清单
        if settings.USERNAME_BLACKLIST_FILE:
            r, ics, m = yweb.utils.blacklist.has_illegal_chars(
                username, settings.USERNAME_BLACKLIST_FILE)
            if r:
                raise ValidationError(_('Illegal Chars: {0}'.format(ics)))

    def validate_password(form, field):

        password = field.data

        if len(password) < 6:
            raise ValidationError(_('Password must be greater than 6 characters.'))

        if len(password) > 64:
            raise ValidationError(_('Password must be less than 64 characters.'))

        # 如果密码太简单，不容许通过
        if settings.PASSWORD_BLACKLIST_FILE:
            if yweb.utils.password.is_too_simple(
                    password, settings.PASSWORD_BLACKLIST_FILE):
                raise ValidationError(_("Password is too simple"))

