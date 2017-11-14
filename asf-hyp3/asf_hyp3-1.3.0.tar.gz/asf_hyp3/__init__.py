# asf_hyp3/__init__.py
# William Horn, Hal DiMarchi, Rohan Weeden
# Created: May 31, 2017

# Class to interface with the API

import base64
from io import IOBase
import json
from .localizer import Localizer
import os
import pygeoif
import re
import requests
import shapefile

import getpass

try:
    # Python 2.x Libs
    from cookielib import CookieJar
    from urllib2 import build_opener, Request, HTTPError
    from urllib2 import URLError, HTTPHandler, HTTPCookieProcessor
    from urlparse import urljoin

except ImportError:
    # Python 3.x Libs
    from http.cookiejar import CookieJar
    from urllib.error import HTTPError, URLError
    from urllib.parse import urljoin
    from urllib.request import build_opener, Request
    from urllib.request import HTTPHandler, HTTPCookieProcessor

from .scripts import load_granules


class API:
    """
        |************************* API CLASS *************************************|

       Works with the hyp3-api and does all the get requests as well as saving
       the repeated data between class, like the username and api_key.

       formats: json by default which will be converted into appropriate data type,
                csv or any orther format returns string of data recieved

       functions are:
           get_jobs: returns a list of dictionaries or a string depending on format
           get_job: returns a dictionary
           get_products: returns a list of dictionaries or a string depending on format
           get_process: return a dictionary or a string depending on format
           get_processes: returns a list of dictionaries or a string depending on format
           one_time_process: returns a dictionary
           one_time_process_batch: returns a dictionary

           get_subscriptions: return a list of dictionaries or a string depending on format
           create_subscription: returns a dictionary
           remove_subscription: returns a dictionary
           enable_subscription: returns a dictionary
           disable_subscription: returns a dictionary
           modify_subscription: returns a dictionary

           go to https://api.hyp3.asf.alaska.edu/ for further documentation

           from asf_hyp3 import api
    """

    url = ""
    username = ""
    api_key = ""

    _pair = "requires pair"
    _dual = "requires dual pol"

    # processes that require a pair of granules
    _pair_req = []
    # processes that require dual polarization
    _dual_pol_req = []

    # Constructor, set url, username and api_key, if no password or api_key
    # is given will prompt the user for earthdata username and password and
    # attempt to login
    def __init__(self, username=None, password=None, api_key=None, url="https://api.hyp3.asf.alaska.edu/", max_retries=0):
        self.session_cookie = {}
        # source for messages
        self.localizer = Localizer("messages.json")
        self.localizer.load_from(os.path.dirname(__file__), fallback_locale="messages.json")
        self.set_url(url)
        self.set_retries(max_retries)

        # check to see if the url is valid and can connect
        try:
            requests.get(self.url)
        except requests.exceptions.ConnectionError as connectError:
            print(str(connectError))
        except:
            print(self.localizer.to_local('connection.error', self.url))

        self.username = username
        self.api_key = api_key

    # Returns a dictionary of the parameters used in every function
    def _get_default_args(self):
        if self.api_key is None:
            raise APIError(self.localizer.to_local('member.undefined', "api_key"))
        if self.username is None:
            raise APIError(self.localizer.to_local('member.undefined', "username"))
        return {"username": self.username, "api_key": self.api_key}

    # Returns either a dictionary if format is json or a string in csv format
    # depending on the format variable
    #      Exception if the format is not recognized
    def _formatter(self, data, format=None):
        formatted_data = ""

        try:
            formatted_data = json.loads(data)
        except:
            formatted_data = data

        return formatted_data

    # Check if a granule string is dual_pol
    def _is_dual_pol(self, granule):
        pol = granule[14]
        return pol == "D"

    def _requires_pair(self, process_id):
        if self._pair_req is None or self._pair_req == []:
            self._update_processes_info()
        return process_id in self._pair_req

    def _requires_dual_pol(self, process_id):
        if self._dual_pol_req is None or self._dual_pol_req == []:
            self._update_processes_info()
        return process_id in self._dual_pol_req

    def _update_processes_info(self):
        processes = self.get_processes()
        self._pair_req = [p['id'] for p in processes if p['requires_pair']]
        self._dual_pol_req = [p['id'] for p in processes if p['requires_dual_pol']]

    def _make_request(self, endpoint, args, post_args=None):
        req_args = self._get_default_args()

        if 'format' in args:
            args['format'] = self._lower(args['format'])
        # Only put the arguments into the url if the value is passed to the function
        req_args.update({key: value for (key, value) in args.items() if value is not None})

        self._format_lists(req_args)

        request_type = "GET" if post_args is None else "POST"
        url = urljoin(self.url, endpoint)
        for i in range(self.tries):
            response = requests.request(request_type, url, params=req_args,
                                        data=post_args, cookies=self.session_cookie)
            if response.status_code == requests.codes.ok:
                text = response.text
                break
            elif response.status_code == 500:
                raise APIError(self.localizer.to_local('connection.server_error',
                                                       "url: {}\nheaders: {}".format(response.request.url, response.request.headers)))
            else:
                return response.text

        return self._formatter(text)

    def _format_lists(self, args):
        """Get requests indicate arrays by adding '[]' to the end of the key:
            Example:
                ?arr[]=first&arr[]=second&arr[]=third
        """

        for k, v in reversed(list(args.items())):
            if isinstance(v, list):
                args.pop(k)
                args[k + "[]"] = v

    # Checks if all statuses succeeded
    def _did_all_succeed(self, statuses):
        if not isinstance(statuses, list):
            # confusing, but in this case statuses is just one status.
            statuses = [statuses]

        for status in statuses:
            if status.get('status') != "SUCCESS":
                return False

        return True

    # Takes a list of statuses and gets the actual objects
    #       return type: Always returns a list.
    def _ids_to_items(self, statuses, item_type):
        items = []

        item_type = self._lower(item_type)

        # make status into a list
        if not isinstance(statuses, list):
            # confusing, but in this case statuses is just one status.
            statuses = [statuses]

        for status in statuses:
            id = status.get('id')
            if item_type == "job":
                job = self.get_job(id)
                items.append(job)

        return items

    # Makes lowercases carfully a string
    def _lower(self, string):

        if string and isinstance(string, str):
            string = string.lower()

        return string

    # Getters an setters for class attributes that need special error checking
    def set_retries(self, max_retries):
        if max_retries >= 0:
            self.tries = max_retries + 1
        else:
            self.tries = 1

    def set_url(self, url):
        self.url = url
        if url[-1] != "/":
            self.url += "/"

    def login(self, password=None, doesPrint=True, reset_key=True):
        """Logs the user in and gets a valid api key"""

        hadUsername = True
        edlogin = EarthdataLogin("YsS6RMIBT4s10UJzyejGaQ", urljoin(self.url, "login/authorized"))

        # Enter username/password
        if self.username is None:
            print("Enter EARTHDATA credentials")
            hadUsername = False
            user_prompt = self.localizer.to_local('login.username_prompt')
            try:
                self.username = str(raw_input(user_prompt))
            except:
                self.username = str(input(user_prompt))

        if password is None:
            prompt = (self.localizer.to_local('login.password_prompt.with_username', self.username)
                      if hadUsername else self.localizer.to_local('login.password_prompt.no_username'))
            new_password = getpass.getpass(prompt=prompt)
        else:
            new_password = password

        session_cookie, response = edlogin.getLoginCookie(self.username, new_password)
        self.session_cookie = {session_cookie.name: session_cookie.value}
        resp = json.loads(response.read().decode())
        if 'api_key' in resp:
            self.api_key = resp['api_key']
        elif 'status' in resp and resp['status'] == "ERROR":
            raise LoginError(self.localizer.to_local(
                'login.no_user_error', urljoin(self.url, "login")))
        elif reset_key is True:
            self.reset_api_key(doesPrint)

        if doesPrint:
            print(self.localizer.to_local('login.success'))

    def reset_api_key(self, doesPrint=True):
        """Gets a new api key. Must call login() first to set the session cookie"""

        if self.session_cookie == {} or self.session_cookie is None:
            raise LoginError(self.localizer.to_local('member.undefined', 'session_cookie'))

        key_resp = json.loads(requests.get(urljoin(self.url, "reset_api_key"),
                                           cookies=self.session_cookie).text)
        if 'api_key' in key_resp:
            self.api_key = key_resp['api_key']
        elif 'message' in key_resp:
            print(self.localizer.to_local('error.with_message', key_resp['message']))
        else:
            print(self.localizer.to_local('error.without_message'))
            exit(-1)
        return key_resp

    def get_jobs(self, id=None, status=None, sub_id=None, granule=None, format=None):
        """Returns a list of dictionaries containing job information with the specified attributes.
        Job info:
            - id, sub_id, user_id, process_id, status, granule,
              granule_url, other_granules, other_granule_urls,
              request_time, processed_time, priority, message
        """

        if isinstance(id, list):
            return self.get_jobs_id_list(id, status, sub_id, granule, format)
        else:
            args = {"id": id,
                    "status": status,
                    "sub_id": sub_id,
                    "granule": granule,
                    "format": format}

            return self._make_request("get_jobs", args)

    def get_jobs_id_list(self, id=None, status=None, sub_id=None, granule=None, format=None):
        args = {
            "status": status,
            "sub_id": sub_id,
            "granule": granule,
            "format": format}

        ids = set(id)

        # can only do list id select with json
        if format is not None and format.lower() == "csv":
            raise APIError(self.localizer.to_local('get_jobs.incompatible_format'))

        # Get all the users jobs first
        all_jobs = self._make_request("get_jobs", args, format)

        # Return only the ones which the user is interested in
        jobs = []
        for job in all_jobs:
            if job['id'] in ids:
                jobs.append(job.copy())
        return jobs

    """Returns a dictionary just like the one referenced in get_jobs"""

    def get_job(self, id, format=None):
        job = self.get_jobs(id=id, format=format)

        if isinstance(job, list) and len(job) > 0:
            return job[0]
        else:
            return job

    def get_products(self,
                     id=None,
                     sub_id=None,
                     sub_name=None,
                     creation_date=None,
                     start_date=None,
                     end_date=None,
                     name=None,
                     group_id=None,
                     group_ids=None,
                     format=None):
        """Returns a list of dictionaries product information with the specified
        attributes.
        Product info contains fields:
        - id, sub_id, name, url, browse_url,
        size, creation_date, group_ids
        """

        args = {"id": id,
                "sub_id": sub_id,
                "sub_name": sub_name,
                "creation_date": creation_date,
                "start_date": str(start_date) if start_date is not None else None,
                "end_date": str(end_date) if end_date is not None else None,
                "name": name,
                "group_id": group_id,
                "group_ids": list(group_ids) if group_ids is not None else None,
                "format": format}

        return self._make_request('get_products', args)

    """Returns a dictionary just like the one referenced in get_product"""

    def get_product(self, id, format=None):
        product = self.get_products(id=id, format=format)

        if isinstance(product, list) and len(product) > 0:
            return product[0]
        else:
            # Most likely there was an error
            return product

    def get_process(self, id, format=None):
        """Returns a dictionary or a string depending on format containing information about the process.
            return fields are:

            - id, name, description, requires_pair,
              supports_time_series_processing, requires_dual_pol
        """

        args = {
            "id": id,
            "format": format
        }

        return self._make_request('get_process', args)

    def get_processes(self, format=None):
        """Returns a list of dictionaries all available processes. Each entry is as
           described by get_process.
        """

        args = {'format': format}

        return self._make_request('get_processes', args)

    def one_time_process(self,
                         granule,
                         process_id,
                         return_object=False,
                         other_granule=None,
                         other_granules=None,
                         priority=None,
                         message=None):
        """Schedules a new processing request and returns a dictionary
        indicating whether or not the request succeeded, and an error message.
        If the process_id specifies a process that requires a granule pair,
        then other_granules must also be supplied.

        The granule can be either passed as a string, as the path of the file that
        contains the granule(s) or as a list of granule strings
        Returns:
            {"status": "SUCCESS", "message": null} or
            {"status": "SUCCESS", "id": 8000}

         other_granule and other_granules are the same thing.
        """

        if isinstance(granule, list):
            return self.one_time_process_list(granule, process_id, return_object, other_granules, priority, message)
        elif isfile(granule) or (isinstance(granule, str) and (not self.is_granule(granule))):
            # Either a file was passed, or possibly a path to a file
            return self.one_time_process_file(granule, process_id, return_object, other_granules, priority, message)
        else:
            return self.one_time_process_single(granule, process_id, return_object, other_granule, other_granules, priority, message)

    def one_time_process_single(self,
                                granule,
                                process_id,
                                return_object=False,
                                other_granule=None,
                                other_granules=None,
                                priority=None,
                                message=None):
        if other_granules is None:
            other_granules = other_granule

        if self._requires_pair(process_id) and other_granules is None:
            raise APIError(self.localizer.to_local('one_time_process.granule_pair_required'))
        if self._requires_dual_pol(process_id) and not self._is_dual_pol(granule):
            raise APIError(self.localizer.to_local(
                'one_time_process.dual_pol_granule_required'))

        args = {
            "granule": granule,
            "process_id": process_id,
            "other_granules": other_granules,
            "priority": priority,
            "message": message
        }

        status = self._make_request("one_time_process", args)

        # Return either the status code or a the job info
        if return_object is True and self._did_all_succeed(status):
            job = self._ids_to_items(status, "job")
            return job
        # there was an error
        else:
            return status

    def one_time_process_list(self,
                              granule_list,
                              process_id,
                              return_object=False,
                              other_granules=None,
                              priority=None,
                              message=None):
        """Do a number of one_time_process requests.
        granule_list - A list of granules to process
        process_id - Either an integer or a list of integers with the same length as granule_list
        other_granules - Either None if no processes in process_id require a granule pair,
                         or a list of the same length as granule_list

        """
        granules = granule_list
        statuses = []
        if isinstance(process_id, list):
            if not len(process_id) == len(granules):
                raise APIError(self.localizer.to_local(
                    'one_time_process.granule_pair_required'))

        # Check that all the required fields are there
        for i in range(len(granules)):
            g = granules[i]
            try:
                other_g = other_granules[i]
            except:
                other_g = None
            # Make sure all are valid granule string
            if not self.is_granule(g):
                raise APIError(self.localizer.to_local('one_time_process.invalid_granule', g))

            # Check if the processes is compatible
            if isinstance(process_id, list):
                p_id = process_id[i]
            else:
                p_id = process_id
            if self._requires_pair(p_id) and other_g is None:
                raise APIError(self.localizer.to_local(
                    'one_time_process.granule_pair_required'))
            if self._requires_dual_pol(p_id) and not self._is_dual_pol(g):
                raise APIError(self.localizer.to_local(
                    'one_time_process.dual_pol_granule_required'))

        # Process each granule
        for i in range(len(granules)):
            g = granules[i]
            try:
                other_g = other_granules[i]
            except:
                other_g = None

            if isinstance(process_id, list):
                p_id = process_id[i]
            else:
                p_id = process_id
            status = self.one_time_process_single(
                g, p_id, False, other_g, other_g, priority, message)
            statuses.append(status)

        # Return either the job info or an error
        if return_object is False:
            return statuses
        else:
            if self._did_all_succeed(statuses):
                return self._ids_to_items(statuses, "job")

    def one_time_process_file(self, granule, process_id, return_object=False,
                              other_granules=None, priority=None, message=None):
        granules = load_granules(granule)
        return self.one_time_process_list(granules, process_id, return_object, other_granules, priority, message)

    def one_time_process_batch(self, filename):
        args = self._get_default_args()
        files = {'file': open(filename)}
        response = requests.post(urljoin(self.url, "one_time_process_batch"),
                                 params=args, files=files)
        return self._formatter(response.text, 'json')

    def _valid_stages(self, stages):
        # Check to make sure evey element is a string
        if len([s for s in stages if not isinstance(s, str)]) > 0:
            return False

        # Make sure first and last elements are correct
        if len(stages) > 0:
            if stages[0].lower() not in ('isce', 'gamma'):
                return False
            if len(stages) > 1 and stages[-1].lower() not in ('giant', 'interograms'):
                return False

        return True

    def _valid_swath(self, swath):
        return swath in (1, 2, 3)

    def time_series_process(self, granule_list=None, latitude=None,
                            longitude=None, priority=None, message=None,
                            swath=None, stages=None):
        if stages is not None and not self._valid_stages(stages):
            raise APIError(self.localizer.to_local("time_series_process.bad_stages", str(stages)))

        if swath is not None and not self._valid_swath(swath):
            raise APIError(self.localizer.to_local("time_series_process.bad_swath", str(swath)))

        shared = {}
        for arg in ['priority', 'message', 'swath', 'stages']:
            shared[arg] = eval(arg)

        if granule_list is not None and isinstance(granule_list, list):
            return self.time_series_from_list(granule_list, **shared)
        elif latitude is not None and longitude is not None:
            return self.time_series_from_lat_lon(latitude, longitude, **shared)
        else:
            raise APIError(self.localizer.to_local("time_series_process.no_data"))

    def time_series_from_list(self, granule_list, **kwargs):
        post_args = {"granule_list": json.dumps(granule_list)}

        return self._make_request("time_series_from_list", kwargs, post_args=post_args)

    def time_series_from_lat_lon(self, latitude, longitude, **kwargs):
        kwargs.update({"latitude": latitude,
                       "longitude": longitude})

        return self._make_request("time_series_from_lat_lon", kwargs)

    def create_subscription(self, crop_to_selection, name, process_id, platform,
                            location, polarization='{}', start_date=None,
                            end_date=None, description=None, extra_arguments="no",
                            enable=True, project_id=None, group_id=None):
        """Schedules a new subscription and returns a dictionary indicating
           whether or not the request succeeded, as well as an error message in
           the event of failure.

           location can either be a MULTIPOLYGON string or a file path to a .dbf or .shp file
        """

        # Checks to see if a shapefile path was passed
        if not re.match("MULTIPOLYGON", location) and (re.search(".(dbf|shp)", location) is not None):
            try:
                sf = shapefile.Reader(location)
            except Exception as e:
                return self.localizer.to_local('create_subscription.shapefile_exception', str(e))

            shape = []
            for feature in sf.shapes():
                shape.append(pygeoif.geometry.as_shape(feature))
            location = pygeoif.MultiPolygon(shape).wkt

        args = {
            "polarization": polarization,
            "crop_to_selection": str(crop_to_selection),
            "name": name,
            "process_id": str(process_id),
            "platform": platform,
            "location": location,
            "start_date": start_date,
            "end_date": end_date,
            "description": description,
            "extra_arguments": extra_arguments,
            "enable": enable,
            "project_id": project_id,
            "group_id": group_id
        }

        return self._make_request("create_subscription", args)

    def get_subscriptions(self, id=None, process_id=None, name=None, location=None,
                          start_date=None, end_date=None, enabled=None,
                          project_id=None, group_id=None, format=None):
        """Returns a array of subscription information with the specified
           attributes or a string depending on format. Subscription info contains fields:

            - id, process_id, user_id, name, location,
              start_date, end_date, enabled, group_ids
        """

        args = {"id": id,
                "process_id": process_id,
                "name": name,
                "location": location,
                "start_date": start_date,
                "end_date": end_date,
                "enabled": enabled,
                "project_id": project_id,
                "group_id": group_id,
                "format": format}

        return self._make_request('get_subscriptions', args)

    def get_subscription(self, id, format=None):
        """Returns a dictionary just like the one referenced in get_subscriptions"""

        subscription = self.get_subscriptions(id=id, format=format)

        if isinstance(subscription, list) and len(subscription) > 0:
            # strips off the list around the dictionary
            return subscription[0]
        else:
            # Most likely there was an error
            return subscription

    def disable_subscription(self, id, project_id=None):
        """Sets the property 'enabled' of a subscription to False. No further
        actions will be taken based on this subscription until it is enabled
        again. Returns a dictionary indicating whether or not the request
        succeeded, and an error message in the event it did not.
        """

        args = {
            "sub_id": id,
            "project_id": project_id
        }

        return self._make_request('disable_subscription', args)

    def enable_subscription(self, id, project_id=None):
        """Sets the property 'enabled' of a subscription to true. Products from
        this subscription will continue to be processed
        """
        args = {
            "sub_id": id,
            "project_id": project_id
        }

        return self._make_request('enable_subscription', args)

    def modify_subscription(self, id, project_id=None, name=None, description=None, end_date=None):
        """Change the name, and/or description of a subscription.
            id - The id of the subscription to modify
        """

        args = {
            "sub_id": id,
            "project_id": project_id,
            "name": name,
            "description": description,
            "end_date": end_date
        }

        return self._make_request("modify_subscription", args)

    def create_group(self, name, description=None):
        """Create a new subscription group"""

        args = {
            "name": name,
            "description": description
        }

        return self._make_request("create_group", args)

    def modify_group(self, id, name=None, description=None, add_subs=[], rem_subs=[], add_users=[], rem_users=[]):
        """Change the name or description of a group
            id - The id of the group to modify
        """
        add_subs = set(add_subs)
        rem_subs = set(rem_subs)
        add_users = set(add_users)
        rem_users = set(rem_users)

        args = {
            "id": id,
            "name": name,
            "description": description,
            "add_subs": list(add_subs),
            "rem_subs": list(rem_subs),
            "add_users": list(add_users),
            "rem_users": list(rem_users)
        }

        return self._make_request("modify_group", args)

    def get_groups(self, id=None, name=None, format=None):
        """Returns an array of group information with the specified attributes
        Group info contains fields:

            - id, name, description, users, subscription_ids"""

        args = {
            "id": id,
            "name": name,
            "format": format
        }

        return self._make_request("get_groups", args)

    def is_granule(self, obj):
        """Check if a string is a valid granule"""

        pattern = re.compile(
            r'(S1[A-D]_(IW|EW|WV|S1|S2|S3|S4|S5|S6)_(GRD|SLC|OCN)[FHM_]_[12][SA](SH|SV|DH|DV)_\d{8}T\d{6}_\d{8}T\d{6}_\d{6}_[0-9A-F]{6}_[0-9A-F]{4})')
        if isinstance(obj, str):
            if re.search(pattern, obj):
                return True
        return False

# |---------------------- END API CLASS -------------------------|


class LoginError(Exception):
    pass


class APIError(Exception):
    pass


class EarthdataLogin(object):
    def __init__(self, client_id, redirect_url):
        # source of messages
        self.localizer = Localizer("messages.json")
        self.localizer.load_from(os.path.dirname(__file__), fallback_locale="messages.json")
        self.urls = {'url': 'https://urs.earthdata.nasa.gov/oauth/authorize',
                     'client': client_id,
                     'redir': redirect_url}

    def getLoginCookie(self, username, password):
        url = '{0}?response_type=code&client_id={1}&redirect_uri={2}'.format(
            self.urls['url'], self.urls['client'], self.urls['redir'])
        user_pass = self.httpBasicAuth(username, password)
        # Authenticate against URS, grab all the cookies
        cj = CookieJar()
        opener = build_opener(HTTPCookieProcessor(cj), HTTPHandler())
        request = Request(url, headers={"Authorization": "Basic {0}".format(user_pass)})

        # Watch out cookie rejection!
        try:
            response = opener.open(request)
        except HTTPError as e:
            if e.code == 401:
                raise LoginError(self.localizer.to_local('login.bad_credentials'))
            else:
                # If an error happens here, the user most likely has not confirmed EULA.
                raise LoginError(self.localizer.to_local('connection.cookie_error'))
        except URLError as e:
            raise LoginError(self.localizer.to_local('connection.urs_error'))

        session_cookie = None
        for cookie in cj:
            if cookie.name == "session":
                session_cookie = cookie
                break

        if session_cookie is None:
            raise LoginError(self.localizer.to_local('connection.cookie_error'))

        return session_cookie, response

    def httpBasicAuth(self, username, password):
        try:
            # python2
            user_pass = base64.b64encode(bytes(username + ":" + password))
        except TypeError:
            # python3
            user_pass = base64.b64encode(bytes(username + ":" + password, "utf-8"))
            user_pass = user_pass.decode("utf-8")
        return user_pass


def isfile(obj):
    try:
        return isinstance(obj, file)
    except NameError:
        return isinstance(obj, IOBase)
