from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = 'app/static/user_uploads/'
ALLOWED_EXTENSIONS = set(['txt', 'jpg', 'png', 'JPG', 'PNG'])


app = Flask(__name__)
app.config.from_object('config')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


db = SQLAlchemy(app)
db.init_app(app)
lm = LoginManager(app)
lm.login_view = 'login'


from app import views, models

