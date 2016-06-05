#forms.py

"""
Make some comments here

It will look like this

"""

from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired, Length
from app.models import User, Profile, Contacts

class ProfileForm(Form):
	name = StringField('name')
	address = StringField('address')
	message = StringField('message')

class UserForm(Form):
	account_sid = StringField('account_sid')
	auth_token = StringField('oauth_token')
	phone_number = StringField('phone_number')
