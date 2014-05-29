# coding: UTF-8

from yweb.forms import Form
from wtforms import BooleanField, StringField, \
    validators, DateTimeField, TextAreaField, IntegerField, \
    PasswordField, FileField, SelectField, HiddenField
from wtforms.validators import ValidationError

from apps.auth.models import User, AuthCode, guess_user

from yweb.utils.translation import ugettext_lazy as _


class AvatarForm(Form):

    avatar = FileField( _('My Avatar') )
