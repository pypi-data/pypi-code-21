import sys

import pdb

# general configuration: default endpoint
endpoint="ovh-eu"

class Domaine:

	def __init__(self, doms, print_err=False):
		""" Initialisation avec une liste de domaines.
			La structure est : 
			domaines = [
				{'dom': 'dom1.fr',
					'appkey': 'xxxxxxxxxxxxxxxx',
					'secret': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
					'cuskey': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'},
				
				{'dom': 'dom2.fr',
					'appkey': 'xxxxxxxxxxxxxxxx',
					'secret': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
					'cuskey': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'},
			]
		"""
		self.doms = doms
		self.print_err = print_err
		#pdb.set_trace()

	def get_dom_lst(self):
		""" Retourne une liste avec les libellés des domaines
		"""
		ret = []
		for d in self.doms:
			ret.append(d['dom'])
		return ret

	def set_dom(self, dom):
		""" recherche et active un domaine
		"""
		self.dom = dom
		found = False
		self.errmsg = ''
		for d in self.doms:
			if d['dom'] == self.dom:
				self.ds = d
				found = True
				break
		if not found:
			self.errmsg = 'Domaine non trouvé'
			if self.print_err:
				print (self.errmsg)
				sys.exit(1)

	def have_error(self):
		if self.errmsg == '':
			return False
		return True

	def get_error(self):
		return self.errmsg

	def get_dm(self):
		return self.dom

	def get_ep(self):
		return endpoint

	def get_ak(self):
		return self.ds['appkey']

	def get_sc(self):
		return self.ds['secret']

	def get_ck(self):
		return self.ds['cuskey']

	
