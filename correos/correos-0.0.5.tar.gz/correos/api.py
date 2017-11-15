#This file is part of correos. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from correos.utils import correos_url
from xml.dom.minidom import parseString
import urllib2
import ssl
import base64
import os
import socket
import datetime
import genshi
import genshi.template

loader = genshi.template.TemplateLoader(
    os.path.join(os.path.dirname(__file__), 'template'),
    auto_reload=True)


class API(object):
    """
    Generic API to connect to correos
    """
    __slots__ = (
        'url',
        'username',
        'password',
        'code',
        'timeout',
    )

    def __init__(self, username, password, code, timeout=None, debug=False):
        """
        This is the Base API class which other APIs have to subclass. By
        default the inherited classes also get the properties of this
        class which will allow the use of the API with the `with` statement

        Example usage ::

            from correos.api import API

            with API(username, password, code) as correos_api:
                return correos_api.test_connection()

        :param username: Correos API username
        :param password: Correos API password
        :param code: Correos API CodeEtiquetador
        :param timeout: int number of seconds to lost connection.
        """
        self.url = correos_url(debug)
        self.username = username
        self.password = password
        self.code = code
        self.timeout = timeout

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return self

    def connect(self, xml, action):
        """
        Connect to the Webservices and return XML data from correos

        :param xml: XML data.

        Return XML object
        """
        if not action:
            return

        base64string = base64.encodestring('%s:%s' % (
            self.username, self.password))[:-1]

        headers = {
            'Content-Type': 'application/soap+xml; charset=utf-8',
            'Content-Type': 'text/xml; charset=utf-8',
            'Content-Length': len(xml),
            'SOAPAction': '%s' % action,
            'Authorization': 'Basic %s' % base64string
            }
        request = urllib2.Request(self.url, xml, headers)
        try:
            response = urllib2.urlopen(request, timeout=self.timeout,
                    context=ssl._create_unverified_context())
            return response.read()
        except socket.timeout as err:
            return
        except socket.error as err:
            return

    def test_connection(self):
        """
        Test connection to Correos webservices
        Send XML to Correos and return error send data
        """
        tmpl = loader.load('test_connection.xml')

        self.url = 'https://preregistroenviospre.correos.es/preregistroenvios'
        vals = {
            'now': datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }

        xml = tmpl.generate(**vals).render()
        result = self.connect(xml, 'Preregistro')
        if not result:
            return 'Error connection to Correos'
        dom = parseString(result)

        CodEnvio = dom.getElementsByTagName('CodEnvio')
        reference = CodEnvio[0].firstChild.data

        Resultado = dom.getElementsByTagName('Resultado')
        result = Resultado[0].firstChild.data

        if result == '0':
            return 'Succesfully delivery test sended to Correos with tracking "%s"' % (reference)
        return 'Error send a delivery test to Correos: %s' % (reference)

    def oficinas(self, zip):
        """
        Oficinas Correos
        """
        tmpl = loader.load('oficinas.xml')

        url = 'http://localizadoroficinas.correos.es/localizadoroficinas'
        vals = {
            'zip': zip,
            }

        xml = tmpl.generate(**vals).render()

        headers = {
            'Content-Type': 'application/soap+xml; charset=utf-8',
            'Content-Type': 'text/xml; charset=utf-8',
            'Content-Length': len(xml),
            }
        request = urllib2.Request(url, xml, headers)
        try:
            response = urllib2.urlopen(request, timeout=self.timeout,
                    context=ssl._create_unverified_context())
        except:
            return
        result = response.read()
        dom = parseString(result)

        oficinas = []
        for item in dom.getElementsByTagName('item'):
            oficinas.append({
                'code': item.getElementsByTagName('ns-980841924:unidad')[0].firstChild.data,
                'name': item.getElementsByTagName('ns-980841924:nombre')[0].firstChild.data,
                'address': item.getElementsByTagName('ns-980841924:direccion')[0].firstChild.data,
                'zip': item.getElementsByTagName('ns-980841924:cp')[0].firstChild.data,
                'code_city': item.getElementsByTagName('ns-980841924:codLocalidad')[0].firstChild.data,
                'city': item.getElementsByTagName('ns-980841924:descLocalidad')[0].firstChild.data,
                'phone': item.getElementsByTagName('ns-980841924:telefono')[0].firstChild.data,
                'timetable': 'LV: %s - S: %s' % (
                    item.getElementsByTagName('ns-980841924:horarioLV')[0].firstChild.data,
                    item.getElementsByTagName('ns-980841924:horarioS')[0].firstChild.data,
                    ),
                })
        return oficinas
