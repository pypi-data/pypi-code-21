#!/usr/bin env python3
"""
Python wrapper for Qiscus SDK RESTful API
"""

from requests import post, get

class Response(object):
    pass

class Api(object):
    """API wrapper. 
    """

    def __init__(self, app_id=None, secret_key=None):
        """This class used for initialize Qiscus API with app id and secret key.
        """
        self.app_id = app_id
        self.secret_key = secret_key
        self.base_url = 'https://' + app_id + '.qiscus.com/api/v2/rest/'

    # USER
    def login_or_register(self, email, username, password=None, avatar_url=None,
                          device_token=None, device_platform=None):
        """Create new user, or if email is exist it will login.
           Previous password will be replaced to new password
           if email with that user is exist.

           :param email string required
           :param username string required
           :param password string required
           :param display_name string
           :param avatar_url string
           :param device_token string
           :param device_platform string
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
        if requests.status_code >= 200 and requests.status_code < 400:
            result = requests.json()
            user = Response()
            user.id = result['results']['user']['id']
            user.email = result['results']['user']['email']
            user.username = result['results']['user']['username']
            user.avatar_url = result['results']['user']['avatar_url']
            user.token = result['results']['user']['token']
            user.as_dict = result['results']['user']
            user.status = requests.status_code
            print('[!] Request Succeed, {0}: {1}'.format(requests.status_code, url))
            return user
        else:
            result = requests.json()
            user = Response()
            user.error_message = result['error']['message']
            user.status = requests.status_code
            print('[!] Request Failed, {0}: {1}'.format(
                requests.status_code, user.error_message))
            return user

    def get_user_profile(self, user_email):
        """Check user profile.

           user_email string required
        """
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key
        }

        url = self.base_url + 'user_profile?user_email=' + user_email
        requests = get(url, headers=headers)
        if requests.status_code >= 200 and requests.status_code < 400:
            result = requests.json()
            user = Response()
            user.id = result['results']['user']['id']
            user.email = result['results']['user']['email']
            user.username = result['results']['user']['username']
            user.avatar_url = result['results']['user']['avatar_url']
            user.token = result['results']['user']['token']
            user.as_dict = result['results']['user']
            user.status = requests.status_code
            print('[!] Request Succeed, {0}: {1}'.format(requests.status_code, url))
            return user
        else:
            result = requests.json()
            user = Response()
            user.error_message = result['error']['message']
            user.status = requests.status_code
            print('[!] Request Failed, {0}: {1}'.format(requests.status_code, user.error_message))
            return user

    def get_user_room_lists(self, user_email, page="1", show_participants="false",
                            room_type="single"):
        """
        get user room lists.

        :param user_email [string] required
        :param page [int, optional] number of page
        :param show_participants [bool, optional] "true" or "false" default will be false
        :param room_type [string, optional] filter by room type ("single" or "group") default will be return all type
        """
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key
        }

        url = self.base_url + 'get_user_rooms?user_email=' + user_email + \
            '&page=' + page + '&show_participants=' + show_participants
        requests = get(url, headers=headers)
        result = requests.json()
        if requests.status_code >= 200 and requests.status_code < 400:
            rooms = Response()
            rooms.current_page = result['results']['meta']['current_page']
            rooms.total_room = result['results']['meta']['total_room']
            rooms_info = []
            for i in result['results']['rooms_info']:
                room = Response()
                room.last_comment_id = i["last_comment_id"]
                room.last_comment_message = i["last_comment_message"]
                room.last_comment_timestamp = i["last_comment_timestamp"]
                room.room_avatar_url = i["room_avatar_url"]
                room.room_id = i["room_id"]
                room.room_name = i["room_name"]
                room.room_type = i["room_type"]
                room.unread_count = i["unread_count"]
                room.as_dict = i
                rooms_info.append(room)
            rooms.rooms_info = rooms_info
            rooms.as_dict = result['results']
            rooms.status = requests.status_code
            print('[!] Request Succeed, {0}: {1}'.format(requests.status_code, url))
            return rooms
        else:
            result = requests.json()
            rooms = Response()
            rooms.error_message = result['error']['message']
            rooms.status = requests.status_code
            print('[!] Request Failed, {0}: {1}'.format(
                requests.status_code, rooms.error_message))
            return rooms

    # ROOM
    def create_room(self, name, creator, participants, avatar_url=None):
        """
        create new room

        :param name [string]
        :param participants[] [array of string email]
        :param creator [string email]
        :param avatar_url [string] optional
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
        if requests.status_code >= 200 and requests.status_code < 400:
            room = Response()
            room.creator = result['results']['creator']
            room_participants = []
            for i in result['results']['participants']:
                rooms = Response()
                rooms.avatar_url = i['avatar_url']
                rooms.email = i['email']
                rooms.id = i['id']
                rooms.last_comment_read_id = i['last_comment_read_id']
                rooms.last_comment_received_id = i['last_comment_received_id']
                rooms.username = i['username']
                rooms.as_dict = i
                room_participants.append(rooms)
            room.participants = room_participants
            room.id = result['results']['room_id']
            room.name = result['results']['room_name']
            room.type = result['results']['room_type']
            room.as_dict = result['results']
            room.status = requests.status_code
            print('[!] Request Succeed, {0}: {1}'.format(requests.status_code, url))
            return room
        else:
            result = requests.json()
            room = Response()
            room.error_message = result['error']['message']
            room.status = requests.status_code
            print('[!] Request Failed, {0}: {1}'.format(
                requests.status_code, room.error_message))
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
        if requests.status_code >= 200 and requests.status_code < 400:
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
                rooms = Response()
                rooms.avatar_url = i['avatar_url']
                rooms.email = i['email']
                rooms.username = i['username']
                rooms.last_comment_read_id = i['last_comment_read_id']
                rooms.last_comment_received_id = i['last_comment_received_id']
                rooms.as_dict = i
                room_participants.append(rooms)
            room.participants = room_participants
            room.room_name = result['results']['room']['room_name']
            room_comments = []
            for i in result['results']['comments']:
                rooms = Response()
                rooms.id = i['id']
                rooms.comment_before_id = i['comment_before_id']
                rooms.message = i['message']
                rooms.type = i['type']
                rooms.payload = i['payload']
                rooms.disable_link_preview = i['disable_link_preview']
                rooms.email = i['email']
                rooms.username = i['username']
                rooms.user_avatar_url = i['user_avatar_url']
                rooms.timestamp = i['timestamp']
                rooms.unix_timestamp = i['unix_timestamp']
                rooms.unique_temp_id = i['unique_temp_id']
                rooms.as_dict = i
                room_comments.append(rooms)
            room.comments = room_comments
            room.status = requests.status_code
            room.as_dict = result['results']
            print('[!] Request Succeed, {0}: {1}'.format(requests.status_code, url))
            return room
        else:
            result = requests.json()
            room = Response()
            room.error_message = result['error']['message']
            room.status = requests.status_code
            print('[!] Request Failed, {0}: {1}'.format(
                requests.status_code, room.error_message))
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
        if requests.status_code >= 200 and requests.status_code < 400:
            room = Response()
            room_comments = []
            for i in result['results']['comments']:
                rooms = Response()
                rooms.comment_before_id = i['comment_before_id']
                rooms.disable_link_preview = i['disable_link_preview']
                rooms.email = i['email']
                rooms.id = i['id']
                rooms.message = i['message']
                rooms.timestamp = i['timestamp']
                rooms.unique_temp_id = i['unique_temp_id']
                rooms.user_avatar_url = i['user_avatar_url']
                rooms.username = i['username']
                rooms.as_dict = i
                room_comments.append(rooms)
            room.comments = room_comments
            room.avatar_url = result['results']['room']['avatar_url']
            room.chat_type = result['results']['room']['chat_type']
            room.id = result['results']['room']['id']
            room.last_comment_id = result['results']['room']['last_comment_id']
            room.last_comment_message = result['results']['room']['last_comment_message']
            room.last_topic_id = result['results']['room']['last_topic_id']
            room.options = result['results']['room']['options']
            room_participants = []
            for i in result['results']['room']['participants']:
                rooms = Response()
                rooms.avatar_url = i['avatar_url']
                rooms.email = i['email']
                rooms.username = i['username']
                rooms.as_dict = i
                room_participants.append(rooms)
            room.participants = room_participants
            room.room_name = result['results']['room']['room_name']
            room.as_dict = result['results']
            room.status = requests.status_code
            print('[!] Request Succeed, {0}: {1}'.format(requests.status_code, url))
            return room
        else:
            result = requests.json()
            room = Response()
            room.error_message = result['error']['message']
            room.status = requests.status_code
            print('[!] Request Failed, {0}: {1}'.format(
                requests.status_code, room.error_message))
            return room

    def get_rooms_info(self, user_email, room_id, show_participants="false"):
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
        if requests.status_code >= 200 and requests.status_code < 400:
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
                rooms.as_dict = i
                rooms_info.append(rooms)
            rooms.rooms_info = rooms_info
            rooms.as_dict = result['results']
            rooms.status = requests.status_code
            print('[!] Request Succeed, {0}: {1}'.format(requests.status_code, url))
            return rooms
        else:
            result = requests.json()
            room = Response()
            room.error_message = result['error']['message']
            room.status = requests.status_code
            print('[!] Request Failed, {0}: {1}'.format(
                requests.status_code, room.error_message))
            return room

    def add_room_participants(self, room_id, emails):
        """
        add room participants

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
        if requests.status_code >= 200 and requests.status_code < 400:
            room = Response()
            room.creator = result['results']['creator']
            room.participants = result['results']['participants']  # updated participants
            room.room_id = result['results']['room_id']
            room.room_name = result['results']['room_name']
            room.room_type = result['results']['room_type']
            room.as_dict = result['results']
            room.status = requests.status_code
            print('[!] Request Succeed, {0}: {1}'.format(requests.status_code, url))
            return room
        else:
            result = requests.json()
            room = Response()
            room.error_message = result['error']['message']
            room.status = requests.status_code
            print('[!] Request Failed, {0}: {1}'.format(
                requests.status_code, room.error_message))
            return room

    def remove_room_participants(self, room_id, emails):
        """
        remove room participants

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
        if requests.status_code >= 200 and requests.status_code < 400:
            room = Response()
            room.creator = result['results']['creator']
            room.participants = result['results']['participants']  # updated participants
            room.room_id = result['results']['room_id']
            room.room_name = result['results']['room_name']
            room.room_type = result['results']['room_type']
            room.as_dict = result['results']
            room.status = requests.status_code
            print('[!] Request Succeed, {0}: {1}'.format(requests.status_code, url))
            return room
        else:
            result = requests.json()
            room = Response()
            room.error_message = result['error']['message']
            room.status = requests.status_code
            print('[!] Request Failed, {0}: {1}'.format(
                requests.status_code, room.error_message))
            return room

    # COMMENT
    def post_comment(self, sender_email, room_id, message, type=None,
                     payload=None, unique_temp_id=None,
                     disable_link_preview=None):
        """
        post comments

        :param sender_email [string]
        :param room_id [string], it can be room_id or channel id specified by client or auto generated by server
        :param message [string]
        :param type [string, default=text]
        :param payload [string json, see payload definitions bellow]
        :param unique_temp_id [string, optional, default=generated by backend]
        :param disable_link_preview [bool, optional, default=false]
        """
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key
        }

        data = {
            "sender_email": sender_email,
            "room_id": room_id,
            "message": message,
            "type": type,
            "payload": payload,
            "unique_temp_id": unique_temp_id,
            "disable_link_preview": disable_link_preview
        }

        url = self.base_url + 'post_comment'
        requests = post(url, data=data, headers=headers)
        result = requests.json()
        if requests.status_code >= 200 and requests.status_code < 400:
            comment = Response()
            comment.comment_before_id = result['results']['comment']['comment_before_id']
            comment.disable_link_preview = result['results']['comment']['disable_link_preview ']
            comment.email = result['results']['comment']['email']
            comment.id = result['results']['comment']['id']
            comment.message = result['results']['comment']['message']
            comment.payload = result['results']['comment']['payload']
            comment.room_id = result['results']['comment']['room_id']
            comment.timestamp = result['results']['comment']['timestamp']
            comment.unix_timestamp = result['results']['comment']['unix_timestamp']
            comment.topic_id = result['results']['comment']['topic_id']
            comment.type = result['results']['comment']['type']
            comment.unique_temp_id = result['results']['comment']['unique_temp_id']
            comment.user_avatar_url = result['results']['comment']['user_avatar_url']
            comment.username = result['results']['comment']['username']
            comment.as_dict = result['results']['comment']
            comment.status = requests.status_code
            print('[!] Request Succeed, {0}: {1}'.format(requests.status_code, url))
            return comment
        else:
            result = requests.json()
            comment = Response()
            comment.error_message = result['error']['message']
            comment.status = requests.status_code
            print('[!] Request Failed, {0}: {1}'.format(
                requests.status_code, comment.error_message))
            return comment

    def load_comments(self, room_id, page, limit=None):
        """
        load comments

        :param room_id [string]
        :param page [int optional]
        :param limit [int optional default=20]
        """
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key
        }

        url = self.base_url + 'load_comments?room_id=' + room_id + \
            '&page=' + page + '&limit=' + limit
        requests = get(url, headers=headers)
        result = requests.json()
        if requests.status_code >= 200 and requests.status_code < 400:
            comment = Response()
            comments_detail = []
            for i in result['results']['comments']:
                comments = Response()
                comments.comment_before_id = i['comment_before_id']
                comments.disable_link_preview = i['disable_link_preview']
                comments.email = i['email']
                comments.id = i['id']
                comments.message = i['message']
                comments.room_id = i['room_id']
                comments.room_name = i['room_name']
                comments.timestamp = i['timestamp']
                comments.unique_temp_id = i['unique_temp_id']
                comments.user_avatar_url = i['user_avatar_url']
                comments.username = i['username']
                comments.as_dict = i
                comments_detail.append(comments)
            comment.comments = comments_detail
            comment.as_dict = result['results']
            comment.status = requests.status_code
            print('[!] Request Succeed, {0}: {1}'.format(requests.status_code, url))
            return comment
        else:
            result = requests.json()
            comment = Response()
            comment.error_message = result['error']['message']
            comment.status = requests.status_code
            print('[!] Request Failed, {0}: {1}'.format(
                requests.status_code, comment.error_message))
            return comment

    def search_messages(self, user_email, query, room_id=None):
        """
        search messages

        :param user_email [string] required, user email
        :param query [string] required, keyword to search
        :param room_id [string] optional, send this param if you want search message in specific room
        """
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key
        }
        data = {
            "user_email": user_email,
            "query": query,
            "room_id": room_id
        }

        url = self.base_url + 'search_messages'
        requests = post(url, data=data, headers=headers)
        result = requests.json()
        if requests.status_code >= 200 and requests.status_code < 400:
            message = Response()
            message_details = []
            for i in result['results']['comments']:
                messages = Response()
                messages.chat_type = i['chat_type']
                messages.comment_before_id = i['comment_before_id']
                messages.disable_link_preview = i['disable_link_preview']
                messages.email = i['email']
                messages.id = i['id']
                messages.message = i['message']
                messages.payload = i['payload']
                messages.room_id = i['room_id']
                messages.room_name = i['room_name']
                messages.timestamp = i['timestamp']
                messages.topic_id = i['topic_id']
                messages.type = i['type']
                messages.unique_temp_id = i['unique_temp_id']
                messages.unix_timestamp = i['unix_timestamp']
                messages.user_avatar_url = i['user_avatar_url']
                messages.user_id = i['user_avatar_url']
                messages.username = i['username']
                messages.as_dict = i
                message_details.append(messages)
            message.messages = message_details
            message.as_dict = result['results']
            message.status = requests.status_code
            print('[!] Request Succeed, {0}: {1}'.format(requests.status_code, url))
            return message
        else:
            result = requests.json()
            message = Response()
            message.error_message = result['error']['message']
            message.status = requests.status_code
            print('[!] Request Failed, {0}: {1}'.format(
                requests.status_code, message.error_message))
            return message
