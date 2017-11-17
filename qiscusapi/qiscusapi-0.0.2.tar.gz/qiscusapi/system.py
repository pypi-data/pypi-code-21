#!/usr/bin env python3
"""
Python wrapper for Qiscus SDK RESTful API
"""
import json
from requests import post


class Response():
    pass


class System(object):
    def __init__(self):
        self.secret_key = None
        self.base_url = None

    def create_room_system_event_message(self, room_id, subject_email,
                                         updated_room_name, _system_event_type='create_room'):
        """
        Create room type post system event message. it can be used to return
        system event message whenever you create room.

        :param room_id:
        :param subject_email:
        :param updated_room_name:
        :param _system_event_type:
        :return:

        example response payload:
            ...
            message: "Ucup created room 'Qiscus'",
            payload: {
                "type": "create_room",
                "subject_username": "Ucup",
                "subject_email": "ucup@qiscus.com",
                "room_name": "Qiscus"
            },
            ...
        """
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key
        }

        data = {
            "system_event_type": _system_event_type,
            "room_id": room_id,
            "subject_email": subject_email,
            "updated_room_name": updated_room_name
        }

        url = self.base_url + 'post_system_event_message'
        requests = post(url, data=data, headers=headers)
        result = requests.json()
        if 200 <= requests.status_code < 400:
            comment = Response()
            comment.comment_before_id = json.dumps(result['results']['comment']['comment_before_id'])
            comment.disable_link_preview = json.dumps(result['results']['comment']['disable_link_preview'])
            comment.email = json.dumps(result['results']['comment']['email'])
            comment.comment_id = json.dumps(result['results']['comment']['id'])
            comment.message = json.dumps(result['results']['comment']['message'])
            comment.payload = json.dumps(result['results']['comment']['payload'])
            comment.room_id = json.dumps(result['results']['comment']['room_id'])
            comment.comment_status = json.dumps(result['results']['comment']['status'])
            comment.timestamp = json.dumps(result['results']['comment']['timestamp'])
            comment.topic_id = json.dumps(result['results']['comment']['topic_id'])
            comment.type = json.dumps(result['results']['comment']['type'])
            comment.unique_temp_id = json.dumps(result['results']['comment']['unique_temp_id'])
            comment.unix_nano_timestamp = json.dumps(result['results']['comment']['unix_nano_timestamp'])
            comment.unix_timestamp = json.dumps(result['results']['comment']['unix_timestamp'])
            comment.user_avatar_url = json.dumps(result['results']['comment']['user_avatar_url'])
            comment.user_id = json.dumps(result['results']['comment']['user_id'])
            comment.username = json.dumps(result['results']['comment']['username'])
            comment.as_json = json.dumps(requests.json())
            return comment
        else:
            comment = Response()
            comment.error_message = json.dumps(result['error']['message'])
            comment.status_code = json.dumps(requests.status_code)
            comment.as_json = json.dumps(requests.json())
            return comment

    def change_room_name_system_event_message(self, room_id, subject_email,
                                              updated_room_name,
                                              _system_event_type='change_room_name'):
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key
        }

        data = {
            "system_event_type": _system_event_type,
            "room_id": room_id,
            "subject_email": subject_email,
            "updated_room_name": updated_room_name
        }

        url = self.base_url + 'post_system_event_message'
        requests = post(url, data=data, headers=headers)
        result = requests.json()
        if 200 <= requests.status_code < 400:
            comment = Response()
            comment.comment_before_id = json.dumps(result['results']['comment']['comment_before_id'])
            comment.disable_link_preview = json.dumps(result['results']['comment']['disable_link_preview'])
            comment.email = json.dumps(result['results']['comment']['email'])
            comment.comment_id = json.dumps(result['results']['comment']['id'])
            comment.message = json.dumps(result['results']['comment']['message'])
            comment.payload = json.dumps(result['results']['comment']['payload'])
            comment.room_id = json.dumps(result['results']['comment']['room_id'])
            comment.comment_status = json.dumps(result['results']['comment']['status'])
            comment.timestamp = json.dumps(result['results']['comment']['timestamp'])
            comment.topic_id = json.dumps(result['results']['comment']['topic_id'])
            comment.type = json.dumps(result['results']['comment']['type'])
            comment.unique_temp_id = json.dumps(result['results']['comment']['unique_temp_id'])
            comment.unix_nano_timestamp = json.dumps(result['results']['comment']['unix_nano_timestamp'])
            comment.unix_timestamp = json.dumps(result['results']['comment']['unix_timestamp'])
            comment.user_avatar_url = json.dumps(result['results']['comment']['user_avatar_url'])
            comment.user_id = json.dumps(result['results']['comment']['user_id'])
            comment.username = json.dumps(result['results']['comment']['username'])
            comment.as_json = json.dumps(requests.json())
            return comment
        else:
            comment = Response()
            comment.error_message = json.dumps(result['error']['message'])
            comment.status_code = json.dumps(requests.status_code)
            comment.as_json = json.dumps(requests.json())
            return comment

    def change_room_avatar_system_event_message(self, room_id, subject_email,
                                                _system_event_type='change_room_avatar'):
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key
        }

        data = {
            "system_event_type": _system_event_type,
            "room_id": room_id,
            "subject_email": subject_email,
        }

        url = self.base_url + 'post_system_event_message'
        requests = post(url, data=data, headers=headers)
        result = requests.json()
        if 200 <= requests.status_code < 400:
            comment = Response()
            comment.comment_before_id = json.dumps(result['results']['comment']['comment_before_id'])
            comment.disable_link_preview = json.dumps(result['results']['comment']['disable_link_preview'])
            comment.email = json.dumps(result['results']['comment']['email'])
            comment.comment_id = json.dumps(result['results']['comment']['id'])
            comment.message = json.dumps(result['results']['comment']['message'])
            comment.payload = json.dumps(result['results']['comment']['payload'])
            comment.room_id = json.dumps(result['results']['comment']['room_id'])
            comment.comment_status = json.dumps(result['results']['comment']['status'])
            comment.timestamp = json.dumps(result['results']['comment']['timestamp'])
            comment.topic_id = json.dumps(result['results']['comment']['topic_id'])
            comment.type = json.dumps(result['results']['comment']['type'])
            comment.unique_temp_id = json.dumps(result['results']['comment']['unique_temp_id'])
            comment.unix_nano_timestamp = json.dumps(result['results']['comment']['unix_nano_timestamp'])
            comment.unix_timestamp = json.dumps(result['results']['comment']['unix_timestamp'])
            comment.user_avatar_url = json.dumps(result['results']['comment']['user_avatar_url'])
            comment.user_id = json.dumps(result['results']['comment']['user_id'])
            comment.username = json.dumps(result['results']['comment']['username'])
            comment.as_json = json.dumps(requests.json())
            return comment
        else:
            comment = Response()
            comment.error_message = json.dumps(result['error']['message'])
            comment.status_code = json.dumps(requests.status_code)
            comment.as_json = json.dumps(requests.json())
            return comment

    def add_member_system_event_message(self, room_id, subject_email,
                                        object_email, _system_event_type='add_member'):
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key
        }

        data = {
            "system_event_type": _system_event_type,
            "room_id": room_id,
            "subject_email": subject_email,
            "object_email[]": object_email
        }

        url = self.base_url + 'post_system_event_message'
        requests = post(url, data=data, headers=headers)
        result = requests.json()
        if 200 <= requests.status_code < 400:
            comment = Response()
            comment.comment_before_id = json.dumps(result['results']['comment']['comment_before_id'])
            comment.disable_link_preview = json.dumps(result['results']['comment']['disable_link_preview'])
            comment.email = json.dumps(result['results']['comment']['email'])
            comment.comment_id = json.dumps(result['results']['comment']['id'])
            comment.message = json.dumps(result['results']['comment']['message'])
            comment.payload = json.dumps(result['results']['comment']['payload'])
            comment.room_id = json.dumps(result['results']['comment']['room_id'])
            comment.comment_status = json.dumps(result['results']['comment']['status'])
            comment.timestamp = json.dumps(result['results']['comment']['timestamp'])
            comment.topic_id = json.dumps(result['results']['comment']['topic_id'])
            comment.type = json.dumps(result['results']['comment']['type'])
            comment.unique_temp_id = json.dumps(result['results']['comment']['unique_temp_id'])
            comment.unix_nano_timestamp = json.dumps(result['results']['comment']['unix_nano_timestamp'])
            comment.unix_timestamp = json.dumps(result['results']['comment']['unix_timestamp'])
            comment.user_avatar_url = json.dumps(result['results']['comment']['user_avatar_url'])
            comment.user_id = json.dumps(result['results']['comment']['user_id'])
            comment.username = json.dumps(result['results']['comment']['username'])
            comment.as_json = json.dumps(requests.json())
            return comment
        else:
            comment = Response()
            comment.error_message = json.dumps(result['error']['message'])
            comment.status_code = json.dumps(requests.status_code)
            comment.as_json = json.dumps(requests.json())
            return comment

    def remove_member_system_event_message(self, room_id, subject_email,
                                           object_email, _system_event_type='remove_member'):
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key
        }

        data = {
            "system_event_type": _system_event_type,
            "room_id": room_id,
            "subject_email": subject_email,
            "object_email[]": object_email
        }

        url = self.base_url + 'post_system_event_message'
        requests = post(url, data=data, headers=headers)
        result = requests.json()
        if 200 <= requests.status_code < 400:
            comment = Response()
            comment.comment_before_id = json.dumps(result['results']['comment']['comment_before_id'])
            comment.disable_link_preview = json.dumps(result['results']['comment']['disable_link_preview'])
            comment.email = json.dumps(result['results']['comment']['email'])
            comment.comment_id = json.dumps(result['results']['comment']['id'])
            comment.message = json.dumps(result['results']['comment']['message'])
            comment.payload = json.dumps(result['results']['comment']['payload'])
            comment.room_id = json.dumps(result['results']['comment']['room_id'])
            comment.comment_status = json.dumps(result['results']['comment']['status'])
            comment.timestamp = json.dumps(result['results']['comment']['timestamp'])
            comment.topic_id = json.dumps(result['results']['comment']['topic_id'])
            comment.type = json.dumps(result['results']['comment']['type'])
            comment.unique_temp_id = json.dumps(result['results']['comment']['unique_temp_id'])
            comment.unix_nano_timestamp = json.dumps(result['results']['comment']['unix_nano_timestamp'])
            comment.unix_timestamp = json.dumps(result['results']['comment']['unix_timestamp'])
            comment.user_avatar_url = json.dumps(result['results']['comment']['user_avatar_url'])
            comment.user_id = json.dumps(result['results']['comment']['user_id'])
            comment.username = json.dumps(result['results']['comment']['username'])
            comment.as_json = json.dumps(requests.json())
            return comment
        else:
            comment = Response()
            comment.error_message = json.dumps(result['error']['message'])
            comment.status_code = json.dumps(requests.status_code)
            comment.error_info_json = json.dumps(requests.json())
            return comment

    def join_room_system_event_message(self, room_id, subject_email,
                                       _system_event_type='join_room'):
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key
        }

        data = {
            "system_event_type": _system_event_type,
            "room_id": room_id,
            "subject_email": subject_email,
        }

        url = self.base_url + 'post_system_event_message'
        requests = post(url, data=data, headers=headers)
        result = requests.json()
        if 200 <= requests.status_code < 400:
            comment = Response()
            comment.comment_before_id = json.dumps(result['results']['comment']['comment_before_id'])
            comment.disable_link_preview = json.dumps(result['results']['comment']['disable_link_preview'])
            comment.email = json.dumps(result['results']['comment']['email'])
            comment.comment_id = json.dumps(result['results']['comment']['id'])
            comment.message = json.dumps(result['results']['comment']['message'])
            comment.payload = json.dumps(result['results']['comment']['payload'])
            comment.room_id = json.dumps(result['results']['comment']['room_id'])
            comment.comment_status = json.dumps(result['results']['comment']['status'])
            comment.timestamp = json.dumps(result['results']['comment']['timestamp'])
            comment.topic_id = json.dumps(result['results']['comment']['topic_id'])
            comment.type = json.dumps(result['results']['comment']['type'])
            comment.unique_temp_id = json.dumps(result['results']['comment']['unique_temp_id'])
            comment.unix_nano_timestamp = json.dumps(result['results']['comment']['unix_nano_timestamp'])
            comment.unix_timestamp = json.dumps(result['results']['comment']['unix_timestamp'])
            comment.user_avatar_url = json.dumps(result['results']['comment']['user_avatar_url'])
            comment.user_id = json.dumps(result['results']['comment']['user_id'])
            comment.username = json.dumps(result['results']['comment']['username'])
            comment.as_json = json.dumps(requests.json())
            return comment
        else:
            comment = Response()
            comment.error_message = json.dumps(result['error']['message'])
            comment.status_code = json.dumps(requests.status_code)
            comment.as_json = json.dumps(requests.json())
            return comment

    def left_room_system_event_message(self, room_id, subject_email,
                                       _system_event_type='left_room'):
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key
        }

        data = {
            "system_event_type": _system_event_type,
            "room_id": room_id,
            "subject_email": subject_email,
        }

        url = self.base_url + 'post_system_event_message'
        requests = post(url, data=data, headers=headers)
        result = requests.json()
        if 200 <= requests.status_code < 400:
            comment = Response()
            comment.comment_before_id = json.dumps(result['results']['comment']['comment_before_id'])
            comment.disable_link_preview = json.dumps(result['results']['comment']['disable_link_preview'])
            comment.email = json.dumps(result['results']['comment']['email'])
            comment.comment_id = json.dumps(result['results']['comment']['id'])
            comment.message = json.dumps(result['results']['comment']['message'])
            comment.payload = json.dumps(result['results']['comment']['payload'])
            comment.room_id = json.dumps(result['results']['comment']['room_id'])
            comment.comment_status = json.dumps(result['results']['comment']['status'])
            comment.timestamp = json.dumps(result['results']['comment']['timestamp'])
            comment.topic_id = json.dumps(result['results']['comment']['topic_id'])
            comment.type = json.dumps(result['results']['comment']['type'])
            comment.unique_temp_id = json.dumps(result['results']['comment']['unique_temp_id'])
            comment.unix_nano_timestamp = json.dumps(result['results']['comment']['unix_nano_timestamp'])
            comment.unix_timestamp = json.dumps(result['results']['comment']['unix_timestamp'])
            comment.user_avatar_url = json.dumps(result['results']['comment']['user_avatar_url'])
            comment.user_id = json.dumps(result['results']['comment']['user_id'])
            comment.username = json.dumps(result['results']['comment']['username'])
            comment.as_json = json.dumps(requests.json())
            return comment
        else:
            comment = Response()
            comment.error_message = json.dumps(result['error']['message'])
            comment.status_code = json.dumps(requests.status_code)
            comment.as_json = json.dumps(requests.json())
            return comment

    def custom_system_event_message(self, room_id, subject_email, message=None,
                                    payload=None, _system_event_type='custom'):
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key
        }

        data = {
            "system_event_type": _system_event_type,
            "room_id": room_id,
            "subject_email": subject_email,
            "message": message,
            "payload": payload
        }

        url = self.base_url + 'post_system_event_message'
        requests = post(url, data=data, headers=headers)
        result = requests.json()
        if 200 <= requests.status_code < 400:
            comment = Response()
            comment.comment_before_id = json.dumps(result['results']['comment']['comment_before_id'])
            comment.disable_link_preview = json.dumps(result['results']['comment']['disable_link_preview'])
            comment.email = json.dumps(result['results']['comment']['email'])
            comment.comment_id = json.dumps(result['results']['comment']['id'])
            comment.message = json.dumps(result['results']['comment']['message'])
            comment.payload = json.dumps(result['results']['comment']['payload'])
            comment.room_id = json.dumps(result['results']['comment']['room_id'])
            comment.comment_status = json.dumps(result['results']['comment']['status'])
            comment.timestamp = json.dumps(result['results']['comment']['timestamp'])
            comment.topic_id = json.dumps(result['results']['comment']['topic_id'])
            comment.type = json.dumps(result['results']['comment']['type'])
            comment.unique_temp_id = json.dumps(result['results']['comment']['unique_temp_id'])
            comment.unix_nano_timestamp = json.dumps(result['results']['comment']['unix_nano_timestamp'])
            comment.unix_timestamp = json.dumps(result['results']['comment']['unix_timestamp'])
            comment.user_avatar_url = json.dumps(result['results']['comment']['user_avatar_url'])
            comment.user_id = json.dumps(result['results']['comment']['user_id'])
            comment.username = json.dumps(result['results']['comment']['username'])
            comment.as_json = json.dumps(requests.json())
            return comment
        else:
            comment = Response()
            comment.error_message = json.dumps(result['error']['message'])
            comment.status_code = json.dumps(requests.status_code)
            comment.as_json = json.dumps(requests.json())
            return comment
