from delune.searcher import document
from delune.lib import unistr

class LabeledDocument (document.Document):
	def __init__ (self, label, text, lang = "un", encoding = None):
		self.fields = {}
		self.label = unistr.makes (label)
		self.text = unistr.makes (text, encoding)
		self.lang = lang
	
	def add_field (self, name, value, ftype = "Text", lang = "un", encoding = None, option = {}):
		if name in ("label", "default"):
			raise NameError("Field Name `label' or `default' is not allowed")
		document.Document.add_field (self, name, value, ftype, option, encoding, lang)

