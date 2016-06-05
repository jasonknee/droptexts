#imgur.py

from imgurpython import ImgurClient
from flask import current_app


class Imgur():
	def __init__(self):
		self.client_id = current_app.config['OAUTH_CREDENTIALS']['imgur']['id']
		self.client_secret = current_app.config['OAUTH_CREDENTIALS']['imgur']['secret']
		self.client = ImgurClient(self.client_id, self.client_secret)

	def upload(self, filepath):
		result = self.client.upload_from_path(filepath, config=None, anon=True)
		return result['link']
