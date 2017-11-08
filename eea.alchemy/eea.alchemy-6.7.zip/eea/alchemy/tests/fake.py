""" Fake
"""
from zope.interface import implements
from eea.alchemy.discover.api import AlchemyAPI
from eea.alchemy.interfaces import IAlchemyAPI

class FakeAlchemyAPI(AlchemyAPI):
    """ Fake API to be used within tests
    """
    implements(IAlchemyAPI)

    def PostRequest(self, apiCall, apiPrefix, paramObject):
        """ Post request
        """
        template = {
            'entities': [],
            'language': 'english',
            'status': 'FAKE',
            'url': '',
            'usage': ('By accessing AlchemyAPI or using information generated '
                      'by AlchemyAPI, you are agreeing to be bound by the '
                      'AlchemyAPI Terms of Use: '
                      'http://www.alchemyapi.com/company/terms.html')
        }
        text = paramObject.getText()

        # Keywords
        if apiCall == "TextGetRankedKeywords":
            template = {
                'status': 'FAKE',
                'usage': (
                    'By accessing AlchemyAPI or using information generated '
                    'by AlchemyAPI, you are agreeing to be bound by the '
                    'AlchemyAPI Terms of Use: '
                    'http://www.alchemyapi.com/company/terms.html'),
                'keywords': [],
                'url': '',
                'language': 'english'
            }

            if 'new land cover' in text:
                template['keywords'] = [{
                    'relevance': '0.992296', 'text': 'new land cover'
                }]
                return template
            return template

        # Geotags
        if 'Spain' in text:
            template['entities'].append({
                'count': '1',
                'relevance': '0.33',
                'text': 'Spain',
                'type': 'Country'
            })

        if 'Valencia' in text:
            template['entities'].append({
                'count': '1',
                'relevance': '0.33',
                'text': 'Valencia',
                'type': 'City'
            })

        if 'Venice' in text:
            template['entities'].append({
                'count': '1',
                'relevance': '0.33',
                'text': 'Venice',
                'type': 'StateOrCounty'})

        return template.copy()

    GetRequest = PostRequest
