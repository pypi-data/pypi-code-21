methods = """
document.activeElement	Returns the currently focused element in the document
document.addEventListener()	Attaches an event handler to the document
document.adoptNode()	Adopts a node from another document
document.anchors	Returns a collection of all <a> elements in the document that have a name attribute
document.applets	Returns a collection of all <applet> elements in the document
document.baseURI	Returns the absolute base URI of a document
document.body	Sets or returns the document's body (the <body> element)
document.close()	Closes the output stream previously opened with document.open()
document.cookie	Returns all name/value pairs of cookies in the document
document.charset	Deprecated. Use document.characterSet instead. Returns the character encoding for the document
document.characterSet	Returns the character encoding for the document
document.createAttribute()	Creates an attribute node
document.createComment()	Creates a Comment node with the specified text
document.createDocumentFragment()	Creates an empty DocumentFragment node
document.createElement()	Creates an Element node
document.createTextNode()	Creates a Text node
document.doctype	Returns the Document Type Declaration associated with the document
document.documentElement	Returns the Document Element of the document (the <html> element)
document.documentMode	Returns the mode used by the browser to render the document
document.documentURI	Sets or returns the location of the document
document.domain	Returns the domain name of the server that loaded the document
document.domConfig	Obsolete. Returns the DOM configuration of the document
document.embeds	Returns a collection of all <embed> elements the document
document.forms	Returns a collection of all <form> elements in the document
document.getElementById()	Returns the element that has the ID attribute with the specified value
document.getElementsByClassName()	Returns a NodeList containing all elements with the specified class name
document.getElementsByName()	Returns a NodeList containing all elements with a specified name
document.getElementsByTagName()	Returns a NodeList containing all elements with the specified tag name
document.hasFocus()	Returns a Boolean value indicating whether the document has focus
document.head	Returns the <head> element of the document
document.images	Returns a collection of all <img> elements in the document
document.implementation	Returns the DOMImplementation object that handles this document
document.importNode()	Imports a node from another document
document.inputEncoding	Returns the encoding, character set, used for the document
document.lastModified	Returns the date and time the document was last modified
document.links	Returns a collection of all <a> and <area> elements in the document that have a href attribute
document.normalize()	Removes empty Text nodes, and joins adjacent nodes
document.normalizeDocument()	Removes empty Text nodes, and joins adjacent nodes
document.open()	Opens an HTML output stream to collect output from document.write()
document.querySelector()	Returns the first element that matches a specified CSS selector(s) in the document
document.querySelectorAll()	Returns a static NodeList containing all elements that matches a specified CSS selector(s) in the document
document.readyState	Returns the (loading) status of the document
document.referrer	Returns the URL of the document that loaded the current document
document.removeEventListener()	Removes an event handler from the document (that has been attached with the addEventListener() method)
document.renameNode()	Renames the specified node
document.scripts	Returns a collection of <script> elements in the document
document.strictErrorChecking	Sets or returns whether error-checking is enforced or not
document.title	Sets or returns the title of the document
document.URL	Returns the full URL of the HTML document
document.write()	Writes HTML expressions or JavaScript code to a document
document.writeln()	Same as write(), but adds a newline character after each statement
"""

print('class document:')
print(end='\t')

print(*[f"def {left.replace('document.', '').replace('()', '')}(self): \n\t\t'''{right}'''" for elm in methods.split('\n')[1:-1] for left, right in [elm.split('\t')]], sep='\n\t')

class document:
	def activeElement(self):
		'''Returns the currently focused element in the document'''
	def addEventListener(self):
		'''Attaches an event handler to the document'''
	def adoptNode(self):
		'''Adopts a node from another document'''
	def anchors(self):
		'''Returns a collection of all <a> elements in the document that have a name attribute'''
	def applets(self):
		'''Returns a collection of all <applet> elements in the document'''
	def baseURI(self):
		'''Returns the absolute base URI of a document'''
	def body(self):
		'''Sets or returns the document's body (the <body> element)'''
	def close(self):
		'''Closes the output stream previously opened with document.open()'''
	def cookie(self):
		'''Returns all name/value pairs of cookies in the document'''
	def charset(self):
		'''Deprecated. Use document.characterSet instead. Returns the character encoding for the document'''
	def characterSet(self):
		'''Returns the character encoding for the document'''
	def createAttribute(self):
		'''Creates an attribute node'''
	def createComment(self):
		'''Creates a Comment node with the specified text'''
	def createDocumentFragment(self):
		'''Creates an empty DocumentFragment node'''
	def createElement(self):
		'''Creates an Element node'''
	def createTextNode(self):
		'''Creates a Text node'''
	def doctype(self):
		'''Returns the Document Type Declaration associated with the document'''
	def documentElement(self):
		'''Returns the Document Element of the document (the <html> element)'''
	def documentMode(self):
		'''Returns the mode used by the browser to render the document'''
	def documentURI(self):
		'''Sets or returns the location of the document'''
	def domain(self):
		'''Returns the domain name of the server that loaded the document'''
	def domConfig(self):
		'''Obsolete. Returns the DOM configuration of the document'''
	def embeds(self):
		'''Returns a collection of all <embed> elements the document'''
	def forms(self):
		'''Returns a collection of all <form> elements in the document'''
	def getElementById(self):
		'''Returns the element that has the ID attribute with the specified value'''
	def getElementsByClassName(self):
		'''Returns a NodeList containing all elements with the specified class name'''
	def getElementsByName(self):
		'''Returns a NodeList containing all elements with a specified name'''
	def getElementsByTagName(self):
		'''Returns a NodeList containing all elements with the specified tag name'''
	def hasFocus(self):
		'''Returns a Boolean value indicating whether the document has focus'''
	def head(self):
		'''Returns the <head> element of the document'''
	def images(self):
		'''Returns a collection of all <img> elements in the document'''
	def implementation(self):
		'''Returns the DOMImplementation object that handles this document'''
	def importNode(self):
		'''Imports a node from another document'''
	def inputEncoding(self):
		'''Returns the encoding, character set, used for the document'''
	def lastModified(self):
		'''Returns the date and time the document was last modified'''
	def links(self):
		'''Returns a collection of all <a> and <area> elements in the document that have a href attribute'''
	def normalize(self):
		'''Removes empty Text nodes, and joins adjacent nodes'''
	def normalizeDocument(self):
		'''Removes empty Text nodes, and joins adjacent nodes'''
	def open(self):
		'''Opens an HTML output stream to collect output from document.write()'''
	def querySelector(self):
		'''Returns the first element that matches a specified CSS selector(s) in the document'''
	def querySelectorAll(self):
		'''Returns a static NodeList containing all elements that matches a specified CSS selector(s) in the document'''
	def readyState(self):
		'''Returns the (loading) status of the document'''
	def referrer(self):
		'''Returns the URL of the document that loaded the current document'''
	def removeEventListener(self):
		'''Removes an event handler from the document (that has been attached with the addEventListener() method)'''
	def renameNode(self):
		'''Renames the specified node'''
	def scripts(self):
		'''Returns a collection of <script> elements in the document'''
	def strictErrorChecking(self):
		'''Sets or returns whether error-checking is enforced or not'''
	def title(self):
		'''Sets or returns the title of the document'''
	def URL(self):
		'''Returns the full URL of the HTML document'''
	def write(self):
		'''Writes HTML expressions or JavaScript code to a document'''
	def writeln(self):
		'''Same as write(), but adds a newline character after each statement'''