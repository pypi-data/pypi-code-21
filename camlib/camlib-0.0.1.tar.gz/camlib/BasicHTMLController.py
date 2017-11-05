from camlib import HTMLController

class BasicHTMLController (HTMLController.HTMLController):
	def __init__(self, parent):
		self._parent = None
		self._nav = None
		self._parent = parent

	def get_headers(self, style=''):
		title = self.get_meta('title')
		if not title:
			title = 'UNNAMED PAGE'

		style = self.get_style()
		if style:
			style = "<style><!--\n"+style+"\n--></style>\n"

		return """
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<meta name="Author" content=\""""+self.get_meta('author')+"""\"/>
<meta name="Keywords" content=\""""+self.get_meta('keywords')+"""\"/>
<meta name="Description" content=\""""+self.get_meta('description')+"""\"/>
<title>"""+title+"""</title>
"""+style

	def get_meta(self, name):
		try:
			return self._parent.metas[name]
		except KeyError as e:
			return ''

	def get_style(self): return ''
	def get_body(self): return 'Le nom de cette page est '+self._parent._name

	def render(self):
		import codecs, sys
		writer = codecs.getwriter('utf8')(sys.stdout.buffer)
		sys.stdout = codecs.getwriter('utf8')(sys.stdout.buffer)
		print("""Content-Type: text/html

<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C/DTD XHTML 1.1//EN"
                      "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang=\"%s\">
<head>%s</head>
<body>
%s
</body>
</html>
""" % (self.get_meta('lang'), self.get_headers(), self.get_body()))

