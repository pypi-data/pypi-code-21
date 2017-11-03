"""
Controllers module of the api
"""

import sys
from functools import wraps

from messente.verigator import routes, models, client

PY2 = sys.version_info.major == 2


def _validate_input(func):
    # decorator for validating that passed arguments are all string
    @wraps(func)
    def wrapper(*args):
        for arg in args[1:]:
            if not isinstance(arg, str if not PY2 else basestring):
                raise ValueError("{} should be string".format(arg))
        return func(*args)

    return wrapper


def _validate_client(func):
    # decorator for validating that passed client is RestClient
    @wraps(func)
    def wrapper(self, rest_client):
        if not isinstance(rest_client, client.RestClient):
            raise ValueError("client should be RestClient")
        return func(self, rest_client)

    return wrapper


class Services(object):
    """
    Controller for service resource
    """

    @_validate_client
    def __init__(self, rest_client):
        """

        Args:
            rest_client (client.RestClient):
        """
        self.rest_client = rest_client

    @_validate_input
    def create(self, domain, name):
        """Creates new service.

        Args:
            domain (str): The domain name.

            name (str): The name of the service.

        Returns:
            models.Service: created service

        """
        json = {
            'fqdn': domain,
            'name': name
        }

        response = self.rest_client.post(routes.CREATE_SERVICE, json=json)
        return self.__service_from_json(response)

    @_validate_input
    def get(self, id):
        """Fetches service with a given id from the server.

        Args:
            id (str): The id of the service

        Returns:
            models.Service: Fetched service

        """
        response = self.rest_client.get(routes.GET_SERVICE.format(id))

        return self.__service_from_json(response)

    @_validate_input
    def delete(self, id):
        """Deletes service with id

        Args:
            id (str): service id

        Returns:
            bool:

        """
        self.rest_client.delete(routes.DELETE_SERVICE.format(id))
        return True

    @staticmethod
    def __service_from_json(json):
        return models.Service(json['id'], json['ctime'], json['name'])


# noinspection PyShadowingBuiltins
class Users(object):
    """Controller for service resource
    """

    @_validate_client
    def __init__(self, rest_client):
        """

        Args:
            rest_client (client.RestClient):
        """
        self.rest_client = rest_client

    @_validate_input
    def get_all(self, service_id):
        """Fetches all users for the given service

        Args:
            service_id (str): service id to search users for

        Returns:
            list[models.User]: list of users

        """
        response = self.rest_client.get(routes.GET_USERS.format(service_id))

        return [self.__user_from_json(user) for user in response['users']]

    @_validate_input
    def get(self, service_id, id):
        """Fetches single user with given id for the given service

        Args:
            service_id (str): service id

            id (str): user id

        Returns:
            models.User: fetched user

        """
        response = self.rest_client.get(routes.GET_USER.format(service_id, id))
        return self.__user_from_json(response)

    @_validate_input
    def create(self, service_id, number, username):
        """Creates new user for the given service

        Args:
            service_id (str): service id

            number (str): users phone number, used for 2fa

            username (str): username

        Returns:
            models.User: created user

        """

        route = routes.CREATE_USER.format(service_id)
        json = {
            "phone_number": number,
            "id_in_service": username
        }

        response = self.rest_client.post(route, json=json)
        return self.__user_from_json(response)

    @_validate_input
    def delete(self, service_id, id):
        """Deleted user with given id for the given service

        Args:
            service_id (str): service id

            id (str): user id

        Returns:
            bool: True on success raises exception on error

        """
        self.rest_client.delete(routes.DELETE_USER.format(service_id, id))

        return True

    @staticmethod
    def __user_from_json(json):
        return models.User(json['id'], json['ctime'], json['id_in_service'])


class Auth(object):
    """Controller for service resource

    """

    METHOD_SMS = "sms"
    METHOD_TOTP = "totp"

    @_validate_client
    def __init__(self, rest_client):
        """

        Args:
            rest_client (client.RestClient):
        """
        self.rest_client = rest_client

    @_validate_input
    def initiate(self, service_id, user_id, method):
        """Initiates authentication process
        sends sms in case of sms authentication

        Args:
            service_id (str): service id

            user_id (str): user id

            method (str): auth method (sms or totp) use Auth.METHOD_SMS or Auth.METHOD_TOTP

        Note:
            System will automatically fall back from TOTP to SMS if user has no devices attached to the number

        """
        route = routes.AUTH_INITIATE.format(service_id, user_id)
        json = {"method": method}

        self.rest_client.post(route, json=json)

    @_validate_input
    def verify(self, service_id, user_id, token):
        """Verifies user input validity

        Args:
            service_id (str): service id

            user_id (str): user id

            token (str): user provided token

        Returns:
            bool: boolean indicating verification status

        """

        route = routes.AUTH_VERIFY.format(service_id, user_id)
        json = {"token": token}

        response = self.rest_client.put(route, json=json)

        verified = response['verified']

        return verified
