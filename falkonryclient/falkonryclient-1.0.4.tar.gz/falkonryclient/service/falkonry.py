"""
Falkonry Client

Client to access Condition Prediction APIs

:copyright: (c) 2016 by Falkonry Inc.
:license: MIT, see LICENSE for more details.

"""

from falkonryclient.helper import schema as Schemas
from falkonryclient.service.http import HttpService
from falkonryclient.helper import utils as Utils
from cStringIO import StringIO
import json
import sseclient
import urllib

"""
FalkonryService
    Service class to link js client to Falkonry API server
"""


class FalkonryService:

    def __init__(self, host, token, options):
        """
        constructor
        :param host: host address of Falkonry service
        :param token: Authorization token
        """
        self.host  = host
        self.token = token
        self.http  = HttpService(host, token, options)

    def get_datastreams(self):
        """
        To get list of Datastream
        """
        datastreams = []
        response = self.http.get('/Datastream')
        for datastream in response:
            datastreams.append(Schemas.Datastream(datastream=datastream))
        return datastreams

    def get_datastream(self, datastream):
        """
        To get Datastream by id
        """
        response = self.http.get('/Datastream/' + str(datastream))
        datastream = Schemas.Datastream(datastream=response)
        return datastream

    def create_datastream(self, datastream):
        """
        To create Datastream
        :param datastream: Datastream
        :param options: dict
        """
        raw_datastream = self.http.post('/Datastream', datastream)
        return Schemas.Datastream(datastream=raw_datastream)

    def delete_datastream(self, datastream):
        """
        To delete a Datastream
        :param datastream: string
        """
        response = self.http.delete('/Datastream/' + str(datastream))
        return response

    def get_assessments(self):
        """
        To get list of Assessments
        """
        assessments = []
        response = self.http.get('/Assessment')
        for assessment in response:
            assessments.append(Schemas.Assessment(assessment=assessment))
        return assessments

    def get_assessment(self, assessment):
        """
        To get Assessment by id
        """
        response = self.http.get('/Assessment/' + str(assessment))
        assessment = Schemas.Assessment(assessment=response)
        return assessment

    def create_assessment(self, assessment):
        """
        To create Assessment
        :param assessment: Assessment
        """
        raw_assessment = self.http.post('/Assessment', assessment)
        return Schemas.Assessment(assessment=raw_assessment)

    def delete_assessment(self, assessment):
        """
        To delete a Assessment
        :param assessment: string
        """
        response = self.http.delete('/Assessment/' + str(assessment))
        return response

    def add_input_data(self, datastream, data_type, options, data):
        """
        To add data to a Datastream
        :param datastream: string
        :param data_type: string
        :param options: dict
        :param data: string
        """

        if 'streaming' in options and options['streaming'] is True:
            streaming = 'true'
        else:
            streaming = 'false'

        if 'hasMoreData' in options and options['hasMoreData'] is True:
            hasMoreData = 'true'
        else:
            hasMoreData = 'false'


        url = '/Datastream/' + str(datastream) + '?streaming=' + streaming + '&hasMoreData=' + hasMoreData
        form_data = {
            'files': {
                'data': (
                    Utils.random_string(10)+('.json' if data_type == 'json' else '.csv'),
                    StringIO(data),
                    'text/plain;charset=UTF-8',
                    {'Expires': '0'}
                )
            }
        }
        response = self.http.fpost(url, form_data)
        return response

    def add_facts(self, assessment, data_type, options, data):
        """
        To add facts data to a Assessment
        :param assessment: string
        :param data_type: string
        :param options: dict
        :param data: string
        """

        url = self.get_fact_url(assessment,options)
        try:
            response = self.http.postData(url, data)
        except Exception as e:
            print e.message
        return response


    def add_input_stream(self, datastream, data_type, options, data):
        """
        To add data stream to a Datastream
        :param datastream: string
        :param data_type: string
        :param options: dict
        :param data: Stream
        """

        if 'streaming' in options and options['streaming'] is True:
            streaming = 'true'
        else:
            streaming = 'false'

        if 'hasMoreData' in options and options['hasMoreData'] is True:
            hasMoreData = 'true'
        else:
            hasMoreData = 'false'


        url = '/Datastream/' + str(datastream) + '?streaming=' + streaming + '&hasMoreData=' + hasMoreData
        form_data = {
            'files': {
                'data': (
                    Utils.random_string(10)+('.json' if data_type == 'json' else '.csv'),
                    data,
                    'text/plain;charset=UTF-8',
                    {'Expires': '0'}
                )
            }
        }
        response = self.http.upstream(url, form_data)
        return response

    def add_facts_stream(self, assessment, data_type, options, data):
        """
        To add  facts data stream to a Assessment
        :param datastream: string
        :param data_type: string
        :param options: dict
        :param data: Stream
        """

        url = self.get_fact_url(assessment,options)

        form_data = {
            'files': {
                'data': (
                    Utils.random_string(10)+('.json' if data_type == 'json' else '.csv'),
                    data,
                    'text/plain;charset=UTF-8',
                    {'Expires': '0'}
                )
            }
        }
        response = self.http.upstream(url,form_data)
        return response

    def get_fact_url(self, assessment, options):
        firstReqParam = True

        url = '/assessment/' + assessment + '/facts?'

        if 'startTimeIdentifier' in options:
            if firstReqParam:
                firstReqParam = False
            else:
                url += "&"
            url += "startTimeIdentifier=" + str(options['startTimeIdentifier'])

        if 'endTimeIdentifier' in options:
            if firstReqParam:
                firstReqParam = False
            else:
                url += "&"
            url += "endTimeIdentifier=" + str(options['endTimeIdentifier'])

        if 'timeFormat' in options:
            if firstReqParam:
                firstReqParam = False
            else:
                url += "&"
            url += "timeFormat=" + str(options['timeFormat'])

        if 'timeZone' in options:
            if firstReqParam:
                firstReqParam = False
            else:
                url += "&"
            url += "timeZone=" + str(options['timeZone'])

        if 'entityIdentifier' in options:
            if firstReqParam:
                firstReqParam = False
            else:
                url += "&"
            url += "entityIdentifier=" + str(options['entityIdentifier'])

        if 'valueIdentifier' in options:
            if firstReqParam:
                firstReqParam = False
            else:
                url += "&"
            url += "valueIdentifier=" + str(options['valueIdentifier'])

        if 'tagIdentifier' in options:
            if firstReqParam:
                firstReqParam = False
            else:
                url += "&"
            url += "tagIdentifier=" + str(options['tagIdentifier'])

        if 'additionalTag' in options:
            if firstReqParam:
                firstReqParam = False
            else:
                url += "&"
            url += "additionalTag=" + str(options['additionalTag'])
        return url

    def get_output(self, assessment, options):
        """
        To get output of a Assessment
        :param assessment: string
        """
        responseFormat=None
        if options and 'format' in options and options['format'] is not None:
            responseFormat = options['format']
            options['format'] = None

        url = '/assessment/' + str(assessment) + '/output'
        response = self.http.downstream(url, responseFormat)
        stream = sseclient.SSEClient(response)
        return stream

    def get_historical_output(self, assessment, options):
        """
        To get output of a historical Assessment
        :param assessment: string
        :param options: dict
        """
        responseFormat=None
        if options and 'format' in options and options['format'] is not None:
            responseFormat = options['format']
            options['format'] = None

        url = '/assessment/' + str(assessment) + '/output?' + urllib.urlencode(options)
        response = self.http.downstream(url, responseFormat)
        return response

    def add_entity_meta(self, datastream, options, data):
        """
        To add entity meta data to a datastream
        :param datastream: string
        :param options: dict
        :param data: list
        """
        url = '/datastream/' + str(datastream) + '/entityMeta'
        response = self.http.post(url, data)
        entityMetaList = []
        for entityMeta in response:
            entityMetaList.append(Schemas.EntityMeta(entityMeta=entityMeta))
        return entityMetaList

    def get_entity_meta(self, datastream):
        """
        To add entity meta data to a datastream
        :param datastream: string
        :param options: dict
        """
        url = '/datastream/' + str(datastream) + '/entityMeta'
        response = self.http.get(url)
        entityMetaList = []
        for entityMeta in response:
            entityMetaList.append(Schemas.EntityMeta(entityMeta=entityMeta))
        return entityMetaList

    def on_datastream(self, datastream):
        """
        To turn on datastream
        :param datastream: string
        """
        url = '/datastream/' + str(datastream) + '/on'
        response = self.http.post(url,"")
        return response

    def off_datastream(self, datastream):
        """
        To turn off datastream
        :param datastream: string
        """
        url = '/datastream/' + str(datastream) + '/off'
        response = self.http.post(url,"")
        return response

    def get_facts(self, assessment, options):
        """
        Get facts data for the assessment
        :param assessment: string
        :param options: dict
        """

        response_format=None
        if options and 'format' in options and options['format'] is not None:
            response_format = options['format']
            options['format'] = None

        url = '/assessment/' + str(assessment) + '/facts?' + urllib.urlencode(options)
        response = self.http.downstream(url, response_format)
        return response

    def get_datastream_data(self, datastream, options):
        """
        Get input data for the datastream
        :param datastream: string
        :param options: dict
        """

        response_format=None
        if options and 'format' in options and options['format'] is not None:
            response_format = options['format']
            options['format'] = None

        url = '/datastream/' + str(datastream) + '/data'
        response = self.http.downstream(url, response_format)
        return response

