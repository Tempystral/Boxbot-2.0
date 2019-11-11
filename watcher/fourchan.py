import itertools
import time
from datetime import datetime

import requests
from html2text import html2text

class NetworkError(Exception):
	pass

class Post:
	def __init__(self, data, board):
		self._data = data
		self._board = board

	@property
	def no(self):
		return self._data.get('no')

	@property
	def subject(self):
		return self._data.get('sub', '')

	@property
	def html_comment(self):
		return self._data.get('com', '')

	@property
	def comment(self):
		return html2text(self.html_comment).rstrip()

	@property
	def name(self):
		return self._data.get('name', '')

	@property
	def time(self):
		return self._data.get('time')

	@property
	def datetime(self):
		return datetime.fromtimestamp(self.time)

	@property
	def ctime(self):
		return self.datetime.ctime()

	@property
	def slug(self):
		return self._data.get('semantic_url')
	
	@property
	def board(self):
		return self._board

	@property
	def url(self):
		u = "https://boards.4chan.org/{board}/thread/{no}/{slug}".format(
				board = self.board,
				no = self.no,
				slug = self.slug)
		return u

class Chan:
	def __init__(self):
		self.s = requests.session()

	def catalog(self, board):
		url = 'https://a.4cdn.org/{}/catalog.json'
		for retry in range(5):
			try:
				response = self.s.get(url.format(board), timeout=60)
				response.raise_for_status()
				data = response.json()
			except requests.exceptions.ConnectionError:
				print(f"Connection error, retrying({retry})...")
				time.sleep(5*1.5**retry)
				continue
			except requests.exceptions.Timeout:
				print(f"Connection timed out, retrying({retry})...")
				time.sleep(5*1.5**retry)
				continue
			except requests.exceptions.HTTPError as e:
				print(f"HTTP error {e.response.status_code}, retrying({retry})")
				time.sleep(5*1.5**retry)
				continue
			break
		else:
			raise NetworkError()
			
		threads = itertools.chain(*(page['threads'] for page in data))
		return [Post(i, board) for i in threads]
