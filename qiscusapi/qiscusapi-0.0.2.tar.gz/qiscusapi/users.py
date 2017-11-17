#!/usr/bin env python3
"""
Python wrapper for Qiscus SDK RESTful API
"""
import json
from requests import post, get


class Response():
    pass


class Users:
    def __init__(self):
        self.secret_key = None
        self.base_url = None

    def login_or_register(self, email, username, password=None, avatar_url=None,
                          device_token=None, device_platform=None):
        """
        This method used to create new user if it does not exist yet,
        or you can use this endpoint to update data (password, username, avatar url,
        device token, device platform) of the user if they already exists

        :param email: user email
        :type email: str
        :param password: optional parameter. Password will be updated if user already exist
        :type password: str
        :param username: you can also update username with this parameter.
        :type username: str
        :param avatar_url: optional
        :type avatar_url: str
        :param device_token: optional
        :type device_token: str
        :param device_platform: optional, you can use "ios" or "android" as device platform
        :type device_platform: str
        :return: it will return to object named user.
        .. note:: Note : password is optional, it will generate random string on the backend
        if you dont pass it during User creation through this API. However, please note for
        those users already created you can not use this API login_or_register without
        passing password value
        """
        headers = {
            'QISCUS_SDK_SECRET': self.secret_key
        }

        data = {
            'email': email,
            'username': username,
            'password': password,
            'avatar_url': avatar_url,
            'device_token': device_token,
            'device_platform': device_platform
        }

        url = self.base_url + 'login_or_register'
        requests = post(url, data=data, headers=headers)
        if 200 <= requests.status_code < 400:
            result = requests.json()
            user = Response()
            user.user_id = result['results']['user']['id']
            user.user_email = result['results']['user']['email']
            user.username = result['results']['user']['username']
            user.user_avatar_url = result['results']['user']['avatar_url']
            user.user_token = result['results']['user']['token']
            user.info_as_json = json.dumps(requests.json())
            return user
        else:
            result = requests.json()
            user = Response()
            user.error_message = result['error']['message']
            user.status_code = requests.status_code
            user.info_as_json = json.dumps(requests.json())
            return user

    def get_user_profile(self, user_email):
        """
        This method used to check user profile enpoint.

        :param user_email: user_email
        :type user_email: str
        :return: json
        """
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key
        }

        url = self.base_url + 'user_profile?user_email=' + user_email
        requests = get(url, headers=headers)
        if 200 <= requests.status_code < 400:
            result = requests.json()
            user = Response()
            user.user_id = result['results']['user']['id']
            user.user_email = result['results']['user']['email']
            user.username = result['results']['user']['username']
            user.user_avatar_url = result['results']['user']['avatar_url']
            user.user_token = result['results']['user']['token']
            user.info_as_json = json.dumps(requests.json())
            return user
        else:
            result = requests.json()
            user = Response()
            user.error_message = result['error']['message']
            user.status_code = requests.status_code
            user.info_as_json = json.dumps(requests.json())
            return user

    def reset_user_token(self, user_email):
        """
        Reset User Authentication Token
        In case your user token is compromised, you can reset their token at any time.
        This make previous token no longer valid.

        Request parameter
        :param user_email [string] user email to reset
        """
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key
        }
        data = {
            "user_email": user_email
        }

        url = self.base_url + 'reset_user_token'
        requests = post(url, data=data, headers=headers)
        result = requests.json()
        if 200 <= requests.status_code < 400:
            user = Response()
            user.app_code = result['results']['user']['app']['code']
            user.app_id = result['results']['user']['app']['id']
            user.app_name = result['results']['user']['app']['name']
            user.user_app_info_json = result['results']['user']['app']
            user.user_avatar_url = result['results']['user']['avatar_url']
            user.user_email = result['results']['user']['email']
            user.user_id = result['results']['user']['id']
            user.user_last_comment_id = result['results']['user']['last_comment_id']
            user.user_pn_android_configured = result['results']['user']['pn_android_configured']
            user.user_pn_ios_configured = result['results']['user']['pn_ios_configured']
            user.user_rtKey = result['results']['user']['rtKey']
            user.user_token = result['results']['user']['token']
            user.username = result['results']['user']['username']
            user.info_as_json = json.dumps(requests.json())
            return user
        else:
            user = Response()
            user.error_message = result['error']['message']
            user.status_code = requests.status_code
            user.info_as_json = json.dumps(requests.json())
            return user

    def get_user_room_lists(self, user_email, page='1', show_participants='false'):
        """

        :type show_participants: object
        :param user_email:
        :param page:
        :param show_participants:
        :return:
        """
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key
        }

        url = self.base_url + 'get_user_rooms?user_email=' + user_email + \
              '&page=' + page + '&show_participants=' + show_participants
        requests = get(url, headers=headers)
        result = requests.json()
        if 200 <= requests.status_code < 400:
            rooms = Response()
            rooms.current_page = result['results']['meta']['current_page']
            rooms.total_room = result['results']['meta']['total_room']
            rooms_info = []
            for i in result['results']['rooms_info']:
                room = Response()
                room.room_last_comment_id = i['last_comment_id']
                room.room_last_comment_message = i['last_comment_message']
                room.room_last_comment_timestamp = i['last_comment_timestamp']
                room.room_avatar_url = i['room_avatar_url']
                room.room_id = i['room_id']
                room.room_name = i['room_name']
                room.room_type = i['room_type']
                room.room_unread_count = i['unread_count']
                room.info_as_json = json.dumps(result['results']['rooms_info'])
                rooms_info.append(room)
            rooms.rooms_info = rooms_info
            rooms.info_as_json = json.dumps(requests.json())
            return rooms
        else:
            rooms = Response()
            rooms.error_message = result['error']['message']
            rooms.status_code = requests.status_code
            rooms.info_as_json = json.dumps(requests.json())
            return rooms
