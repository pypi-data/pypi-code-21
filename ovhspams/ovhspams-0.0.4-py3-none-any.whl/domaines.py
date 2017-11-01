import sys

# general configuration: default endpoint
endpoint="ovh-eu"

# aller sur https://api.ovh.com/

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

def get_dom_lst():
	ret = []
	for d in domaines:
		ret.append(d['dom'])
	return ret

class Domaine:

	def __init__(self, dom, print_err=False):

		self.dom = dom
		found = False
		self.errmsg = ''
		for d in domaines:
			if d['dom'] == self.dom:
				self.ds = d
				found = True
				break
		if not found:
			self.errmsg = 'Domaine non trouvé'
			if print_err:
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

	
