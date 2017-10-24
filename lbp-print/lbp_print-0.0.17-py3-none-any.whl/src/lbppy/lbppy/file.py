import lbppy
import urllib
from lxml import etree

class File():
    def __init__(self, file_path, transcription_type, confighash):
        self.file_path = file_path
        self.confighash = confighash
        if (self.confighash != None):
            self.stylesheets = self.confighash["stylesheets"]

        self.transcription = transcription_type
        #if (self.confighash != nil):
        #	self.xslt_dir = "#{@confighash[:xslt_base]}#{@xslt_version}/#{@transcription_type}/"

    def file(self):
        response = urllib.request.urlopen(self.file_path)
        # this conditional is needed for private repos requring basic auth
        #if (response.base_uri.to_s != self.file_path):
            #response = urllib.request.urlopen(self.file_path, {:http_basic_authentication => [self.confighash["git_username"], self.confighash["git_password"] ]})
        return response
    def lxmldoc(self):
        doc = etree.parse(self.file())
        return doc
    def validating_schema_version(self):
        result = self.lxmldoc().xpath("/tei:TEI/tei:teiHeader[1]/tei:encodingDesc[1]/tei:schemaRef[1]/@n", namespaces={"tei": "http://www.tei-c.org/ns/1.0"})
        if (len(result) > 0):
            return result[0].split("-").pop()
        else:
            return "default"

    def title(self):
        xmldoc = self.lxmldoc()
        title = xmldoc.xpath("/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title", namespaces={"tei": "http://www.tei-c.org/ns/1.0"})
        return title[0].text

    def author(self):
        xmldoc = self.lxmldoc()
        author = xmldoc.xpath("/tei:TEI/tei:teiHeader[1]/tei:fileDesc/tei:titleStmt[1]/tei:author", namespaces={"tei": "http://www.tei-c.org/ns/1.0"})
        return author[0].text

    def editor(self):
        xmldoc = self.lxmldoc()
        editor = xmldoc.xpath("/tei:TEI/tei:teiHeader[1]/tei:fileDesc/tei:titleStmt[1]/tei:editor", namespaces={"tei": "http://www.tei-c.org/ns/1.0"})
        return editor[0].text

# begin transform methods
    def transform(self, xslturl):
        raw = urllib.request.urlopen(xslturl)
        xsltdoc = etree.parse(raw)
        xmldoc = self.lxmldoc()
        result = xmldoc.xslt(xsltdoc)
        return result
