'''Module containing definition of the main Client class'''

# Standard library imports
import uuid

# Imports
import requests
import click

# Package imports
from . import constants
from . import errors
from . import util

class Client(object):
    '''Main Client class for accessing Gencove API'''
    def __init__(
            self, host, device_uuid=None, refresh_token=None, api_key=None):
        self._set_host(host)
        self._set_device_uuid(device_uuid)
        self.set_refresh_token(refresh_token)
        self.set_api_key(api_key)

    def _set_host(self, host):
        '''Set host

        Defaults to constants.HOST_DEFAULT
        Even though it can be None, we want the user to explicitly define it as 
        None

        Args:
            host (str): host

        Raises:
            TypeError: if host is not text
        '''
        if host is None:
            # Output to stderr so stdout is not contaminated
            click.echo(
                'Using default host: {}'.format(constants.HOST_DEFAULT), 
                err=True)
            host = constants.HOST_DEFAULT
        if not util.is_text(host):
            raise TypeError('host must be text')
        self._host = host

    def _set_device_uuid(self, device_uuid=None):
        '''Set device UUID

        Defaults to uuid.getnode()

        Args:
            device_uuid (str): device UUID
        '''
        if device_uuid is None:
            device_uuid = uuid.getnode()

        self._device_uuid = device_uuid

    def set_refresh_token(self, refresh_token):
        '''Set a refresh token for auth

        Args:   
            refresh_token (str): new refresh token

        Raises:
            TypeError: refresh_token is not text
        '''
        if not (refresh_token is None or util.is_text(refresh_token)):
            raise TypeError('refresh_token must be either None or text')
        self._refresh_token = refresh_token
        self._set_jwt(None)

    def get_refresh_token(self):
        '''Get current refresh token'''
        return self._refresh_token

    def set_api_key(self, api_key):
        '''Set an API key for auth

        Args:   
            api_key (str): new API key

        Raises:
            TypeError: api_key is not text
        '''
        if not (api_key is None or util.is_text(api_key)):
            raise TypeError('api_key must be either None or text')
        self._api_key = api_key

    def get_api_key(self):
        '''Get current API key'''
        return self._api_key

    def _set_jwt(self, jwt):
        '''Set a JWT for auth

        Args:
            jwt (str): new jwt

        Raises:
            TypeError: if jwt is not text
            ValueError: if jwt is not formatted as Header.Payload.Signature
        '''
        if not (jwt is None or util.is_text(jwt)):
            raise TypeError('jwt must be either None or text')
        if util.is_text(jwt) and len(jwt.split('.')) != 3:
            raise ValueError('jwt must consist of three parts separated by "."')
        self._jwt = jwt  

    def url(self, endpoint, keys={}):
        '''Generate URL for endpoint

        Args:
            endpoint (str): endpoint identifier
            keys (dict): dict defining keys in URL to fill in

        Returns:
            str: complete URL for endpoint

        Raises:
            gencove.errors.URLDataIncompleteError: on unknown endpoint or missing 
                incomplete keys
        '''
        try:
            return (self._host+constants.ENDPOINTS[endpoint]).format(**keys)
        except KeyError as e:
            raise errors.URLDataIncompleteError('Please provide key {} for endpoint \'{}\''.format(e, endpoint))

    def _process_response(self, response):
        '''Common method to process HTTP responses

        It will attempt to decode JSON and check the response code

        Args:
            response (requests.Response): HTTP response to process

        Returns:
            dict: response.text parsed as JSON

        Raises:
            gencove.errors.HTTPError: on HTTP response with an erroneous 
                status_code
            gencove.errors.NoJSONInResponseError: in case JSON cannot be parsed
        '''

        # This will raise gencove.errors.HTTPError if needed
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            raise errors.HTTPError(e.args[0], response=response)

        # This will raise gencove.errors.NoJSONInResponseError if needed
        try:
            response_dict = response.json()
        except ValueError as e:
            raise errors.NoJSONInResponseError(e, response)

        return response_dict

    def register(self, name, email, password=None, return_response=False):
        '''Register new account with Gencove

        In case password is None, user will be prompted for password.

        Args:
            email (str): email to associate with user
            password (str): password to associate with user
            name (str): name to associate with user
            return_response (bool): whether to return backend response parsed as 
                JSON

        Returns:
            None or dict: None or backend response parsed as JSON, depending on
            return_response

        Raises:
            click.Abort: in case user aborts when prompted for input
            gencove.errors.HTTPError: on HTTP response with an erroneous 
                status_code
            gencove.errors.NoJSONInResponseError: in case JSON cannot be parsed
            gencove.errors.URLDataIncompleteError: on unknown endpoint or missing 
                incomplete keys
            TypeError: in case returned refresh token is not text

        '''
        password = util.prompt_stderr(password, confirmation_prompt=True)

        response = requests.post(
            self.url('register'), 
            json={
                'email': email, 
                'password': password, 
                'name': name, 
                'device_uuid': self._device_uuid
            }, 
            headers=constants.HEADER_JSON
        )

        response_dict = self._process_response(response)

        self.set_refresh_token(response_dict['refresh_token'])

        if return_response:
            return response_dict

    def login(self, email, password=None, return_response=False):
        '''Log into Gencove backend

        In case password is None, user will be prompted for password.

        CAUTION: This will log out any sessions (tokens) the user has with 
        current device_uuid

        Keyword arguments:
            email (str): email associated with user
            password (str): password associated with user
            return_response (bool): whether to return backend response parsed as 
                JSON

        Returns:
            None or dict: None or backend response parsed as JSON, depending on
            return_response

        Raises:
            gencove.errors.HTTPError: on HTTP response with an erroneous 
                status_code
            click.Abort: in case user aborts when prompted for input
            gencove.errors.NoJSONInResponseError: in case JSON cannot be parsed
            gencove.errors.URLDataIncompleteError: on unknown endpoint or missing 
                incomplete keys
            TypeError: in case returned refresh token is not text
        '''
        password = util.prompt_stderr(password)

        response = requests.post(
            self.url('login'), 
            json={
                'email': email, 
                'password': password, 
                'device_uuid': self._device_uuid
            }, 
            headers=constants.HEADER_JSON
          )

        response_dict = self._process_response(response)

        self.set_refresh_token(response_dict['refresh_token'])

        if return_response:
            return response_dict

    def logout(self, return_response=False):
        '''Log out of Gencove

        Invalidates refresh token on backend.

        Args:
            return_response (bool): whether to return backend response parsed as 
                JSON

        Returns:
            None or dict: None or backend response parsed as JSON, depending on
            return_response
        
        Raises:
            gencove.errors.HTTPError: on HTTP response with an erroneous 
                status_code
            gencove.errors.NoJSONInResponseError: in case JSON cannot be parsed
            gencove.errors.NotLoggedInError: if not logged in
            gencove.errors.URLDataIncompleteError: on unknown endpoint or missing 
                incomplete keys
            TypeError: in case returned refresh token is not text
        '''
        self.check_login()
        
        response = requests.post(
            self.url('logout'), 
            json={
                'refresh_token': self.get_refresh_token()
            }, 
            headers=constants.HEADER_JSON
        )

        response_dict = self._process_response(response)

        self.set_refresh_token(None)

        if return_response:
            return response_dict

    def email_confirm(self, confirm_id, return_response=False):
        '''Confirm email with confirmation code

        Args:
            confirm_id (str): email confirmation code (usually received via 
                email)
            return_response (bool): whether to return backend response parsed as 
                JSON

        Returns:
            None or dict: None or backend response parsed as JSON, depending on
            return_response
        
        Raises:
            gencove.errors.HTTPError: on HTTP response with an erroneous 
                status_code
            gencove.errors.NoJSONInResponseError: in case JSON cannot be parsed
            gencove.errors.URLDataIncompleteError: on unknown endpoint or missing 
                incomplete keys
        '''

        response_dict = self._process_response(
            # No need for auth
            requests.put(
                self.url('confirm', {'confirm_id': confirm_id})
            )
        )

        if return_response:
            return response_dict

    def password_forgot_init(self, email, return_response=False):
        '''Trigger sending of forgotten password email

        CAUTION: changing password invalidates all sessions (tokens) for current
        user

        Args:
            email (str): email associated with account
            return_response (bool): whether to return backend response parsed as 
                JSON

        Returns:
            None or dict: None or backend response parsed as JSON, depending on
            return_response
        
        Raises:
            gencove.errors.HTTPError: on HTTP response with an erroneous 
                status_code
            gencove.errors.NoJSONInResponseError: in case JSON cannot be parsed
            gencove.errors.URLDataIncompleteError: on unknown endpoint or missing 
                incomplete keys
        '''
        response_dict = self._process_response(
            requests.post(
              self.url('password_forgot_init'),
              json = {
                  'email': email
              }, 
              headers=constants.HEADER_JSON
            )
        )

        if return_response:
            return response_dict

    def check_login(self):
        '''Check if user is logged in

        Raises:
            gencove.errors.NotLoggedInError: if not logged in
        '''
        if self.get_refresh_token() is None:
            raise errors.NotLoggedInError('Not logged in')

    def is_logged_in(self):
        try:
            self.check_login()
            return True
        except errors.NotLoggedInError as e1:
            return False

    def check_api_key(self):
        '''Check if user has api key

        Raises:
            gencove.errors.NoApiKeyError: if no API key
        '''
        if self.get_api_key() is None:
            raise errors.NoApiKeyError('No API key present')

    def check_auth(self):
        try:
            self.check_login()    
        except errors.NotLoggedInError as e1:
            try:
                self.check_api_key()
            except errors.NoApiKeyError as e2:
                raise errors.NoAuthError(
                    'Not logged in and no API key present')

    def _get_jwt(self):
        '''Get JWT from Gencove backend'''
        self.check_login()

        response = requests.post(
            self.url('auth'), 
            json={
                'refresh_token': self.get_refresh_token(),
                'empty': 'e'
            }, 
            headers=constants.HEADER_JSON
        )

        response_dict = self._process_response(response)

        self._set_jwt(response_dict['access_token'])

    def _auth_header(self):
        '''Generate Authorization header for HTTP request'''
        try: 
            if self._jwt is None:
                self._get_jwt()

            return {'Authorization':'JWT {}'.format(self._jwt)}
        except errors.NotLoggedInError as e1:
            try:
                self.check_api_key()

                return {
                    'Authorization':'GENCOVE-API-KEY {}'.format(
                        self.get_api_key())
                }
            except errors.NoApiKeyError as e2:
                raise errors.NoAuthError(
                    'Not logged in and no API key present')

    def _auth_req(self, method, *args, **kwargs):
        '''Base method for requests to backend endpoints requiring auth'''
        self.check_auth()

        if 'headers' not in kwargs:
            kwargs['headers'] = {}

        kwargs['headers'].update(self._auth_header())
        response = method(*args, **kwargs)

        if response.status_code == 401 and self.is_logged_in():
            # trigger fetching of new JWT
            self._set_jwt(None)
            kwargs['headers'].update(self._auth_header())
            response = method(*args, **kwargs)

        return response

    def _get(self, *args, **kwargs):
        '''HTTP GET to backend endpoints requiring auth'''
        return self._auth_req(requests.get, *args, **kwargs)

    def _post(self, *args, **kwargs):
        '''HTTP POST to backend endpoints requiring auth'''
        return self._auth_req(requests.post, *args, **kwargs)

    def _put(self, *args, **kwargs):
        '''HTTP PUT to backend endpoints requiring auth'''
        return self._auth_req(requests.put, *args, **kwargs)

    def _patch(self, *args, **kwargs):
        '''HTTP PATCH to backend endpoints requiring auth'''
        return self._auth_req(requests.patch, *args, **kwargs)

    def _delete(self, *args, **kwargs):
        '''HTTP DELETE to backend endpoints requiring auth'''
        return self._auth_req(requests.delete, *args, **kwargs)

    def password_change(
            self, password, new_password, new_password_confirm, 
            return_response=False):
        '''Change password

        In case passwords are None, user will be prompted for password.

        CAUTION: changing password invalidates all sessions (tokens) for current
        user

        Args:
            password (str): current password
            new_password (str): new password
            new_password_confirm (str): must match new_password
            return_response (bool): whether to return backend response parsed as 
                JSON

        Returns:
            None or dict: None or backend response parsed as JSON, depending on
            return_response
            
        Raises:
            click.Abort: in case user aborts when prompted for input
            gencove.errors.HTTPError: on HTTP response with an erroneous 
                status_code
            gencove.errors.NoJSONInResponseError: in case JSON cannot be parsed
            gencove.errors.NotLoggedInError: if not logged in
            gencove.errors.URLDataIncompleteError: on unknown endpoint or missing 
                incomplete keys
            TypeError: in case new auth JWT or refresh token are not text
            ValueError: in case new auth JWT is not properly formatted
        '''
        password = util.prompt_stderr(password)
        new_password = util.prompt_stderr(new_password, 'New password')
        new_password_confirm = util.prompt_stderr(
            new_password_confirm, 'Confirm new password')

        response_dict = self._process_response(
            self._put(
                self.url('password_change'),
                json = {
                    'password': password,
                    'new_password': new_password,
                    'new_password_confirm': new_password_confirm,
                    'device_uuid': self._device_uuid
                }
            )
          )

        self.set_refresh_token(response_dict['refresh_token'])

        if return_response:
            return response_dict

    def studies_get(self, return_response=False):
        '''Get all studies owned by user

        Returns:
            list or dict: list of studies or backend response parsed as JSON, 
            depending on return_response
            
        Raises:
            gencove.errors.HTTPError: on HTTP response with an erroneous 
                status_code
            gencove.errors.NoJSONInResponseError: in case JSON cannot be parsed
            gencove.errors.NotLoggedInError: if not logged in
            gencove.errors.URLDataIncompleteError: on unknown endpoint or missing 
                incomplete keys
            TypeError: in case new auth JWT is not text
            ValueError: in case new auth JWT is not properly formatted
        '''
        response_dict = self._process_response(
            self._get(
                self.url('studies')
            )
        )

        if return_response:
            return response_dict
        else:
            return response_dict['studies']

    def study_create(
            self, name, href, description, study_enabled=True, 
            discoverable=True, return_response=False):
        '''Create a new study that will be owned by this user

        Args:
            name (str): study name
            href (str): URL of study description
            description (str): study description
            study_enabled (bool): whether the study is enabled upon creation 
                [optional, default: True]
            discoverable (bool): whether the study is discoverable upon 
                creation [optional, default: True]

        Returns:
            dict: study or backend response parsed as JSON, depending on 
                return_response
            
        Raises:
            gencove.errors.HTTPError: on HTTP response with an erroneous 
                status_code
            gencove.errors.NoJSONInResponseError: in case JSON cannot be parsed
            gencove.errors.NotLoggedInError: if not logged in
            gencove.errors.URLDataIncompleteError: on unknown endpoint or missing 
                incomplete keys
            TypeError: in case new auth JWT is not text
            ValueError: in case new auth JWT is not properly formatted
        '''
        response_dict = self._process_response(
            self._post(
                self.url('studies'),
                json = {
                    'name': name,
                    'href': href,
                    'description': description,
                    'study_enabled': study_enabled,
                    'discoverable': discoverable
                }, 
                headers=constants.HEADER_JSON
            )
        )

        if return_response:
            return response_dict
        else:
            return response_dict['study']

    def study_get(self, study_id, return_response=False):
        '''Get study info

        Args:
            study_id (int): study id

        Returns:
            dict: study or backend response parsed as JSON, depending on 
                return_response
            
        Raises:
            gencove.errors.HTTPError: on HTTP response with an erroneous 
                status_code
            gencove.errors.NoJSONInResponseError: in case JSON cannot be parsed
            gencove.errors.NotLoggedInError: if not logged in
            gencove.errors.URLDataIncompleteError: on unknown endpoint or missing 
                incomplete keys
            TypeError: in case new auth JWT is not text
            ValueError: in case new auth JWT is not properly formatted
        '''
        response_dict = self._process_response(
            self._get(
                self.url('study', {'study_id': study_id})
            )
        )

        if return_response:
            return response_dict
        else:
            return response_dict['study']

    def study_update(
            self, study_id, name=None, href=None, description=None, 
            subsidy_enabled=None, study_enabled=None, 
            discoverable=None, return_response=False):
        '''Update study info

        Args:
            study_id (int): study id
            name (str): study name
            href (str): URL of study description
            description (str): study description
            subsidy_enabled (bool): whether subsidies are enabled for this study
            study_enabled (bool): whether the study is enabled
            discoverable (bool): whether the study is discoverable

        Returns:
            dict: study or backend response parsed as JSON, depending on 
                return_response
            
        Raises:
            gencove.errors.HTTPError: on HTTP response with an erroneous 
                status_code
            gencove.errors.NoJSONInResponseError: in case JSON cannot be parsed
            gencove.errors.NotLoggedInError: if not logged in
            gencove.errors.URLDataIncompleteError: on unknown endpoint or missing 
                incomplete keys
            gencove.errors.NoDataError: when all arguments but study_id are None
            TypeError: in case new auth JWT is not text
            ValueError: in case new auth JWT is not properly formatted
        '''    
        update_data = {}
        if name is not None:
            update_data['name'] = name

        if href is not None:
            update_data['href'] = href

        if description is not None:
            update_data['description'] = description

        if subsidy_enabled is not None:
            update_data['subsidy_enabled'] = subsidy_enabled

        if study_enabled is not None:
            update_data['study_enabled'] = study_enabled

        if discoverable is not None:
            update_data['discoverable'] = discoverable

        if len(update_data) == 0:
            raise errors.NoDataError('No data provided. Provide at least one of: name, href, description.')

        response_dict = self._process_response(
            self._put(
                self.url('study', {'study_id': study_id}),
                json = update_data, 
                headers=constants.HEADER_JSON
            )
        )

        if return_response:
            return response_dict
        else:
            return response_dict['study']

    def study_participants_get(self, study_id, return_response=False):
        '''Get a list of study participants

        Args:
            study_id (int): study id

        Returns:
            list or dict: list of participants or backend response parsed as 
            JSON, depending on return_response
            
        Raises:
            gencove.errors.HTTPError: on HTTP response with an erroneous 
                status_code
            gencove.errors.NoJSONInResponseError: in case JSON cannot be parsed
            gencove.errors.NotLoggedInError: if not logged in
            gencove.errors.URLDataIncompleteError: on unknown endpoint or missing 
                incomplete keys
            TypeError: in case new auth JWT is not text
            ValueError: in case new auth JWT is not properly formatted
        '''
        response_dict = self._process_response(
            self._get(
                self.url('study_participants', {'study_id': study_id})
            )
        )

        if return_response:
            return response_dict
        else:
            return response_dict['participants']

    def study_raw_data_get(
            self, study_id, participant_ids=None, return_response=False):
        '''Get presigned links for downloading study data of participants

        Args:
            study_id (int): study id
            participant_ids (list): list of participant ids

        Returns:
            list or dict: list of raw data info or backend response parsed as 
            JSON, depending on return_response
            
        Raises:
            gencove.errors.HTTPError: on HTTP response with an erroneous 
                status_code
            gencove.errors.NoJSONInResponseError: in case JSON cannot be parsed
            gencove.errors.NotLoggedInError: if not logged in
            gencove.errors.URLDataIncompleteError: on unknown endpoint or missing 
                incomplete keys
            TypeError: in case new auth JWT is not text
            ValueError: in case new auth JWT is not properly formatted
        '''
        response_dict = self._process_response(
            self._post(
                self.url('study_raw_data', {'study_id': study_id}),
                json = {
                    'participant_ids': participant_ids
                }, 
                headers=constants.HEADER_JSON
            )
        )

        if return_response:
            return response_dict
        else:
            return response_dict['raw_data']

    def apps_get(self, return_response=False):
        '''Get all apps owned by user

        Returns:
            list or dict: list of apps or backend response parsed as JSON, 
            depending on return_response
            
        Raises:
            gencove.errors.HTTPError: on HTTP response with an erroneous 
                status_code
            gencove.errors.NoJSONInResponseError: in case JSON cannot be parsed
            gencove.errors.NotLoggedInError: if not logged in
            gencove.errors.URLDataIncompleteError: on unknown endpoint or missing 
                incomplete keys
            TypeError: in case new auth JWT is not text
            ValueError: in case new auth JWT is not properly formatted
        '''
        response_dict = self._process_response(
            self._get(
                self.url('apps')
            )
        )

        if return_response:
            return response_dict
        else:
            return response_dict['apps']

    def app_create(
            self, name, href, description, enabled=True, 
            discoverable=True, return_response=False):
        '''Create a new app that will be owned by this user

        Args:
            name (str): app name
            href (str): URL of app description
            description (str): app description
            enabled (bool): whether the app is enabled upon creation 
                [optional, default: True]
            discoverable (bool): whether the app is discoverable upon 
                creation [optional, default: True]

        Returns:
            dict: app or backend response parsed as JSON, depending on 
                return_response
            
        Raises:
            gencove.errors.HTTPError: on HTTP response with an erroneous 
                status_code
            gencove.errors.NoJSONInResponseError: in case JSON cannot be parsed
            gencove.errors.NotLoggedInError: if not logged in
            gencove.errors.URLDataIncompleteError: on unknown endpoint or missing 
                incomplete keys
            TypeError: in case new auth JWT is not text
            ValueError: in case new auth JWT is not properly formatted
        '''
        response_dict = self._process_response(
            self._post(
                self.url('apps'),
                json = {
                    'name': name,
                    'href': href,
                    'description': description,
                    'enabled': enabled,
                    'discoverable': discoverable
                }, 
                headers=constants.HEADER_JSON
            )
        )

        if return_response:
            return response_dict
        else:
            return response_dict['app']

    def app_get(self, app_id, return_response=False):
        '''Get app info

        Args:
            app_id (int): app id

        Returns:
            dict: app or backend response parsed as JSON, depending on 
                return_response
            
        Raises:
            gencove.errors.HTTPError: on HTTP response with an erroneous 
                status_code
            gencove.errors.NoJSONInResponseError: in case JSON cannot be parsed
            gencove.errors.NotLoggedInError: if not logged in
            gencove.errors.URLDataIncompleteError: on unknown endpoint or missing 
                incomplete keys
            TypeError: in case new auth JWT is not text
            ValueError: in case new auth JWT is not properly formatted
        '''
        response_dict = self._process_response(
            self._get(
                self.url('app', {'app_id': app_id})
            )
        )

        if return_response:
            return response_dict
        else:
            return response_dict['app']

    def app_update(
            self, app_id, name=None, href=None, description=None, 
            subsidy_enabled=None, enabled=None, 
            discoverable=None, return_response=False):
        '''Update app info

        Args:
            app_id (int): app id
            name (str): app name
            href (str): URL of app description
            description (str): app description
            subsidy_enabled (bool): whether subsidies are enabled for this app
            enabled (bool): whether the app is enabled
            discoverable (bool): whether the app is discoverable

        Returns:
            dict: app or backend response parsed as JSON, depending on 
                return_response
            
        Raises:
            gencove.errors.HTTPError: on HTTP response with an erroneous 
                status_code
            gencove.errors.NoJSONInResponseError: in case JSON cannot be parsed
            gencove.errors.NotLoggedInError: if not logged in
            gencove.errors.URLDataIncompleteError: on unknown endpoint or missing 
                incomplete keys
            gencove.errors.NoDataError: when all arguments but app_id are None
            TypeError: in case new auth JWT is not text
            ValueError: in case new auth JWT is not properly formatted
        '''    
        update_data = {}
        if name is not None:
            update_data['name'] = name

        if href is not None:
            update_data['href'] = href

        if description is not None:
            update_data['description'] = description

        if subsidy_enabled is not None:
            update_data['subsidy_enabled'] = subsidy_enabled

        if enabled is not None:
            update_data['enabled'] = enabled

        if discoverable is not None:
            update_data['discoverable'] = discoverable

        if len(update_data) == 0:
            raise errors.NoDataError('No data provided. Provide at least one of: name, href, description.')

        response_dict = self._process_response(
            self._put(
                self.url('app', {'app_id': app_id}),
                json = update_data, 
                headers=constants.HEADER_JSON
            )
        )

        if return_response:
            return response_dict
        else:
            return response_dict['app']

    def app_members_get(self, app_id, return_response=False):
        '''Get a list of app members

        Args:
            app_id (int): app id

        Returns:
            list or dict: list of members or backend response parsed as 
            JSON, depending on return_response
            
        Raises:
            gencove.errors.HTTPError: on HTTP response with an erroneous 
                status_code
            gencove.errors.NoJSONInResponseError: in case JSON cannot be parsed
            gencove.errors.NotLoggedInError: if not logged in
            gencove.errors.URLDataIncompleteError: on unknown endpoint or missing 
                incomplete keys
            TypeError: in case new auth JWT is not text
            ValueError: in case new auth JWT is not properly formatted
        '''
        response_dict = self._process_response(
            self._get(
                self.url('app_members', {'app_id': app_id})
            )
        )

        if return_response:
            return response_dict
        else:
            return response_dict['members']

    def app_raw_data_get(
            self, app_id, member_ids=None, external_ids=None, 
            return_response=False):
        '''Get presigned links for downloading app data of members

        Args:
            app_id (int): app id
            member_ids (list): list of member ids
            external_ids (list): list of external ids

        Returns:
            list or dict: list of raw data info or backend response parsed as 
            JSON, depending on return_response
            
        Raises:
            gencove.errors.HTTPError: on HTTP response with an erroneous 
                status_code
            gencove.errors.NoJSONInResponseError: in case JSON cannot be parsed
            gencove.errors.NotLoggedInError: if not logged in
            gencove.errors.URLDataIncompleteError: on unknown endpoint or 
                missing incomplete keys
            gencove.errors.MemberAndExternalIdsProvided: when both member and
                external ids are provided
            TypeError: in case new auth JWT is not text
            ValueError: in case new auth JWT is not properly formatted
        '''
        if member_ids and external_ids:
            raise errors.MemberAndExternalIdsProvided(
                'Please provide either member ids or external ids, but not'
                'both.')


        request_json = {}
        if member_ids is not None:
            request_json = {
                'member_ids': member_ids
            }
        if external_ids is not None:
            request_json = {
                'external_ids': external_ids
            }

        response_dict = self._process_response(
            self._post(
                self.url('app_raw_data', {'app_id': app_id}),
                json=request_json, 
                headers=constants.HEADER_JSON
            )
        )

        if return_response:
            return response_dict
        else:
            return response_dict['raw_data']


    def _frontend_version_min_get(self):
        '''Get minimum frontend version

        Currently used for testing

        Returns:
            dict: backend response parsed as JSON
            
        Raises:
            gencove.errors.HTTPError: on HTTP response with an erroneous 
                status_code
            gencove.errors.NoJSONInResponseError: in case JSON cannot be parsed
            gencove.errors.NotLoggedInError: if not logged in
            gencove.errors.URLDataIncompleteError: on unknown endpoint or missing 
                incomplete keys
            TypeError: in case new auth JWT is not text
            ValueError: in case new auth JWT is not properly formatted
        '''
        return self._process_response(
            self._get(
                self.url('frontend_version_min'),
                headers=constants.HEADER_JSON
            )
        )
