"""
config.py
~~~~~~~~~

Make some comments here
"""

import os

WTF_CSRF_ENABLED = True
SECRET_KEY = 'jn062494'
ADMINS = ['thejayceace@gmail.com']
OAUTH_CREDENTIALS = {
    'facebook': {
        'id': '887673284674662',
        'secret': '19d7fed2154a832909cc81ebcb657cfc'
    },
    'twitter': {
        'id': '',
        'secret': ''
    },
    'imgur': {
        'id': '50916598a59fc51',
        'secret': '61e26ca01a756a69e39feb64d35fb3dca7cce25b'
    }
}


##############################################################################
# settings for heroku postgresql

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_RECORD_QUERIES = True
SQLALCHEMY_TRACK_MODIFICATIONS = True

if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = ('sqlite:///' + os.path.join(basedir, 'app.db') +
                               '?check_same_thread=False')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

##############################################################################
