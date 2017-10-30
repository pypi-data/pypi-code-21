import lbppy
import urllib

class FilePart():
    def __init__(self, file_path, transcription_type, confighash, partid):
        self.partid = partid
        self.file_path = file_path
        self.confighash = confighash

        if (self.confighash != None):
            self.stylesheets = self.confighash["stylesheets"]

        self.transcription_type = transcription_type
        
        #if (self.confighash != nil):
        #	self.xslt_dir = "#{@confighash[:xslt_base]}#{@xslt_version}/#{@transcription_type}/"
