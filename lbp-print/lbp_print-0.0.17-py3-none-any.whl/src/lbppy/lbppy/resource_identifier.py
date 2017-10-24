import lbppy
class ResourceIdentifier():
    def __init__(self, url):
        self.url = url
        #self.short_id = url.split("resource/").last

    def to_s(self):
        return self.url

    def resource(self):
        return lbppy.Resource.find(self.url) #need class level method here called "find"
