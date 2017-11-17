from urllib.parse import urljoin
from collections import namedtuple

import requests


TRUNITY_2_API_ENDPOINT = "http://api.trunity.net/v1/"
# TRUNITY_2_API_ENDPOINT = "http://api2.trunity.net/v1/"
TRUNITY_2_APP_CODE = 'afb7a0a03ef25600d5d88d7df33884d0'


HEADERS = {
    'Application': TRUNITY_2_APP_CODE,
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
}

session = requests.Session()
session.headers.update(HEADERS)


UserData = namedtuple(
    'UserData',
    ['user_id', 'auth_code', 'first_name', 'last_name']
    )


def _get_full_url(tail: str) -> str:
    return urljoin(TRUNITY_2_API_ENDPOINT, tail)


class Login(object):

    @staticmethod
    def application_provision(params):
        # TODO: implement
        """
        Setup a new application that will make requests to the Trunity API.
        The application serves as the client for the API requests and must be
         explicitly identified with each call.
        """
        pass

    @staticmethod
    def login_a_user(user_name: str, user_password: str) -> UserData:
        """
        Logs in a user and returns an authCode for subsequent calls to identify the user.

        :param user_name:
        :param user_password:
        :return: UserData
        """

        url_tail = 'users/login'

        request_data = {
            'userName': user_name,
            'userPassword': user_password
        }

        url = _get_full_url(url_tail)

        response = session.post(url, request_data)
        response.raise_for_status()
        response_data = response.json()

        return UserData(
            user_id=response_data['userId'],
            auth_code=response_data['authCode'],
            first_name=response_data['firstName'],
            last_name=response_data['lastName'],
        )

    @staticmethod
    def validate_a_user_auth_code():
        # TODO:
        pass


class SiteType(object):
    """
    Types of Sites on Trunity 2
    """
    TEXTBOOK = "Textbook"
    COURSE = "Course"
    COLLECTION = "Collection"
    BOOKS_AND_COURSES = "BooksAndCourses"

    ALL = "All"


class Client(object):

    def __init__(self, user_name, password):
        user_data = Login.login_a_user(user_name=user_name,
                                       user_password=password)

        self.user_id = user_data.user_id
        self.auth_code = user_data.auth_code

    def get_user_sites(self, site_type: str):
        """
        Gets a list of sites a user belongs to.
        Returns an List of Dict objects with information about each site

        :param site_type:
        :return: [
                    {
                    'rootTopic': '53a81ac50cf226e0bdc00a37',
                    'role': 'Managing Editor',
                    'type': 'Textbook',
                    'siteId': '10202',
                    'name': '16_cnx_collection'
                    }
                ]
        """
        url = _get_full_url('users/sites')

        request_data = {
            "authCode": self.auth_code,
            "siteType": site_type,
        }

        response = session.get(url, params=request_data)
        response.raise_for_status()

        response_data = response.json()
        return response_data

    def get_topics_for_a_site(self, site_id: str, topic_id=None):
        """
        Gets all of the topics attached to a specific topic.

        If no topic_id is specified, it will get all of the topics attached to
        the root of the site

        :param site_id:
        :param topic_id:
        :return: [
                   {
                      '_id': '53a81af80cf226e0bdc00a3e',
                      'joinType': 'selected',
                      'title': 'Welcome to Economics!',
                      'type': 'topics'
                      },
                  ]
        """

        url = _get_full_url('sites/{site_id}/topics').format(site_id=site_id)

        request_params = {
            'authCode': self.auth_code,
            'topicId': topic_id,
        }
        request = session.get(url, params=request_params)
        request.raise_for_status()
        response_data = request.json()
        return response_data

    def get_a_topic(self, site_id, topic_id):
        """
        Gets the information for a topic. The information describes not only
        the topic itself, but will also list any content or topics that have
        been joined to the topic.
        """

        url = _get_full_url('sites/{site_id}/topics/{topic_id}').format(
            site_id=site_id,
            topic_id=topic_id,
        )

        request_params = {
            "authCode": self.auth_code,
        }
        response = session.get(url, params=request_params)
        response.raise_for_status()
        response_data = response.json()
        return response_data

    def get_topic_joins(self, site_id, topic_id):
        """
        Gets all of the topics and content associated with a specific topic.

        :param site_id:
        :param topic_id:
        :return:
        """

        url = _get_full_url('sites/{site_id}/topics/{topic_id}/all').format(
            site_id=site_id,
            topic_id=topic_id,
        )

        request_params = {
            "authCode": self.auth_code,
        }
        response = session.get(url, params=request_params)
        response.raise_for_status()
        response_data = response.json()
        return response_data

    def get_content(self, site_id, content_id):
        """
        Gets the most recent published version of a specific piece of content.
        Content will consist of at least an _id and a content field.
        Depending on the type of content, the content field will contain a JSON
        Object with various additional fields set.

        :param site_id:
        :param content_id:
        :return:
        """

        url = _get_full_url('view/{content_id}/').format(
            content_id=content_id,
        )

        request_params = {"authCode": self.auth_code, "siteId": site_id}

        response = session.get(url, params=request_params)
        response.raise_for_status()
        response_data = response.json()
        return response_data



