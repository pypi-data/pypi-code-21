try:
    from urllib.parse import urljoin
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
except ImportError:
    from urlparse import urljoin
    from urllib2 import urlopen, Request, HTTPError

import json
import inspect
import logging

logging.basicConfig(
    filename = 'pynoaa.log',
    level=logging.DEBUG,
    format='%(asctime)s %(message)s',
)

class PyNOAA:
    def __init__(self, token, api_base = "https://www.ncdc.noaa.gov/cdo-web/api/v2/"):
        self._token = token
        self._api_base = api_base
        logging.info('PyNOAA(%s) initialized' % self._token)

    def _fetch_and_parse(self):
        p_frame = inspect.currentframe().f_back
        path = inspect.getframeinfo(p_frame).function
        _, _, _, values = inspect.getargvalues(p_frame)
        logging.info("%s(%s)" % (path, values))
        values.pop("self", None)
        query = []
        for var, value in values.items():
            if not value:
                continue
            if var == "id":
                path += "/" + value
                continue
            if not (isinstance(value, list) or isinstance(value, set)):
                if not isinstance(value, str):
                    value = str(value)
                value = [value,]
            for occ in value:
                query.append(var + "=" + occ)
        if len(query):
            path += "?" + "&".join(query)
        logging.debug("Create request to: %s" % urljoin(self._api_base, path))
        request = Request(urljoin(self._api_base, path), headers={"token": self._token})
        raw_data = urlopen(request).read().decode('utf-8')
        logging.debug("Got response: %s" % raw_data)
        return json.loads(raw_data)

    def datasets(self,
        id = None,
        datatypeid = None,
        locationid = None,
        stationid = None,
        startdate = None,
        enddate = None,
        sortfield = None,
        sortorder = None,
        limit = None,
        offset = None
    ):
        return self._fetch_and_parse()

    def datacategories(self,
        id = None,
        datasetid = None,
        locationid = None,
        stationid = None,
        startdate = None,
        enddate = None,
        sortfield = None,
        sortorder = None,
        limit = None,
        offset = None
    ):
        return self._fetch_and_parse()

    def datatypes(self,
        id = None,
        datasetid = None,
        locationid = None,
        stationid = None,
        datacategoryid = None,
        startdate = None,
        enddate = None,
        sortfield = None,
        sortorder = None,
        limit = None,
        offset = None
    ):
        return self._fetch_and_parse()

    def locationcategories(self,
        id = None,
        datasetid = None,
        startdate = None,
        enddate = None,
        sortfield = None,
        sortorder = None,
        limit = None,
        offset = None
    ):
        return self._fetch_and_parse()

    def locations(self,
        id = None,
        datasetid = None,
        locationcategoryid = None,
        datacategoryid = None,
        startdate = None,
        enddate = None,
        sortfield = None,
        sortorder = None,
        limit = None,
        offset = None
    ):
        return self._fetch_and_parse()

    def stations(self,
        id = None,
        datasetid = None,
        locationid = None,
        datacategoryid = None,
        datatypeid = None,
        extent = None,
        startdate = None,
        enddate = None,
        sortfield = None,
        sortorder = None,
        limit = None,
        offset = None
    ):
        return self._fetch_and_parse()

    def data(self,
        datasetid = None,
        datatypeid = None,
        locationid = None,
        stationid = None,
        startdate = None,
        enddate = None,
        units = None,
        sortfield = None,
        sortorder = None,
        limit = None,
        offset = None
    ):
        return self._fetch_and_parse()
