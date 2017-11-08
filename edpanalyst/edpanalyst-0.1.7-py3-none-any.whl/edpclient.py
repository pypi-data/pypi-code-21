from typing import Any, Dict, List, NamedTuple, Optional  # NOQA
from typing import Text
import os
import re

from configparser import RawConfigParser  # type: ignore
from six.moves.urllib.parse import quote, unquote
import requests

from .population_schema import PopulationSchema  # NOQA

ID_REGEX = '^[a-z]+-[a-z0-9]{16}$'  # matches pids and pmids

VisibilityTuple = NamedTuple('Visibility', [('owner', str), ('public', bool),
                                            ('readers', List[str]),
                                            ('reader_domains', List[str])])
"""The visibility of a population or population model"""


class Visibility(VisibilityTuple):

    @staticmethod
    def from_json(json):  # type: (Dict[str, Any]) -> Visibility
        return Visibility(json['owner'], json['public'], json['readers'],
                          json['reader_domains'])


_Config = NamedTuple('_Config', [('edp_url', str), ('bearer_token', Text)])
"""Authentication configuration from ~/.edp_auth or EdpClient.__init__"""


class EdpClient(object):
    """Provides a python API to the Empirical Data Platform."""

    def __init__(
            self,
            profile=None,  # type: str
            edp_url=None,  # type: str
            bearer_token=None  # type: Text
    ):  # type: (...) -> None
        """Create an EDP client.

        This class is thread-safe if requests.Session is thread-safe. It very
        much seems that it should be, but the requests developers are hesitant
        to declare it so. See
        https://github.com/kennethreitz/requests/issues/1871
        https://github.com/kennethreitz/requests/issues/2766 and
        http://stackoverflow.com/questions/18188044/is-the-session-object-from-pythons-requests-library-thread-safe
        Nevertheless, we're treating it as thread-safe until we discover
        otherwise.

        Args:
            profile: The name of a profile to use. If not provided the
                EDP_PROFILE environment variable is checked, and if not set
                then "default" profile is used.
            bearer_token: The JWT to be used for authentication soon. If not
                provided the EDP_BEARER_TOKEN environment variable is checked,
                and if not set the value from the selected profile is used.
            edp_url: An endpoint to connect to. If not set, the EDP_URL
                environment variable is checked, and if not set the value from
                the selected profile is used, and if not set then a default
                of "https://betaplatform.empirical.com" is used.
        """
        self.config = self._config(profile_name=profile, edp_url=edp_url,
                                   bearer_token=bearer_token)
        self._session = requests.Session()
        if self.config.bearer_token:
            self._session.headers.update({
                'Authorization': 'Bearer ' + self.config.bearer_token,
            })  # yapf: disable

    @staticmethod
    def _config(profile_name=None, edp_url=None, bearer_token=None):
        # type: (str, str, Text) -> _Config
        """Returns a `_Config`, looking up fields in a variety of places.

        Usually, values will come from the "default" profile in ~/.edp_auth,
        which can be overridden by either `profile_name` or, if that is unset,
        `EDP_PROFILE` in the environment.

        You can override individual `_Config` fields by passing arguments to
        this constructor, which passes them to this function.
        """
        profile_name = profile_name or os.environ.get('EDP_PROFILE', 'default')
        config = EdpClient._read_edp_auth(profile_name)
        edp_url = (edp_url or os.environ.get('EDP_URL') or
                   config.get('edp_url') or
                   'https://betaplatform.empirical.com')
        bearer_token = (bearer_token or os.environ.get('EDP_BEARER_TOKEN') or
                        config.get('bearer_token'))
        if not bearer_token:
            raise ValueError(
                'No bearer_token was found in %r section of %r or '
                'the EDP_BEARER_TOKEN environment variable, nor '
                'passed to EdpClient constructor.' %
                (profile_name, EdpClient._config_path()))
        return _Config(edp_url=edp_url, bearer_token=bearer_token)

    @staticmethod
    def _read_edp_auth(profile_name):
        # type: (str) -> Dict[str, Any]
        """Returns the named section of ~/.edp_auth or {} if not found."""
        config_path = EdpClient._config_path()
        if not os.path.isfile(config_path):
            return {}
        config = RawConfigParser()
        config.read(config_path)
        if profile_name not in config.sections():
            return {}
        return dict(config.items(profile_name))

    @staticmethod
    def _config_path():  # type: () -> str
        """Return the path to the configuration file based on os and
        environment."""
        default = os.path.expanduser(os.path.join('~', '.edp_auth'))
        return os.environ.get('EDP_CONFIG_FILE', default)

    def get_username(self):  # type: () -> str
        """Get the authenticated user's email address."""
        resp = self._session.get(self.config.edp_url + '/auth/username')
        _raise_for_error(resp)
        return resp.text

    def upload_population(
            self,
            data,  # type: Dict[str, List[Optional[str]]]
            name,  # type: str
            schema=None,  # type: PopulationSchema
            hints=None,  # type: Dict[str, Any]
            this_is_a_lot_of_data_but_i_know_what_im_doing=False  # type: bool
    ):  # type: (...) -> str
        """Upload a population to EDP.

        Returns:
            str: The ID of the newly uploaded population.

        Args:
            data: The data to be uploaded.
            schema: A schema describing the uploaded data.
            name: Name of the newly created population.
        """
        url = self.config.edp_url + '/rpc/population'
        if len(data) == 0:
            raise ValueError('`data` must not be empty')
        if name is None:
            raise ValueError('`name` must not be None')
        # Grab an arbitrary row's length. If the row lengths are inconsistent
        # the server will yell at us.
        num_rows = len(list(data.values())[0])
        postdata = {
            'name': name,
            'data': {
                'num_rows': num_rows,
                'columns': data
            },
        }  # type: Dict[str, Any]
        if schema:
            postdata['schema'] = schema.to_json()
        if hints:
            postdata['hints'] = hints
        if this_is_a_lot_of_data_but_i_know_what_im_doing:
            postdata['this_is_a_lot_of_data_but_i_know_what_im_doing'] = True
        resp = self._session.post(url, json=postdata)
        _raise_for_error(resp)
        return _artifact_id_from_response(resp)

    # TODO(asilvers): This is only hanging around because we use it in tests.
    # Delete it after that.
    def _upload_population_as_generator(self, generator, name,
                                        parent_pid=None):
        # type: (bytes, str, str) -> str
        """Upload a population (as a generator) to EDP."""
        if not isinstance(generator, bytes):
            raise ValueError('generator must be a bytes')
        edp_url = self.config.edp_url
        if parent_pid is None:
            url = edp_url + '/rpc/population_model/upload_generator'
        else:
            url = edp_url + '/rpc/population/%s/upload_generator' % (
                quote(parent_pid),)
        # The (None, 'foo') syntax is request.post's way of passing non-file
        # params in a multipart/form-data request.
        formdata = {'name': (None, name), 'file': generator}
        resp = self._session.post(url, files=formdata)
        _raise_for_error(resp)
        return _artifact_id_from_response(resp)


class CallableEndpoint(object):
    """A helper class to make it easy to mock out HTTP calls.

    Call like:
        endpoint = CallableEndpoint('http://test.com/base', session)
        endpoint.logpdf_rows.post(json=request)
    and it will issue:
        session.post('http://test.com/base/logpdf_rows', json=request)

    Unlike just using requests, this will automatically raise on HTTP error
    codes. If for some reason you need that to not happen I'd be ok adding a
    `autoraise` parameter to the methods.
    """

    def __init__(
            self,
            url,  # type: str
            session  # type: requests.Session
    ):  # type: (...) -> None
        self.url = url
        self._session = session

    def get(self, *args, **kwargs):
        resp = self._session.get(self.url, *args, **kwargs)
        _raise_for_error(resp)
        return resp

    def post(self, *args, **kwargs):
        resp = self._session.post(self.url, *args, **kwargs)
        _raise_for_error(resp)
        return resp

    def patch(self, *args, **kwargs):
        resp = self._session.patch(self.url, *args, **kwargs)
        _raise_for_error(resp)
        return resp

    def delete(self, *args, **kwargs):
        resp = self._session.delete(self.url, *args, **kwargs)
        _raise_for_error(resp)
        return resp

    # This isn't just an attempt to make a cute API. It'd be less strange to
    # have a `sub_url()` method that did this, but python's mock can't mock
    # based on args, so you couldn't mock `ce.sub_url('select')` and
    # `ce.sub_url('logpdf_rows')` separately. This gets around that by letting
    # you mock `ce.select` and `ce.logpdf_rows`.
    def __getattr__(self, attr):
        new_url = self.url + '/' + quote(attr)
        return CallableEndpoint(new_url, self._session)


def _artifact_id_from_response(resp):  # type: (requests.Response) -> str
    """Figure out the id of the population or model.

    This should be the last part of the path of the URL.
    """
    # This obviously depends on the format of the URL in the response, but so
    # does actually constructing the URLs when making the requests, so it's not
    # horrendous.
    #
    # TODO(asilvers): Really though this is going to break if/when we start
    # appending colon-separated names to the URLs. We should probably just
    # return the ID in another header. I wonder if there's a standard for that.
    location = unquote(resp.headers['location'])
    artifact_id = location.split('/')[-1]
    assert re.match(ID_REGEX, artifact_id)
    return artifact_id


def _raise_for_error(response):
    """Raise an error if response indicates an HTTP error code.

    Like requests.raise_for_status(), but additionally tries to raise a
    more sensible error if we can parse out what happened from the response.

    Raises:
        NoSuchGeneratorError: If the response was a 404
        ValueError: If the request was bad due to user error, e.g. bad columns
            or too large a sample size
        HTTPError: If the response is any other 4XX or 5XX error
    """
    # TODO(asilvers): This may turn some other 404s into NoSuchGeneratorErrors
    # if, say, we start building bad URLs and 404ing due to structural issues
    # in the requests. We should work out a signalling this exact case in the
    # body of the 404 to get rid of that ambiguity.
    if response.status_code == 404:
        raise NoSuchGeneratorError
    if response.status_code == 401:
        raise AuthenticationError(
            'You are not authenticated to EDP. Do you have a token from '
            'https://betaplatform.empirical.com/tokens?')
    if response.status_code == 403:
        raise PermissionDeniedError(
            'You do not have access to the requested resource on EDP.')
    if response.status_code == 400:
        # Some errors return nice json for us
        try:
            respjson = response.json()
            error = respjson['error']
        except ValueError:
            # But if not, raise a ValueError and hope that there was some
            # useful text in the HTML. It's better than swallowing the response
            # text which is what `raise_for_status` does.
            raise ValueError(response.content)
        if error == 'MODEL_NOT_BUILT':
            raise ModelNotBuiltError('This model has not finished building.')
        if error == 'N_TOO_LARGE':
            raise ValueError('Request\'s \'n\' was too large.')
        if error == 'NO_SUCH_COLUMN':
            raise ValueError('No such column in %s: %s' %
                             (respjson['field'], respjson['columns']))
        # Got JSON but we're not handling its error code. Still better than
        # raising a 400.
        raise ValueError(respjson)
    response.raise_for_status()


class EdpError(Exception):
    pass


class NoSuchGeneratorError(EdpError):
    pass


class ModelNotBuiltError(EdpError):
    pass


class PermissionDeniedError(EdpError):
    pass


class AuthenticationError(EdpError):
    pass
