import sys
from lxml.etree import ElementTree
from lxml.etree import ParseError
from urllib import request as askurl


def build_tree(request):
	try:
		tree = ElementTree().parse(request)
	except ParseError as err:
		print('Parsing failed: {err}'.format(err=err))
		sys.exit(42)
	return tree


class Receiver(object):
	def __init__(self, ip='192.168.1.183', port=80):
		self.ip = ip
		self.port = str(port)

	def api_handle(self, append_url):
		url = 'http://{0}:{1}/web/{2}'.format(self.ip, self.port, append_url)
		request = askurl.Request(url)
		response = askurl.urlopen(request)
		return response

	def get_current_channel(self):
		request = self.api_handle('subservices')
		tree = build_tree(request)
		for e2about in tree.getiterator('e2servicelist'):
			try:
				e2servicename = e2about.find('.//e2servicename').text
			except AttributeError as e:
				print('Element error: {err}'.format(err=e))
		return e2servicename

	def get_current(self):
		request = self.api_handle('getcurrent')
		tree = build_tree(request)
		for details in tree.getiterator('e2currentserviceinformation'):
			try:
				e2servicename = details.find('.//e2servicename').text
				e2providername = details.find('.//e2providername').text
				e2servicevideosize = details.find('.//e2servicevideosize').text
				e2eventservicereference = details.find('.//e2eventservicereference').text
				e2eventname = details.find('.//e2eventname').text
				e2eventdescriptionextended = details.find('.//e2eventdescriptionextended').text
			except ArithmeticError as e:
				print('Element error: {err}'.format(err=e))
		return (e2servicename, e2providername, e2servicevideosize, e2eventservicereference, e2eventname,
				e2eventdescriptionextended)

	def get_audio_status(self):
		request = self.api_handle('vol?set=state')
		tree = build_tree(request)
		for volume_stat in tree.getiterator('e2volume'):
			try:
				worked = volume_stat.find('.//e2result').text
				volume_status = volume_stat.find('.//e2current').text
				mute_status = volume_stat.find('.//e2ismuted').text
			except AttributeError as e:
				print('Element error: {err}'.format(err=e))
		return (worked, volume_status, mute_status)

	def get_audio_tracks(self):
		request = self.api_handle('getaudiotracks')
		tree = build_tree(request)
		for audio in tree.getiterator('e2audiotrack'):
			e2audiotrackdescription = audio.find('.//e2audiotrackdescription').text
			e2audiotrackid = audio.find('.//e2audiotrackid').text
			e2audiotrackpid = audio.find('.//e2audiotrackpid').text
			e2audiotrackactive = audio.find('.//e2audiotrackactive').text
			print(e2audiotrackdescription, e2audiotrackid, e2audiotrackpid, e2audiotrackactive)

	def recording_list(self):
		movies = []
		request = self.api_handle('movielist')
		tree = build_tree(request)
		for movie in tree.getiterator('e2movie'):
			try:
				movies.append(movie.find('.//e2title').text)
			except AttributeError as e:
				print('Element error: {err}'.format(err=e))
		return movies

	def volume_set(self, volume_level):
		self.api_handle('vol?set=set{0}'.format(volume_level))
		worked, volume_status, mute_status = self.get_audio_status()
		return (worked, volume_status, mute_status)

	def send_key(self, key):
		request = self.api_handle('remotecontrol?command={0}'.format(str(key)))
		tree = build_tree(request)
		for e2about in tree.getiterator('e2remotecontrol'):
			try:
				success = e2about.find('.//e2result').text
				if success:
					print('Accepted key', key)
			except AttributeError as e:
				print('Element error: {err}'.format(err=e))
		return success

	def goto_channel(self, channel):
		for key in str(channel):
			key = int(key) + 1
			self.send_key(key)

	def record_now(self):
		self.api_handle('recordnow')

	def volume_up(self):
		self.send_key('115')

	def volume_down(self):
		self.send_key('114')

	def mute(self):
		self.send_key('113')

	def ok(self):
		self.send_key('352')

	def left(self):
		self.send_key('105')

	def right(self):
		self.send_key('106')

	def up(self):
		self.send_key('103')

	def down(self):
		self.send_key('108')

	def power(self):
		self.send_key('116')

	def previous(self):
		self.send_key('412')

	def next(self):
		self.send_key('407')

	def info(self):
		self.send_key('358')

	def audio(self):
		self.send_key('392')

	def video(self):
		self.send_key('393')

