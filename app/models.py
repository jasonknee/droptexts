"""
models.py
~~~~~~~~~

Make some comments here
"""


from app import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	social_id = db.Column(db.String(128), nullable=False, unique=True)
	username = db.Column(db.String(128), index=True, nullable=False, unique=True)
	account_sid = db.Column(db.String(128))
	auth_token = db.Column(db.String(128))
	phone_number = db.Column(db.String(32))

	# relationships
	profiles = db.relationship('Profile', backref='user', lazy='dynamic')

	def __repr__(self):
		return '<User %r' % (self.username)

	@staticmethod
	def make_unique_username(username):
		if User.query.filter_by(username=username).first() is None:
			return username
		version = 2
		while True:
			new_username = username + str(version)
			if User.query.filter_by(username=new_username).first() is None:
				break
			version += 1
		return new_username


class Profile(db.Model):
	__tablename__ = 'profiles'
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	contacts = db.relationship('Contacts', backref='profile', lazy='dynamic')
	name = db.Column(db.String(128))
	address = db.Column(db.String(128))
	message = db.Column(db.String(512))
	front_image_URL = db.Column(db.String(128))
	back_image_URL = db.Column(db.String(128))
	

class Contacts(db.Model):
	__tablename__ = 'contacts'
	id = db.Column(db.Integer, primary_key=True)
	profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'))
	filename = db.Column(db.String(128))


##############################################################################