from .libs import SearcherGene

class DuckDuckGo(SearcherGene):

    def set(self):
        self.method ='post'
        self.url = 'https://duckduckgo.com/html/'
        self.params = {
            'q': 'xxx',
            's': '0',
        }
        self.res_css = '#links .links_main'



