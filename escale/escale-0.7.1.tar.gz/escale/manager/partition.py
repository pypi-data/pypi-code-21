# -*- coding: utf-8 -*-

# Copyright © 2017, François Laurent

# This file is part of the Escale software available at
# "https://github.com/francoislaurent/escale" and is distributed under
# the terms of the CeCILL-C license as circulated at the following URL
# "http://www.cecill.info/licenses.en.html".

# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL-C license and that you accept its terms.


from .access import *
from collections import defaultdict


class PullCombine(Pull):
	__slots__ = ()
	def __exit__(self, exc_type, exc_value, traceback):
		if exc_type is None:
			self.controller.combine(self.filename)
class SplitPush(Push):
	__slots__ = ()
	def __enter__(self):
		return self.controller.split(self.filename)

class SplitCombine(AccessController):
	def __init__(self, *args, **kwargs):
		self.cache_dir = os.path.expanduser(kwargs.pop('cache_dir', kwargs.pop('cachedir', None)))
		self.min_split_size = kwargs.pop('min_split_size', kwargs.pop('minsplitsize', None))
		AccessController.__init__(self, *args, **kwargs)
		self.parted = defaultdict(list)
		if os.path.isdir(self.cache_dir):
			for filepath in self.listFiles(self.cache_dir):
				dirname, basename = os.path.split(filepath)
				self.parted[dirname].append(basename)
		else:
			os.makedirs(self.cache_dir)
	def confirmPull(self, filename):
		return PullCombine(self, filename)
	def confirmPush(self, filename):
		return SplitPush(self, filename)

