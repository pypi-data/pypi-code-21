#!/usr/bin env python3
"""
Python wrapper for Qiscus SDK RESTful API
"""
from qiscusapi.users import Users
from qiscusapi.rooms import Rooms
from qiscusapi.comments import Comments
from qiscusapi.system import System


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

        :param email:
        :param username:
        :param password:
        :param avatar_url:
        :param device_token:
        :param device_platform:
        :return:
        """
        user = Users.login_or_register(self, email, username, password, avatar_url,
                                       device_token, device_platform)

        return user

    def get_user_profile(self, user_email):
        """

        :param user_email:
        :return:
        """
        user = Users.get_user_profile(self, user_email)
        return user

    def reset_user_token(self, user_email):
        """

        :param user_email:
        :return:
        """
        user = Users.reset_user_token(self, user_email)
        return user

    def get_user_room_lists(self, user_email, page='1', show_participants='false'):
        """

        :param user_email:
        :param page:
        :param show_participants:
        :param room_type:
        :return:
        """
        user = Users.get_user_room_lists(self, user_email, page, show_participants)
        return user

    def create_room(self, name, creator, participants, event_message=False, avatar_url=None):
        """

        :param name:
        :param creator:
        :param participants:
        :param avatar_url:
        :return:
        """
        user = Rooms.create_room(self, name, creator, participants, event_message, avatar_url)
        return user



    def update_room(self, user_email, room_id, room_name=None, room_avatar_url=None, options=None):
        """

        :param user_email:
        :param room_id:
        :param room_name:
        :param room_avatar_url:
        :param options:
        :return:
        """
        user = Users.update_room(self, user_email, room_id, room_name, room_avatar_url, options)
        return user

    def get_or_create_room_with_target(self, email1, email2):
        """

        :param email1:
        :param email2:
        :return:
        """
        room = Rooms.get_or_create_room_with_target(self, email1, email2)
        return room

    def get_rooms_info(self, user_email, room_id, show_participants=''):
        """

        :param user_email:
        :param room_id:
        :param show_participants:
        :return:
        """
        room = Rooms.get_rooms_info(self, user_email, room_id, show_participants)
        return room

    def add_room_participants(self, room_id, emails, event_message=False):
        """

        :param room_id:
        :param emails:
        :return:
        """
        room = Rooms.add_room_participants(self, room_id, emails, event_message)
        return room

    def remove_room_participants(self, room_id, emails, event_message=False):
        """

        :param room_id:
        :param emails:
        :return:
        """
        room = Rooms.remove_room_participants(self, room_id, emails, event_message)
        return room

    def post_comment_text(self, sender_email, room_id, message, _type='text',
                          payload=None, unique_temp_id=None, disable_link_preview=None):
        """

        :param sender_email:
        :param room_id:
        :param message:
        :param payload:
        :param unique_temp_id:
        :param disable_link_preview:
        :return:
        """
        comment = Comments.post_comment_text(self, sender_email, room_id, message,
                                             _type, payload, unique_temp_id, disable_link_preview)
        return comment

    def post_comment_buttons(self, sender_email, room_id, payload):

        """

        :param sender_email:
        :param room_id:
        :param payload:
        :param unique_temp_id:
        :param disable_link_preview:
        :return:
        """
        comment = Comments.post_comment_buttons(self, sender_email, room_id, payload)
        return comment

    def post_comment_card(self, sender_email, room_id, payload):
        """

        :param sender_email:
        :param room_id:
        :param payload:
        :return:
        """
        comment = Comments.post_comment_card(self, sender_email, room_id, payload)
        return comment

    def post_comment_custom(self, sender_email, room_id, payload):
        """

        :param sender_email:
        :param room_id:
        :param payload:
        :return:
        """
        comment = Comments.post_comment_custom(self, sender_email, room_id, payload)
        return comment

    def post_comment_account_linking(self, sender_email, room_id, payload):
        """

        :param sender_email:
        :param room_id:
        :param payload:
        :return:
        """
        comment = Comments.post_comment_account_linking(self, sender_email, room_id, payload)
        return comment

    def load_comments(self, room_id, page, limit='20'):
        """

        :param room_id:
        :param page:
        :param limit:
        :return:
        """
        comment = Comments.load_comments(self, room_id, page, limit)
        return comment

    def search_messages(self, user_email, query, room_id=None):
        """

        :param user_email:
        :param query:
        :param room_id:
        :return:
        """
        comment = Comments.search_messages(self, user_email, query, room_id)
        return comment

    def create_room_system_event_message(self, room_id, subject_email,
                                         updated_room_name):
        """

        :param room_id:
        :param subject_email:
        :param updated_room_name:
        :param _system_event_type:
        :return:
        """
        system = System.create_room_system_event_message(self, room_id, subject_email,
                                         updated_room_name)
        return system

    def change_room_name_system_event_message(self, room_id, subject_email, updated_room_name):
        """

        :param room_id:
        :param subject_email:
        :param updated_room_name:
        :param _system_event_type:
        :return:
        """
        system = System.change_room_name_system_event_message(self, room_id, subject_email,
                                                              updated_room_name)
        return system

    def change_room_avatar_system_event_message(self, room_id, subject_email):
        """

        :param room_id:
        :param subject_email:
        :param _system_event_type:
        :return:
        """
        system = System.change_room_avatar_system_event_message(self, room_id, subject_email)
        return system

    def add_member_system_event_message(self, room_id, subject_email,
                                        object_email):
        """

        :param room_id:
        :param subject_email:
        :param object_email:
        :param _system_event_type:
        :return:
        """
        system = System.add_member_system_event_message(self, room_id, subject_email,
                                                        object_email)
        return system

    def remove_member_system_event_message(self, room_id, subject_email, object_email):
        """

        :param room_id:
        :param subject_email:
        :param object_email:
        :param _system_event_type:
        :return:
        """
        system = System.remove_member_system_event_message(self, room_id, subject_email,
                                                           object_email)
        return system

    def join_room_system_event_message(self, room_id, subject_email,
                                       _system_event_type='join_room'):
        """

        :param room_id:
        :param subject_email:
        :param _system_event_type:
        :return:
        """
        system = System.join_room_system_event_message(self, room_id, subject_email,
                                       _system_event_type)
        return system

    def left_room_system_event_message(self, room_id, subject_email):
        """

        :param room_id:
        :param subject_email:
        :param _system_event_type:
        :return:
        """
        system = System.left_room_system_event_message(self, room_id, subject_email)
        return system

    def custom_system_event_message(self, room_id, subject_email, message=None,
                                    payload=None):
        """

        :param room_id:
        :param subject_email:
        :param message:
        :param payload:
        :param _system_event_type:
        :return:
        """
        system = System.custom_system_event_message(self, room_id, subject_email, message,
                                    payload)
        return system
