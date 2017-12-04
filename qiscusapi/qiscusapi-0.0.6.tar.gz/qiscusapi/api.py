#!/usr/bin env python3
"""
Python wrapper for Qiscus SDK RESTful API
"""
from qiscusapi.users import Users
from qiscusapi.rooms import Rooms
from qiscusapi.comments import Comments


class Api(object):
    def __init__(self, app_id=None, secret_key=None):
        """This class used for initialize Qiscus API with app id and secret key.
        """
        self.app_id = app_id
        self.secret_key = secret_key
        self.base_url = 'https://{}.qiscus.com/api/v2/rest/'.format(app_id)

    def login_or_register(self, email, username, password, avatar_url=None,
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
        user = Users.login_or_register(self, email, username, password, avatar_url,
                                       device_token, device_platform)

        return user

    def check_user_profile(self, user_email):
        """
        This method used to check user profile.

        :param user_email: user email
        :type user_email: str
        :return: it will return to object named user.
        """
        user = Users.check_user_profile(self, user_email)
        return user

    def reset_user_token(self, user_email):
        """
        This method used to reset user authentication token.
        In case your user token is compromised, you can reset their token at any time.
        This make previous token no longer valid.

        :param user_email: user email
        :type user_email: str
        :return: it will return to object named user.
        """
        user = Users.reset_user_token(self, user_email)
        return user

    def get_user_room_lists(self, user_email, page='1', show_participants='false'):
        """
        This method used to show user room lists. It will show maximum 20 data per page.
        If page parameter empty, this API will return all conversations (max 100)

        :param user_email: user email
        :type user_email: str
        :param page: number of page
        :type page: str
        :param show_participants: "true" or "false" default will be false
        :type show_participants: bool
        :return: it will return to object named user.
        """
        user = Users.get_user_room_lists(self, user_email, page, show_participants)
        return user

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
        user = Rooms.create_room(self, name, creator, participants, avatar_url)
        return user



    def update_room(self, user_email, room_id, room_name=None, room_avatar_url=None, options=None):
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
        room = Rooms.update_room(self, user_email, room_id, room_name, room_avatar_url, options)
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
        room = Rooms.get_or_create_room_with_target(self, email1, email2)
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
        room = Rooms.get_rooms_info(self, user_email, room_id, show_participants)
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
        room = Rooms.add_room_participants(self, room_id, emails)
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
        room = Rooms.remove_room_participants(self, room_id, emails)
        return room

    def post_comment_text(self, sender_email, room_id, message, payload=None,
                          unique_temp_id=None, disable_link_preview=None):
        """
        This method used to post comment text type.

        :param sender_email: sender email
        :type sender_email: str
        :param room_id:it can be room_id or channel id specified by client or
        auto generated by server
        :type room_id: str
        :param message: message
        :type message: str
        :param payload: payload, optional parameter. default=null
        :type payload: str
        :param unique_temp_id: optional parameter. default=generated by backend.
        :type unique_temp_id: str
        :param disable_link_preview: optional parameter. default='false'
        :type disable_link_preview: bool
        :return: it will return object named room
        """
        comment = Comments.post_comment_text(self, sender_email, room_id, message,
                                             payload, unique_temp_id, disable_link_preview)
        return comment

    def post_comment_buttons(self, sender_email, room_id, payload):

        """
        This method used to post comment buttons type.

        :param sender_email: sender email
        :type sender_email: str
        :param room_id:it can be room_id or channel id specified by client or
        auto generated by server
        :type room_id: str
        :param message: message
        :type message: str
        :param payload:
        :type payload: str
            Payload example:
                {
                    "text": "Silahkan pilih menu berikut:",
                    "buttons": [
                        {
                            "label": "KiNews",
                            "type": "postback",
                            "payload": {
                                "url": "http://telkomnews.bots.qiscus.com/v1/postback",
                                "method": "post",
                                "payload": {
                                    "intent": "POPULER_NEWS"
                                }
                            }
                        },
                        {
                            "label": "Google.co.id",
                            "type": "link",
                            "payload": {
                                "url": "http://google.co.id"
                            }
                        }
                    ]
                }
        :return: it will return object named room
        """
        comment = Comments.post_comment_buttons(self, sender_email, room_id, payload)
        return comment

    def post_comment_card(self, sender_email, room_id, payload):
        """
        This method used to post comment card type.

        :param sender_email:
        :type sender_email: str
        :param room_id:
        :type room_id: str
        :param payload:
            payload example:
                {
                    "text": "Special deal buat sista nih..",
                    "image": "http://url.com/gambar.jpg",
                    "title": "Atasan Blouse Tunik Wanita Baju Muslim Worie Longtop",
                    "description": "Oleh sippnshop\n96% (666 feedback)\nRp 49.000.00,-\nBUY 2 GET 1 FREE!!!",
                    "url": "http://url.com/baju?id=123&track_from_chat_room=123",
                    "buttons": [
                        {
                            "label": "button1",
                            "type": "postback",
                            "payload": {
                                "url": "http://somewhere.com/button1",
                                "method": "get",
                                "payload": null
                            }
                        },
                        {
                            "label": "button2",
                            "type": "link",
                            "payload": {
                                "url": "http://somewhere.com/button2?id=123",
                                "method": "get",
                                "payload": null
                            }
                        }
                    ]
                }
        :type payload: str
        :return: it will return object named room
        """
        comment = Comments.post_comment_card(self, sender_email, room_id, payload)
        return comment

    def post_comment_custom(self, sender_email, room_id, payload):
        """
        This method used to post comment custom type.

        :param sender_email:
        :type sender_email: str
        :param room_id:
        :type room_id: str
        :param payload: can be anything: object, array, string, number in JSON
            payload example 1:
                {
                    "type": "typecustom",
                    "content": {
                          "foo": "bar"
                }
            payload example 2:
                {
                    "type": "promo", // sub type of custom payload
                    "content": {
                        "date": "2017-09-09"
                    }
                }
        :type payload: str
        :return: it will return object named room
        """
        comment = Comments.post_comment_custom(self, sender_email, room_id, payload)
        return comment

    def post_comment_account_linking(self, sender_email, room_id, payload):
        """
        This method used to post comment account linking type.

        :param sender_email:
        :type sender_email: str
        :param room_id:
        :type room_id: str
        :param payload:
            payload example:
                {
                    "url": "http://google.com",
                    "redirect_url": "http://google.com/redirect",
                    "text": "silahkan login",
                    "params": {
                      "user_id": 1,
                      "topic_id": 1
                }
        :type payload: str
        :return: it will return object named room
        """
        comment = Comments.post_comment_account_linking(self, sender_email, room_id, payload)
        return comment

    def post_comment_postback_button(self, sender_email, room_id, payload):
        """

        :param sender_email:
        :param room_id:
        :param payload:
        :return:
        """
        comment = Comments.post_comment_postback_button(self, sender_email, room_id, payload)
        return comment

    def load_comments(self, room_id, page='1', limit='20'):
        """
        This method used to load comments in specific room

        :param room_id:
        :type room_id: int
        :param page: optional default=1
        :type page: int
        :param limit: optional default=20
        :type limit: int
        :return: it will return object named room
        """
        comment = Comments.load_comments(self, room_id, page, limit)
        return comment

    def search_messages(self, user_email, query, room_id=None):
        """
        This method used to search messages in specific room

        :param user_email:
        :type user_email: str
        :param query:keyword to search
        :type query: str
        :param room_id: optional, send this param if you want
        search message in specific room
        :type room_id: str
        :return: it will return object named room
        """
        comment = Comments.search_messages(self, user_email, query, room_id)
        return comment

    def post_system_event_message(self, system_event_type, room_id, subject_email,
                                  object_email=None, updated_room_name=None):
        """
        This method used to post all type of system event message

        :param system_event_type: valid value is: "create_room", "add_member",
        "join_room", "remove_member", "left_room", "change_room_name", "change_room_avatar"
        :type system_event_type: str
        :param room_id: room id to post
        :type room_id: str
        :param subject_email: person who create a room, add member to room,
        join room, remove member from room, left from room,
        change room name and/or room avatar
        :type subject_email: str
        :param object_email: array of string. optional, only required when
        system event type is add_member or remove_member
        :type object_email: str
        :param updated_room_name: only required when system event message
        type is change_room_name or create_room
        :type updated_room_name: str
        :return: it will return object named room
        """
        comment = Comments.post_system_event_message(self, system_event_type, room_id, subject_email,
                                                     object_email, updated_room_name)
        return comment
