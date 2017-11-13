# -*- coding: utf-8 -*-
from pytdx.hq import TdxHq_API
from pytdx.exhq import TdxExHq_API

class LiveBars(object):
	"""docstring for LiveReader"""
	client = None

	def __init__(self, arg):
		super(LiveReader, self).__init__()
		self.client = TdxHq_API(auto_retry=True)
		self.client.connect()

	def __del__(self):
		self.client.disconnect()

	def bars(self, symbol=''):
		data = self.client.get_security_bars(9, 0, symbol, 0, 10)
		return self.client.to_df(data)

	def index(self, file='incon.dat'):
		pass

	def count(self):
		pass

	def symbol(self):
		pass

class ExLiveBars(LiveBars):
	"""docstring for ExLiveReader"""
	def __init__(self, arg):
		super(ExLiveBars, self).__init__()
		self.client = TdxExHq_API(auto_retry=True)
		self.client.connect()

	def bars(self, symbol=''):
		data = self.client.get_security_bars(9, 0, symbol, 0, 10)
		return self.client.to_df(data)
		