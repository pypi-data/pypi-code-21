#!/usr/bin env python3
"""
Python module for rooms API.
This module used for Python wrapper for Qiscus SDK RESTful API
"""

import json
from requests import post, get


class Response():
    pass


class Rooms:
    def __init__(self):
        self.secret_key = None
        self.base_url = None
        self.app_id = None

    def create_room(self, name, creator, participants, avatar_url=None):
        """
        This method used to create a new room.

        :param name: name of room
        :type name: str
        :param creator: room creator
        :type creator: str
        :param participants: array of string email
        :type participants: str
        :param avatar_url: room avatar url. This is optional parameter
        :type avatar_url: str
        :return: it will return object named room
        """
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key,
            "QISCUS_SDK_APP_ID": self.app_id
        }

        data = {
            "name": name,
            "creator": creator,
            "participants[]": participants,
            "avatar_url": avatar_url
        }

        url = self.base_url + 'create_room'
        requests = post(url, data=data, headers=headers)
        result = requests.json()
        if 200 <= requests.status_code < 400:
            room = Response()
            room.room_creator = result['results']['creator']
            room.room_participants = result['results']['participants']
            room_participants = []
            for i in result['results']['participants']:
                room = Response()
                room.participants_avatar_url = i['avatar_url']
                room.participants_email = i['email']
                room.participants_id = i['id']
                room.participants_last_comment_read_id = i['last_comment_read_id']
                room.participants_last_comment_received_id = i['last_comment_received_id']
                room.participants_username = i['username']
                room.participants_as_json = result['results']['participants']
                room_participants.append(room)
            room.participants = room_participants
            room.room_id = result['results']['room_id']
            room.room_name = result['results']['room_name']
            room.room_type = result['results']['room_type']
            room.room_info_as_json = json.dumps(requests.json())
            return room
        else:
            room = Response()
            room.error_message = result['error']['message']
            room.error_status_code = requests.status_code
            room.error_info_as_json = json.dumps(requests.json())
            return room

    def update_room(self, user_email, room_id, room_name=None, room_avatar_url=None,
                    options=None):
        """
        This method used to update room detail, like room name or room avatar url.

        :param user_email:
        :type user_email: str
        :param room_id:
        :type room_id: str
        :param room_name:
        :type room_name: str
        :param room_avatar_url:
        :type room_avatar_url: str
        :param options:
        :type options: str
        :return: it will return object named room
        """
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key,
            "QISCUS_SDK_APP_ID": self.app_id
        }

        data = {
            "user_email": user_email,
            "room_id": room_id,
            "room_name": room_name,
            "room_avatar_url": room_avatar_url,
            "options": options
        }

        url = self.base_url + 'update_room'
        requests = post(url, data=data, headers=headers)
        result = requests.json()
        if 200 <= requests.status_code < 400:
            room = Response()
            room.changed = result['results']['changed']
            room.room_chat_type = result['results']['room']['chat_type']
            room.room_id = result['results']['room']['id']
            room.room_last_comment_id = result['results']['room']['last_comment_id']
            room.room_last_comment_message = result['results']['room']['last_comment_message']
            room.room_last_topic_id = result['results']['room']['last_topic_id']
            room.room_avatar_url = result['results']['room']['avatar_url']
            room_participants = []
            for i in result['results']['room']['participants']:
                room = Response()
                room.participants_avatar_url = i['avatar_url']
                room.participants_email = i['email']
                room.participants_username = i['username']
                room.participants_last_comment_read_id = i['last_comment_read_id']
                room.participants_last_comment_received_id = i['last_comment_received_id']
                room.participants_as_json = result['results']['room']['participants']
                room_participants.append(room)
            room.room_participants = room_participants
            room.room_name = result['results']['room']['room_name']
            room_comments = []
            for i in result['results']['comments']:
                comment = Response()
                comment.comment_id = i['id']
                comment.comment_before_id = i['comment_before_id']
                comment.comment_message = i['message']
                comment.comment_comment_type = i['type']
                comment.comment_comment_payload = json.dumps(i['payload'])
                comment.comment_disable_link_preview = i['disable_link_preview']
                comment.comment_email = i['email']
                comment.comment_username = i['username']
                comment.comment_user_avatar_url = i['user_avatar_url']
                comment.comment_timestamp = i['timestamp']
                comment.comment_unix_timestamp = i['unix_timestamp']
                comment.comment_unique_temp_id = i['unique_temp_id']
                comment.comment_as_json = json.dumps(result['results']['comments'])
                room_comments.append(comment)
            room.room_comments = room_comments
            room.room_info_as_json = json.dumps(requests.json())
            return room
        else:
            room = Response()
            room.error_message = result['error']['message']
            room.error_info_as_json = json.dumps(requests.json())
            room.error_status_code = requests.status_code
            return room

    def get_or_create_room_with_target(self, email1, email2):
        """
        This method used to get room with target of two user.
        If room does not exist yet, it will create new room.

        :param email1:
        :type email1: str
        :param email2:
        :type email2: str
        :return: it will return object named room
        """
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key,
            "QISCUS_SDK_APP_ID": self.app_id
        }

        url = self.base_url + 'get_or_create_room_with_target?emails[]=' + \
            email1 + '&emails[]=' + email2
        requests = get(url, headers=headers)
        result = requests.json()
        if 200 <= requests.status_code < 400:
            room = Response()
            room_comments = []
            for i in result['results']['comments']:
                comment = Response()
                comment.comments_before_id = i['comment_before_id']
                comment.comments_disable_link_preview = i['disable_link_preview']
                comment.comments_email = i['email']
                comment.comments_id = i['id']
                comment.comments_message = i['message']
                comment.comments_timestamp = i['timestamp']
                comment.comments_unique_temp_id = i['unique_temp_id']
                comment.comments_user_avatar_url = i['user_avatar_url']
                comment.comments_username = i['username']
                comment.comments_as_json = json.dumps(result['results']['comments'])
                room_comments.append(comment)
            room.room_comments = room_comments
            room.room_avatar_url = result['results']['room']['avatar_url']
            room.room_chat_type = result['results']['room']['chat_type']
            room.room_id = result['results']['room']['id']
            room.room_last_comment_id = result['results']['room']['last_comment_id']
            room.room_last_comment_message = result['results']['room']['last_comment_message']
            room.room_last_topic_id = result['results']['room']['last_topic_id']
            room.room_options = result['results']['room']['options']
            room_participants = []
            for i in result['results']['room']['participants']:
                room = Response()
                room.participants_avatar_url = i['avatar_url']
                room.participants_email = i['email']
                room.participants_username = i['username']
                room.participants_info_as_json = json.dumps(result['results']['room']['participants'])
                room_participants.append(room)
            room.room_participants = room_participants
            room.room_name = result['results']['room']['room_name']
            room.room_info_as_json = json.dumps(requests.json())
            return room
        else:
            room = Response()
            room.error_message = result['error']['message']
            room.error_info_as_json = json.dumps(requests.json())
            room.error_status_code = requests.status_code
            return room

    def get_rooms_info(self, user_email, room_id, show_participants=''):
        """
        This method used to get rooms info of specific user.

        :param user_email: user email
        :type user_email: str
        :param room_id: room id, array of string
        :type room_id: str
        :param show_participants: boolean true or false, default is false
        :type show_participants: bool
        :return: it will return object named room
        """
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key,
            "QISCUS_SDK_APP_ID": self.app_id
        }

        data = {
            "user_email": user_email,
            "room_id[]": room_id,
            "show_participants": show_participants
        }

        url = self.base_url + 'get_rooms_info'
        requests = post(url, data=data, headers=headers)
        result = requests.json()
        if 200 <= requests.status_code < 400:
            rooms = Response()
            rooms_info = []
            for i in result['results']['rooms_info']:
                rooms = Response()
                rooms.rooms_last_comment_id = i['last_comment_id']
                rooms.rooms_last_comment_message = i['last_comment_message']
                rooms.rooms_last_comment_timestamp = i['last_comment_timestamp']
                rooms.rooms_id = i['room_id']
                rooms.rooms_name = i['room_name']
                rooms.rooms_type = i['room_type']
                rooms.rooms_unread_count = i['unread_count']
                rooms.rooms_info_as_json = json.dumps(result['results']['rooms_info'])
                rooms_info.append(rooms)
            rooms.rooms_info = rooms_info
            rooms.rooms_info_as_json = json.dumps(requests.json())
            return rooms
        else:
            room = Response()
            room.error_message = result['error']['message']
            room.error_info_as_json = json.dumps(requests.json())
            room.error_status_code = requests.status_code
            return room

    def add_room_participants(self, room_id, emails):
        """
        This method used to add participants to specific room.

        :param room_id: room id
        :type room_id: str
        :param emails: emails, array of string
        :type emails: str
        :return: it will return object name room
        """
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key,
            "QISCUS_SDK_APP_ID": self.app_id
        }

        data = {
            "room_id": room_id,
            "emails[]": emails
        }

        url = self.base_url + 'add_room_participants'
        requests = post(url, data=data, headers=headers)
        result = requests.json()
        if 200 <= requests.status_code < 400:
            room = Response()
            room.room_creator = result['results']['creator']
            room.room_participants = result['results']['participants']
            room.room_id = result['results']['room_id']
            room.room_name = result['results']['room_name']
            room.room_type = result['results']['room_type']
            room.room_info_as_json = json.dumps(requests.json())
            return room
        else:
            room = Response()
            room.error_message = result['error']['message']
            room.error_info_as_json = json.dumps(requests.json())
            room.error_status_code = requests.status_code
            return room

    def remove_room_participants(self, room_id, emails):
        """
        This method used to remove participants from specific room.

        :param room_id: room id
        :type room_id: str
        :param emails: emails, array of string
        :type emails: str
        :return: it will return object named room
        """
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key,
            "QISCUS_SDK_APP_ID": self.app_id
        }

        data = {
            "room_id": room_id,
            "emails[]": emails
        }

        url = self.base_url + 'remove_room_participants'
        requests = post(url, data=data, headers=headers)
        result = requests.json()
        if 200 <= requests.status_code < 400:
            room = Response()
            room.room_creator = result['results']['creator']
            room.room_participants = result['results']['participants']
            room.room_id = result['results']['room_id']
            room.room_name = result['results']['room_name']
            room.room_type = result['results']['room_type']
            room.room_info_as_json = json.dumps(requests.json())
            return room
        else:
            room = Response()
            room.error_message = result['error']['message']
            room.error_info_as_json = json.dumps(requests.json())
            room.error_status_code = requests.status_code
            return room
