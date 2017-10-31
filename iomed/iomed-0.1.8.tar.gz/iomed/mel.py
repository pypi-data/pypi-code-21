# -*- coding: utf-8 -*-

import requests
import json

class MEL:
    """
    Simple interface to IOMED's Medical Language API.
    
    Example:

    mel = MEL('you-api-key')
    text = 'refiere dolor en el pecho desde hace tres días'
    results = mel.parse(text)

    Visit https://docs.iomed.es for more information on the API.
    """
    def __init__(self, apikey, test=False, url=None):
        """
        Args:
            apikey (str): api key, get it from https://console.iomed.es.
            test (boolean): whether to use the testing platform instead of production.
        """
        self.__apikey = apikey
        self.__host = 'test.iomed.es' if test else 'api.iomed.es'
        self.__url = url if url else 'https://{}/tagger/annotation'.format(self.__host)

    def parse(self, text, as_json=False):
        """
        Parse a text to find medical concepts. Returns either a dictionary or a json
        string.

        Args:
            text (str): text to be processed. Keep into account there are length
                        limits: http://docs.iomed.es/pricing/#limits
            as_json (boolean): whether to return a json string, instead of the parsed
                            response from the API.
        Returns:
            A dictionary with entries "version" (version of the IOMED MEL API), and
            "annotations". "annotations" contains a list of medical concepts.
            Learn more at http://docs.iomed.es/api_usage/find_concepts/.
        """
        data = {"text": text}
        headers = {
          'apikey': self.__apikey,
          'X-Consumer-ID': 'iomed-cli',
          'Access-Method': 'iomed-cli'        
        }
        response = requests.post(self.__url, json=data, headers=headers)
        body = response.content.decode('utf-8')
        if as_json:
            return body
        return json.loads(body)
