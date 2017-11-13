# -*- coding: utf-8 -*-
from pytdx.reader import (
	TdxFileNotFoundException,
	TdxExHqDailyBarReader, 
	CustomerBlockReader,
	TdxLCMinBarReader,
	TdxDailyBarReader, 
	TdxMinBarReader,
	BlockReader
)
import os

class Reader(object):
	"""docstring for Reader"""

	tdxdir = r'C:/new_tdx'

	def __init__(self, tdxdir=None):
		super(Reader, self).__init__()
		self.tdxdir = tdxdir

	def find_path(self, stock=None, subdir='lday', ext='day'):
		paths = [
			'vipdoc/sz/%s/sz%s.%s' % (subdir, stock, ext),
			'vipdoc/sh/%s/sh%s.%s' % (subdir, stock, ext),
		]
		
		for p in paths:
			path = os.path.join(self.tdxdir, p)
			if os.path.exists(path):
				return path

		return None

	def daily(self, stock=None):
		reader = TdxDailyBarReader()
		stocks = self.find_path(stock)
		return reader.get_df(stocks)

	def minbar(self, stock=None, subdir='minline'):
		stocks = self.find_path(stock, subdir='minline', ext='lc1')
		stocks = self.find_path(stock, subdir='minline', ext='1') if not stocks else stocks
		reader = TdxLCMinBarReader()
		return reader.get_df(stocks)

	def fzline(self, stock=None):
		stocks = self.find_path(stock, subdir='fzline', ext='lc5')
		stocks = self.find_path(stock, subdir='fzline', ext='5') if not stocks else stocks		
		reader = TdxLCMinBarReader()
		return reader.get_df(stocks)

	def block(self, group=False, custom=False):
		reader = BlockReader()
		stocks = os.path.join(self.tdxdir, 'block_zs.dat')
		return reader.get_df(stocks, True)
	
	def index(self, file='incon.dat'):
		reader = BlockReader()
		stocks = os.path.join(self.tdxdir, file)
		return reader.get_df(stocks, True)

class ExReader(Reader):
	"""docstring for ExReader"""

	def ExDaily(stock=None):
		reader = TdxExHqDailyBarReader()
		stocks = self.find_path(stock)
		return reader.get_df(stocks)

		