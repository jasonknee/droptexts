"""
views.py
~~~~~~~~~

Make some comments here
"""

import os, base64

from flask import render_template, flash, redirect, url_for, g, request
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from .models import User, Profile, Contacts
from .forms import ProfileForm, UserForm
from .oauth import OAuthSignIn
from .upload import allowed_file
from .imgur import Imgur
from twilio.rest import TwilioRestClient
from werkzeug import secure_filename
from random import randint


@lm.user_loader
def load_user(id):
	return User.query.get(int(id))

@app.before_request
def before_request():
    if current_user.is_authenticated:
        g.user = current_user


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

##############################################################################


@app.route('/', methods=['GET'])
def index():
	profiles = None
	if current_user.is_authenticated:
		profiles = Profile.query.filter_by(user=current_user)
	return render_template('index.html',
							title='Home',
							profiles=profiles)

##############################################################################



##############################################################################


@app.route('/new', methods=['GET', 'POST'])
def new():
	form = ProfileForm()

	if form.validate_on_submit():
		profile = Profile() #~~ create a new profile
		profile.user = current_user
		profile.name = form.name.data
		profile.address = form.address.data
		profile.message = form.message.data
		db.session.add(profile)
		db.session.commit()
		return redirect(url_for('index'))
	else:
		return render_template('new.html',
								form=form)

@app.route('/<profile>/contacts', methods=['GET', 'POST'])
def contacts(profile):
	profile = Profile.query.filter_by(name=profile, user=current_user).first()
	contacts = Contacts.query.filter_by(profile=profile)
	return render_template('contacts.html',
							contacts=contacts,
							profile=profile)

@app.route('/<profile>/contacts/upload', methods=['GET', 'POST'])
def upload_contacts(profile):
	profile = Profile.query.filter_by(name=profile, user=current_user).first()

	if request.method == 'POST':
        # check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		# if user does not select file, browser also
		# submit a empty part without filename
		if file.filename == '':
			flash('No selected file')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

			contacts = Contacts()
			contacts.profile = profile
			contacts.filename = filename
			db.session.add(contacts)
			db.session.commit()
			return redirect(url_for('contacts', profile=profile.name))
	return render_template('upload_contacts.html')


@app.route('/<profile>/verify/', methods=['GET'])
def verify(profile):
	filename = request.args.get('filename')
	profile = Profile.query.filter_by(name=profile, user=current_user).first()
	return render_template('verify.html',
							profile=profile,
							filename=filename)

@app.route('/<profile>/modify', methods=['GET', 'POST'])
def modify(profile):
	filename = request.args.get('filename')
	profile = Profile.query.filter_by(name=profile, user=current_user).first()
	form = ProfileForm()
	if form.validate_on_submit():
		profile.user = current_user
		profile.name = form.name.data
		profile.address = form.address.data
		profile.message = form.message.data
		db.session.add(profile)
		db.session.commit()
		return redirect(url_for('verify', profile=profile.name, filename=filename))
	else:
		form.name.data = profile.name
		form.address.data = profile.address
		form.message.data = profile.message
		return render_template('new.html',
						form=form)

@app.route('/<profile>/upload/front_image', methods=['GET', 'POST'])
def upload_front_image(profile):
	profile = Profile.query.filter_by(name=profile, user=current_user).first()

	if request.method == 'POST':
        # check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		print(file)
		# if user does not select file, browser also
		# submit a empty part without filename
		if file.filename == '':
			flash('No selected file')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

			imgur = Imgur()
			imageURL = imgur.upload(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))

			profile.front_image_URL = imageURL
			db.session.add(profile)
			db.session.commit()

			return redirect(url_for('verify', profile=profile.name))
	return render_template('upload_image.html')


@app.route('/<profile>/upload/back_image', methods=['GET', 'POST'])
def upload_back_image(profile):
	profile = Profile.query.filter_by(name=profile, user=current_user).first()

	if request.method == 'POST':
        # check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		print(file)
		# if user does not select file, browser also
		# submit a empty part without filename
		if file.filename == '':
			flash('No selected file')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

			imgur = Imgur()
			imageURL = imgur.upload(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))

			profile.back_image_URL = imageURL
			db.session.add(profile)
			db.session.commit()

			return redirect(url_for('verify', profile=profile.name))
	return render_template('upload_image.html')


@app.route('/<profile>/send', methods=['GET'])
def send(profile):
	filename = request.args.get('filename')
	profile = Profile.query.filter_by(name=profile, user=current_user).first()
	client = TwilioRestClient(current_user.account_sid, current_user.auth_token)
	phone = current_user.phone_number
	message = profile.message + " - " + profile.address
	lines = []
	media = []

	if profile.front_image_URL:
		media.append(profile.front_image_URL)
	if profile.back_image_URL:
		media.append(profile.back_image_URL)

	# split contact numbers into an array
	with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'r') as f:
		lines = f.read().splitlines()

	# send message out to each contact

	try:
		for line in lines[1:]:
			message = client.messages.create(body=message,
									    	to="+1"+line,    # Replace with your phone number
									    	from_="+1"+phone,
									    	media_url=media) # Replace with your Twilio number
	except:
		pass


	image = images[randint(0,18)]
	return render_template('success.html',
							image=image)









##############################################################################

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
	if not current_user.is_anonymous:
		return redirect(url_for('index'))
	oauth = OAuthSignIn.get_provider(provider)
	return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
	if not current_user.is_anonymous:
		return redirect(url_for('index'))
	oauth = OAuthSignIn.get_provider(provider)
	social_id, username, email = oauth.callback()
	if social_id is None:
		flash('Authentication failed.')
		return redirect(url_for('index'))
	user = User.query.filter_by(social_id=social_id).first()
	if not user:
		print(username)
		user = User(social_id=social_id, username=username)
		db.session.add(user)
		db.session.commit()
		login_user(user,True)
		return redirect(url_for('setup'))
	login_user(user,True)
	return redirect(url_for('index'))

@app.route('/setup/user', methods=['GET', 'POST'])
def setup():
	user = current_user
	form = UserForm()

	if form.validate_on_submit():
		user.account_sid = form.account_sid.data
		user.auth_token = form.auth_token.data
		user.phone_number = form.phone_number.data
		db.session.add(user)
		db.session.commit()
		return redirect(url_for('index'))
	else:
		form.account_sid.data = user.account_sid
		form.auth_token.data = user.auth_token
		form.phone_number.data = user.phone_number
		return render_template('setup.html',
								form=form)


##############################################################################
# PROGRAM CONSTANTS

images = [
		"http://i.imgur.com/JoF5FNd.jpg",
		"http://www.lovethispic.com/uploaded_images/53451-Cute-Dog.jpg",
		"http://www.windowsmode.com/wp-content/uploads/2015/08/Cute-Puppies-Wallpaper.jpg",
		"http://hdwallpaperia.com/wp-content/uploads/2013/11/Cute-Dog-Boo-Wallpaper-640x400.jpg",
		"http://i.imgur.com/lsoomRq.jpg",
		"../static/img/1.png",
		"../static/img/2.jpeg",
		"../static/img/3.jpeg",
		"../static/img/4.jpeg",
		"../static/img/5.jpeg",
		"../static/img/6.png",
		"../static/img/7.png",
		"../static/img/8.jpeg",
		"../static/img/9.jpeg",
		"../static/img/10.jpg",
		"../static/img/11.jpg",
		"../static/img/12.jpg",
		"../static/img/13.jpg",
		"../static/img/14.jpg"
		]
