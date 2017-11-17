#!/usr/bin env python3
"""
Python wrapper for Qiscus SDK RESTful API
"""

import json
from requests import post, get
from qiscusapi.system import System


class Response():
    pass


class Rooms:
    def __init__(self):
        self.secret_key = None
        self.base_url = None

    def create_room(self, name, creator, participants, event_message=False, avatar_url=None):
        """

        :param name:
        :param creator:
        :param participants:
        :param avatar_url:
        :return:
        """
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key
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
            room.info_as_json = json.dumps(requests.json())
            if event_message is True:
                room.event_message = System.create_room_system_event_message(
                    self,
                    room_id=room.room_id,
                    subject_email=creator,
                    updated_room_name=name
                )
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
        Update room.

        :param user_email [string required] must one of user participant
        :param room_id [string required] must be group room
        :param room_name [string optional]
        :param room_avatar_url [string optional]
        :param options [string optional]
        """
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key
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
            room.chat_type = result['results']['room']['chat_type']
            room.id = result['results']['room']['id']
            room.last_comment_id = result['results']['room']['last_comment_id']
            room.last_comment_message = result['results']['room']['last_comment_message']
            room.last_topic_id = result['results']['room']['last_topic_id']
            room.avatar_url = result['results']['room']['avatar_url']
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
            room.participants = room_participants
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
            room.comments = room_comments
            room.error_info_as_json = json.dumps(requests.json())
            return room
        else:
            room = Response()
            room.error_message = result['error']['message']
            room.error_info_as_json = json.dumps(requests.json())
            room.error_status_code = requests.status_code
            return room

    def get_or_create_room_with_target(self, email1, email2):
        """
        get or create room with target

        :param email1 [string required]
        :param email2 [string required]
        """
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key
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
                comment.comment_before_id = i['comment_before_id']
                comment.comment_disable_link_preview = i['disable_link_preview']
                comment.comment_email = i['email']
                comment.comment_id = i['id']
                comment.comment_message = i['message']
                comment.comment_timestamp = i['timestamp']
                comment.comment_unique_temp_id = i['unique_temp_id']
                comment.comment_user_avatar_url = i['user_avatar_url']
                comment.comment_username = i['username']
                comment.comment_as_json = json.dumps(result['results']['comments'])
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
            room.participants = room_participants
            room.room_name = result['results']['room']['room_name']
            room.info_as_json = json.dumps(requests.json())
            return room
        else:
            room = Response()
            room.error_message = result['error']['message']
            room.error_info_as_json = json.dumps(requests.json())
            room.error_status_code = requests.status_code
            return room

    def get_rooms_info(self, user_email, room_id, show_participants=''):
        """
        get rooms info

        :param room_id[] [array of string]
        :param user_email [string email]
        :param show_participants [boolean true or false, default is false]
        """
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key
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
                rooms.last_comment_id = i['last_comment_id']
                rooms.last_comment_message = i['last_comment_message']
                rooms.last_comment_timestamp = i['last_comment_timestamp']
                rooms.room_id = i['room_id']
                rooms.room_name = i['room_name']
                rooms.room_type = i['room_type']
                rooms.unread_count = i['unread_count']
                rooms.as_json = json.dumps(result['results']['rooms_info'])
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

    def add_room_participants(self, room_id, emails, event_message=False):
        """
        add room participants

        :param event_message:
        :param room_id [string]
        :param emails [array of string emails]
        """
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key
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
            if event_message is True:
                room.event_message = System.add_member_system_event_message(
                    self,
                    room_id=room_id,
                    subject_email=room.creator,
                    object_email=emails
                )
            return room
        else:
            room = Response()
            room.error_message = result['error']['message']
            room.error_info_as_json = json.dumps(requests.json())
            room.status_code = requests.status_code
            return room

    def remove_room_participants(self, room_id, emails, event_message=False):
        """
        remove room participants

        :param event_message:
        :param room_id [string]
        :param emails [array of string emails]
        """
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key
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
            if event_message is True:
                room.event_message = System.add_member_system_event_message(
                    self,
                    room_id=room_id,
                    subject_email=room.creator,
                    object_email=emails
                )
            return room
        else:
            room = Response()
            room.error_message = result['error']['message']
            room.error_info_as_json = json.dumps(requests.json())
            room.error_status_code = requests.status_code
            return room
