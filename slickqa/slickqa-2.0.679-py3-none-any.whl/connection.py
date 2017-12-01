"""
slick.py is a library for talking to slick (http://code.google.com/p/slickqa).

Copyright 2013 AccessData Group, LLC.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
__author__ = 'Jason Corbett'

import requests
import logging
import sys
import traceback
import pprint

try:
    from urllib.parse import urlencode, quote
except ImportError:
    from urllib import urlencode, quote

from .micromodels import Model
from .data import *
from . import queries

import os
import mimetypes
import hashlib

if not mimetypes.inited:
    mimetypes.init()
mimetypes.add_type('text/plain', '.log')

json_content = {'Content-Type': 'application/json'}
STREAM_CONTENT = {'Content-Type': 'application/octet-stream'}


class FindOneModeEnum(object):
    """

    """
    FIRST = 1
    LAST = 2

    def __getattr__(self, name):
        if name in FindOneModeEnum.__dict__:
            return FindOneModeEnum.__dict__[name]
        raise AttributeError


FindOneMode = FindOneModeEnum()


class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


def obj_hook_attr_dict(dct):
    return AttributeDict(dct)


class SlickApiPart(object):
    """A class representing part of the slick api"""

    def __init__(self, model, parentPart, name=None):
        self.model = model
        if name is None:
            self.name = model.__name__.lower() + "s"
        else:
            self.name = name

        self.parent = parentPart
        self.logger = logging.getLogger(name=self.get_name())
        self.data = None

    def get_name(self):
        return self.parent.get_name() + "." + self.name

    def find(self, query=None, **kwargs):
        """
        You can pass in the appropriate model object from the queries module,
        or a dictionary with the keys and values for the query,
        or a set of key=value parameters.
        """
        url = self.getUrl()
        if query is not None:
            if isinstance(query, queries.SlickQuery):
                url = url + "?" + urlencode(query.to_dict())
            elif isinstance(query, dict):
                url = url + "?" + urlencode(query)
        elif len(kwargs) > 0:
            url = url + "?" + urlencode(kwargs)

        # hopefully when we discover what problems exist in slick to require this, we can take the loop out
        for retry in range(3):
            try:
                self.logger.debug("Making request to slick at url %s", url)
                r = requests.get(url)
                self.logger.debug("Request returned status code %d", r.status_code)
                if r.status_code is 200:
                    retval = []
                    objects = r.json()
                    for dct in objects:
                        retval.append(self.model.from_dict(dct))
                    return retval
                else:
                    self.logger.error("Slick returned an error when trying to access %s: status code %s" % (url, str(r.status_code)))
                    self.logger.error("Slick response: ", pprint.pformat(r))
                    
            except BaseException as error:
                self.logger.warn("Received exception while connecting to slick at %s", url, exc_info=sys.exc_info())
        raise SlickCommunicationError(
            "Tried 3 times to request data from slick at url %s without a successful status code.", url)

    query = find

    def findOne(self, query=None, mode=FindOneMode.FIRST, **kwargs):
        """
        Perform a find, with the same options present, but only return a maximum of one result.  If find returns
        an empty array, then None is returned.

        If there are multiple results from find, the one returned depends on the mode parameter.  If mode is
        FindOneMode.FIRST, then the first result is returned.  If the mode is FindOneMode.LAST, then the last is
        returned.  If the mode is FindOneMode.ERROR, then a SlickCommunicationError is raised.
        """
        results = self.find(query, **kwargs)
        if len(results) is 0:
            return None
        elif len(results) is 1 or mode == FindOneMode.FIRST:
            return results[0]
        elif mode == FindOneMode.LAST:
            return results[-1]

    def get(self):
        """Get the specified object from slick.  You specify which one you want by providing the id as a parameter to
        the parent object.  Example:
        slick.projects("4fd8cd95e4b0ee7ba54b9885").get()
        """
        url = self.getUrl()

        # hopefully when we discover what problems exist in slick to require this, we can take the loop out
        for retry in range(3):
            try:
                self.logger.debug("Making request to slick at url %s", url)
                r = requests.get(url)
                self.logger.debug("Request returned status code %d", r.status_code)
                if r.status_code is 200:
                    return self.model.from_dict(r.json())
                else:
                    self.logger.debug("Body of what slick returned: %s", r.text)
            except BaseException as error:
                self.logger.warn("Received exception while connecting to slick at %s", url, exc_info=sys.exc_info())
        raise SlickCommunicationError(
            "Tried 3 times to request data from slick at url %s without a successful status code.", url)

    def update(self):
        """Update the specified object from slick.  You specify the object as a parameter, using the parent object as
        a function.  Example:
        proj = slick.projects.findByName("foo")
        ... update proj here
        slick.projects(proj).update()
        """
        obj = self.data
        url = self.getUrl()

        # hopefully when we discover what problems exist in slick to require this, we can take the loop out
        last_stats_code = None
        last_body = None
        for retry in range(3):
            try:
                json_data = obj.to_json()
                self.logger.debug("Making request to slick at url %s, with data: %s", url, json_data)
                r = requests.put(url, data=json_data, headers=json_content)
                self.logger.debug("Request returned status code %d", r.status_code)
                if r.status_code is 200:
                    return self.model.from_dict(r.json())
                else:
                    last_stats_code = r.status_code
                    last_body = r.text
                    self.logger.warn("Slick status code: %d", r.status_code)
                    self.logger.warn("Body of what slick returned: %s", r.text)
            except BaseException as error:
                self.logger.warn("Received exception while connecting to slick at %s", url, exc_info=sys.exc_info())
                traceback.print_exc()
        raise SlickCommunicationError(
            "Tried 3 times to request data from slick at url %s without a successful status code.  Last status code: %d, body: %s", url, last_stats_code, last_body)

    put = update

    def create(self):
        """Create the specified object (perform a POST to the api).  You specify the object as a parameter, using
        the parent object as a function.  Example:
        proj = Project()
        ... add project data here
        proj = slick.projects(proj).create()
        """
        obj = self.data
        self.data = None
        url = self.getUrl()

        # hopefully when we discover what problems exist in slick to require this, we can take the loop out
        for retry in range(3):
            try:
                json_data = obj.to_json()
                self.logger.debug("Making request to slick at url %s, with data: %s", url, json_data)
                r = requests.post(url, data=json_data, headers=json_content)
                self.logger.debug("Request returned status code %d", r.status_code)
                if r.status_code is 200:
                    return self.model.from_dict(r.json())
                else:
                    self.logger.debug("Body of what slick returned: %s", r.text)
            except BaseException as error:
                self.logger.warn("Received exception while connecting to slick at %s", url, exc_info=sys.exc_info())
        raise SlickCommunicationError(
            "Tried 3 times to request data from slick at url %s without a successful status code.", url)

    post = create

    def remove(self):
        """Remove or delete the specified object from slick.  You specify which one you want by providing the id as
        a parameter to the parent object, using it as a function.  Example:
        slick.projects("4fd8cd95e4b0ee7ba54b9885").remove()
        """
        url = self.getUrl()

        # hopefully when we discover what problems exist in slick to require this, we can take the loop out
        for retry in range(3):
            try:
                self.logger.debug("Making DELETE request to slick at url %s", url)
                r = requests.delete(url)
                self.logger.debug("Request returned status code %d", r.status_code)
                if r.status_code is 200:
                    return None
                else:
                    self.logger.debug("Body of what slick returned: %s", r.text)
            except BaseException as error:
                self.logger.warn("Received exception while connecting to slick at %s", url, exc_info=sys.exc_info())
        raise SlickCommunicationError(
            "Tried 3 times to request data from slick at url %s without a successful status code.", url)

    delete = remove

    def getUrl(self):
        url = self.parent.getUrl() + "/" + self.name
        if self.data is not None:
            if isinstance(self.data, Model) and hasattr(self.data, 'id'):
                url = url + "/" + self.data.id
            else:
                url = url + "/" + str(self.data)
            self.data = None
        return url

    def __call__(self, *args, **kwargs):
        if len(args) > 0:
            self.data = args[0]
        return self


class SlickProjectApiPart(SlickApiPart):
    def __init__(self, parentPart):
        super(SlickProjectApiPart, self).__init__(Project, parentPart)

    def findByName(self, name):
        """Find a project by it's name"""
        self.data = "byname/" + quote(name)
        return self.get()


class SystemConfigurationApiPart(SlickApiPart):
    """
    The system-configuration api is different from other apis.  The model for the return type is variable due to it
    being able to store different instances of system configuration classes.
    """

    def __init__(self, parentPart):
        super(SystemConfigurationApiPart, self).__init__(SystemConfiguration, parentPart, 'system-configuration')

    def __call__(self, model, data=None):
        """Make a request for system-configuration, but you not only need to provide the data, but the model that is
        needed for return type.
        """
        self.model = model
        if data is not None:
            return super(SystemConfigurationApiPart, self).__call__(data)
        else:
            return self

    def find(self, query=None, **kwargs):
        instance = self.model()
        if hasattr(instance, 'configurationType') and instance.configurationType is not None:
            kwargs['config-type'] = instance.configurationType
        return super(SystemConfigurationApiPart, self).find(query, **kwargs)

def upload_chunks(url, stored_file, file_like_obj):
    md5 = hashlib.md5()
    bindata = file_like_obj.read(stored_file.chunkSize)
    while bindata:
        if isinstance(bindata, bytes):
            md5.update(bindata)
        elif isinstance(bindata, str):
            md5.update(bindata.encode('ascii', 'ignore'))
        requests.post(url, data=bindata, headers={'Content-Type': 'application/octet-stream'})
        bindata = file_like_obj.read(stored_file.chunkSize)
    stored_file.md5 = md5.hexdigest()

class StoredFileApiPart(SlickApiPart):

    def __init__(self, parentPart):
        super(StoredFileApiPart, self).__init__(StoredFile, parentPart, "files")

    def upload_local_file(self, local_file_path, file_obj=None):
        """Create a Stored File and upload it's data.  This is a one part do it all type method.  Here is what
        it does:
            1. "Discover" information about the file (mime-type, size)
            2. Create the stored file object in slick
            3. Upload (chunked) all the data in the local file
            4. re-fetch the stored file object from slick, and return it
        """
        if file_obj is None and not os.path.exists(local_file_path):
            return
        storedfile = StoredFile()
        storedfile.mimetype = mimetypes.guess_type(local_file_path)[0]
        storedfile.filename = os.path.basename(local_file_path)
        if file_obj is None:
            storedfile.length = os.stat(local_file_path).st_size
        else:
            file_obj.seek(0,os.SEEK_END)
            storedfile.length = file_obj.tell()
            file_obj.seek(0)
        storedfile = self(storedfile).create()
        md5 = hashlib.md5()
        url = self(storedfile).getUrl() + "/addchunk"
        if file_obj is None:
            with open(local_file_path, 'rb') as filecontents:
                upload_chunks(url, storedfile, filecontents)
        else:
            upload_chunks(url, storedfile, file_obj)
        return self(storedfile).update()


class TestrunGroupApiPart(SlickApiPart):

    def __init__(self, parentPart):
        super(TestrunGroupApiPart, self).__init__(TestrunGroup, parentPart)

    def add_testrun(self, testrun):
        id = testrun
        if isinstance(testrun, Testrun):
            id = testrun.id
        url = self.getUrl()

        # hopefully when we discover what problems exist in slick to require this, we can take the loop out
        for retry in range(3):
            try:
                self.logger.debug("Making request to slick at url %s", url)
                r = requests.post(url + "/addtestrun/" + id)
                self.logger.debug("Request returned status code %d", r.status_code)
                if r.status_code is 200:
                    return self.model.from_dict(r.json())
                else:
                    self.logger.debug("Body of what slick returned: %s", r.text)
            except BaseException as error:
                self.logger.warn("Received exception while connecting to slick at %s", url, exc_info=sys.exc_info())
        raise SlickCommunicationError(
            "Tried 3 times to request data from slick at url %s without a successful status code.", url)

    def remove_testrun(self, testrun):
        id = testrun
        if isinstance(testrun, Testrun):
            id = testrun.id
        url = self.getUrl()

        # hopefully when we discover what problems exist in slick to require this, we can take the loop out
        for retry in range(3):
            try:
                url = url + "/removetestrun/" + id
                self.logger.debug("Making request to slick at url %s", url)
                r = requests.delete(url)
                self.logger.debug("Request returned status code %d", r.status_code)
                if r.status_code is 200:
                    return self.model.from_dict(r.json())
                else:
                    self.logger.debug("Body of what slick returned: %s", r.text)
            except BaseException as error:
                self.logger.warn("Received exception while connecting to slick at %s", url, exc_info=sys.exc_info())
        raise SlickCommunicationError(
            "Tried 3 times to request data from slick at url %s without a successful status code.", url)




class SlickCommunicationError(Exception):
    def __init__(self, *args, **kwargs):
        super(SlickCommunicationError, self).__init__(*args, **kwargs)


class SlickConnection(object):
    """Slick Connection contains the information on how to connect to slick."""
    logger = logging.getLogger("slick.SlickConnection")

    def __init__(self, baseUrl):
        """Create a new connection to slick, providing the base url under which to contact slick."""
        if baseUrl is None or not isinstance(baseUrl, str):
            SlickConnection.logger.error("Base URL provided to slick connection is not a string.")
            raise SlickCommunicationError

        if baseUrl.endswith("/"):
            self.baseUrl = baseUrl + "api"
        else:
            self.baseUrl = baseUrl + "/api"
        self.configurations = SlickApiPart(Configuration, self)
        self.projects = SlickProjectApiPart(self)
        self.projects.releases = SlickApiPart(Release, self.projects)
        self.projects.releases.builds = SlickApiPart(Build, self.projects.releases)
        self.projects.components = SlickApiPart(Component, self.projects)
        self.systemconfigurations = SystemConfigurationApiPart(self)
        self.testplans = SlickApiPart(Testplan, self)
        self.testruns = SlickApiPart(Testrun, self)
        self.version = SlickApiPart(ProductVersion, self, name='version')
        self.testcases = SlickApiPart(Testcase, self)
        self.results = SlickApiPart(Result, self)
        self.testrungroups = TestrunGroupApiPart(self)
        self.hoststatus = SlickApiPart(HostStatus, self, name='hoststatus')
        self.updates = SlickApiPart(SlickUpdate, self, name='updates')
        self.updates.records = SlickApiPart(UpdateRecord, self.updates, name='records')
        self.quotes = SlickApiPart(Quote, self)
        self.files = StoredFileApiPart(self)

    def getUrl(self):
        """This method is used by the slick api parts to get the base url."""
        return self.baseUrl

    def get_name(self):
        return "slick"
