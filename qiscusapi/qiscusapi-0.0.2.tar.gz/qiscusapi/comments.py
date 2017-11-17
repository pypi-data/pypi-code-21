#!/usr/bin env python3
"""
Python wrapper for Qiscus SDK RESTful API
"""

import json
from requests import post, get


class Response():
    pass


class Comments:
    def __init__(self):
        self.secret_key = None
        self.base_url = None

    def post_comment_text(self, sender_email, room_id, message, _type='text',
                          payload=None, unique_temp_id=None,
                          disable_link_preview=None):
        """

        :param sender_email:
        :param room_id:
        :param message:
        :param payload:
        :param unique_temp_id:
        :param disable_link_preview:
        :return:
        """
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key
        }

        data = {
            "sender_email": sender_email,
            "room_id": room_id,
            "message": message,
            "type": _type,
            "payload": payload,
            "unique_temp_id": unique_temp_id,
            "disable_link_preview": disable_link_preview
        }

        url = self.base_url + 'post_comment'
        requests = post(url, data=data, headers=headers)
        result = requests.json()
        if 200 <= requests.status_code < 400:
            comment = Response()
            comment.comment_before_id = result['results']['comment']['comment_before_id']
            comment.comment_disable_link_preview = result['results']['comment']['disable_link_preview']
            comment.comment_user_email = result['results']['comment']['email']
            comment.comment_id = result['results']['comment']['id']
            comment.comment_message = result['results']['comment']['message']
            comment.comment_payload = result['results']['comment']['payload']
            comment.comment_room_id = result['results']['comment']['room_id']
            comment.comment_timestamp = result['results']['comment']['timestamp']
            comment.comment_unix_timestamp = result['results']['comment']['unix_timestamp']
            comment.comment_topic_id = result['results']['comment']['topic_id']
            comment.comment_type = result['results']['comment']['type']
            comment.comment_unique_temp_id = result['results']['comment']['unique_temp_id']
            comment.comment_user_avatar_url = result['results']['comment']['user_avatar_url']
            comment.comment_username = result['results']['comment']['username']
            comment.comment_info_as_json = json.dumps(requests.json())
            return comment
        else:
            comment = Response()
            comment.error_message = result['error']['message']
            comment.error_info_as_json = json.dumps(requests.json())
            comment.error_status_code = requests.status_code
            return comment

    def post_comment_buttons(self, sender_email, room_id, payload, _type='buttons'):
        """

        :param sender_email:
        :param room_id:
        :param payload:
        :param unique_temp_id:
        :param disable_link_preview:
        :return:
        """
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key
        }

        data = {
            "sender_email": sender_email,
            "room_id": room_id,
            "type": _type,
            "payload": payload
        }

        url = self.base_url + 'post_comment'
        requests = post(url, data=data, headers=headers)
        result = requests.json()
        if 200 <= requests.status_code < 400:
            comment = Response()
            comment_payload_buttons = []
            for i in result['results']['comment']['payload']['buttons']:
                comment = Response()
                comment.buttons_label = i['label']
                comment.buttons_type = i['type']
                comment.buttons_payload = i['payload']
                comment.buttons_info_as_json = json.dumps(result['results']['comment']['payload']['buttons'])
                comment_payload_buttons.append(comment)
            comment.comment_payload_buttons = comment_payload_buttons
            comment.comment_room_id = result['results']['comment']['room_id']
            comment.comment_timestamp = result['results']['comment']['timestamp']
            comment.comment_topic_id = result['results']['comment']['topic_id']
            comment.comment_type = result['results']['comment']['type']
            comment.comment_unique_temp_id = result['results']['comment']['unique_temp_id']
            comment.comment_unix_nano_timestamp = result['results']['comment']['unix_nano_timestamp']
            comment.comment_unix_timestamp = result['results']['comment']['unix_timestamp']
            comment.comment_user_avatar_url = result['results']['comment']['user_avatar_url']
            comment.comment_user_id = result['results']['comment']['user_id']
            comment.comment_username = result['results']['comment']['username']
            comment.comment_before_id = result['results']['comment']['comment_before_id']
            comment.comment_disable_link_preview = result['results']['comment']['disable_link_preview']
            comment.comment_email = result['results']['comment']['email']
            comment.comment_id = result['results']['comment']['id']
            comment.comment_message = result['results']['comment']['message']
            comment.comment_payload_text = result['results']['comment']['payload']['text']
            comment.comment_info_as_json = json.dumps(requests.json())
            return comment
        else:
            comment = Response()
            comment.error_message = result['error']['message']
            comment.error_as_json = json.dumps(requests.json())
            comment.error_status_code = requests.status_code
            return comment

    def post_comment_card(self, sender_email, room_id, payload, _type='card'):
        """

        :param sender_email:
        :param room_id:
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
        :return:
        """
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key
        }

        data = {
            "sender_email": sender_email,
            "room_id": room_id,
            "type": _type,
            "payload": payload.replace("\n", " ")
        }

        url = self.base_url + 'post_comment'
        requests = post(url, data=data, headers=headers)
        result = requests.json()
        if 200 <= requests.status_code < 400:
            comment = Response()
            comment.comment_before_id = result['results']['comment']['comment_before_id']
            comment.comment_disable_link_preview = result['results']['comment']['disable_link_preview']
            comment.comment_user_email = result['results']['comment']['email']
            comment.comment_id = result['results']['comment']['id']
            comment.comment_message = result['results']['comment']['message']
            comment.comment_payload = result['results']['comment']['payload']
            comment.comment_payload_description = result['results']['comment']['payload']['description']
            comment.comment_payload_image = result['results']['comment']['payload']['image']
            comment.comment_payload_text = result['results']['comment']['payload']['text']
            comment.comment_payload_title = result['results']['comment']['payload']['title']
            comment.comment_payload_url = result['results']['comment']['payload']['url']
            comment.comment_room_id = result['results']['comment']['room_id']
            comment.comment_status = result['results']['comment']['status']
            comment.comment_timestamp = result['results']['comment']['timestamp']
            comment.comment_topic_id = result['results']['comment']['topic_id']
            comment.comment_user_avatar_url = result['results']['comment']['user_avatar_url']
            comment.comment_user_id = result['results']['comment']['user_id']
            comment.comment_username = result['results']['comment']['username']
            comment.comment_info_as_json = json.dumps(requests.json())
            return comment
        else:
            comment = Response()
            comment.error_message = result['error']['message']
            comment.error_as_json = json.dumps(requests.json())
            comment.error_status_code = requests.status_code
            return comment

    def post_comment_custom(self, sender_email, room_id, payload, _type='custom'):
        """

        :param sender_email:
        :param room_id:
        :param payload:
        :param _type:
        :return:
        """
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key
        }

        data = {
            "sender_email": sender_email,
            "room_id": room_id,
            "type": _type,
            "payload": payload.replace("\n", " ")
        }

        url = self.base_url + 'post_comment'
        requests = post(url, data=data, headers=headers)
        result = requests.json()
        if 200 <= requests.status_code < 400:
            comment = Response()
            comment.comment_before_id = result['results']['comment']['comment_before_id']
            comment.comment_disable_link_preview = result['results']['comment']['disable_link_preview']
            comment.comment_user_email = result['results']['comment']['email']
            comment.comment_id = result['results']['comment']['id']
            comment.comment_message = result['results']['comment']['message']
            comment.comment_payload = result['results']['comment']['payload']
            comment.comment_room_id = result['results']['comment']['room_id']
            comment.comment_status = result['results']['comment']['status']
            comment.comment_timestamp = result['results']['comment']['timestamp']
            comment.comment_topic_id = result['results']['comment']['topic_id']
            comment.comment_user_avatar_url = result['results']['comment']['user_avatar_url']
            comment.comment_user_id = result['results']['comment']['user_id']
            comment.comment_username = result['results']['comment']['username']
            comment.comment_info_as_json = json.dumps(requests.json())
            return comment
        else:
            comment = Response()
            comment.error_message = result['error']['message']
            comment.error_as_json = json.dumps(requests.json())
            comment.error_status_code = requests.status_code
            return comment

    def post_comment_account_linking(self, sender_email, room_id, payload, _type='account_linking'):
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key
        }

        data = {
            "sender_email": sender_email,
            "room_id": room_id,
            "type": _type,
            "payload": payload.replace("\n", " ")
        }

        url = self.base_url + 'post_comment'
        requests = post(url, data=data, headers=headers)
        result = requests.json()
        if 200 <= requests.status_code < 400:
            comment = Response()
            comment.comment_before_id = result['results']['comment']['comment_before_id']
            comment.comment_disable_link_preview = result['results']['comment']['disable_link_preview']
            comment.comment_user_email = result['results']['comment']['email']
            comment.comment_id = result['results']['comment']['id']
            comment.comment_message = result['results']['comment']['message']
            comment.comment_payload = result['results']['comment']['payload']
            comment.comment_room_id = result['results']['comment']['room_id']
            comment.comment_status = result['results']['comment']['status']
            comment.comment_timestamp = result['results']['comment']['timestamp']
            comment.comment_topic_id = result['results']['comment']['topic_id']
            comment.comment_user_avatar_url = result['results']['comment']['user_avatar_url']
            comment.comment_user_id = result['results']['comment']['user_id']
            comment.comment_username = result['results']['comment']['username']
            comment.comment_info_as_json = json.dumps(requests.json())
            return comment
        else:
            comment = Response()
            comment.error_message = result['error']['message']
            comment.error_as_json = json.dumps(requests.json())
            comment.error_status_code = requests.status_code
            return comment

    def load_comments(self, room_id, page, limit='20'):
        """
        load comments

        :param room_id [string]
        :param page [int optional]
        :param limit [int optional default=20]
        """
        headers = {
            "QISCUS_SDK_SECRET": self.secret_key
        }

        url = self.base_url + 'load_comments?room_id=' + \
            room_id + '&page=' + page + '&limit=' + limit
        requests = get(url, headers=headers)
        result = requests.json()
        if 200 <= requests.status_code < 400:
            comment = Response()
            comments_detail = []
            for i in result['results']['comments']:
                comments = Response()
                comments.comment_before_id = i['comment_before_id']
                comments.comment_disable_link_preview = i['disable_link_preview']
                comments.comment_user_email = i['email']
                comments.comment_id = i['id']
                comments.comment_message = i['message']
                comments.comment_room_id = i['room_id']
                comments.comment_room_name = i['room_name']
                comments.comment_timestamp = i['timestamp']
                comments.comment_unique_temp_id = i['unique_temp_id']
                comments.comment_user_avatar_url = i['user_avatar_url']
                comments.comment_username = i['username']
                comments.comment_info_as_json = json.dumps(result['results']['comments'])
                comments_detail.append(comments)
            comment.comments = comments_detail
            comment.comment_as_json = json.dumps(requests.json())
            comment.comment_status_code = requests.status_code
            return comment
        else:
            comment = Response()
            comment.error_message = result['error']['message']
            comment.error_info_as_json = json.dumps(requests.json())
            comment.error_status_code = requests.status_code
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
        if 200 <= requests.status_code < 400:
            message = Response()
            message_details = []
            for i in result['results']['comments']:
                messages = Response()
                messages.comments_chat_type = i['chat_type']
                messages.comments_comment_before_id = i['comment_before_id']
                messages.comments_disable_link_preview = i['disable_link_preview']
                messages.comments_user_email = i['email']
                messages.comments_id = i['id']
                messages.comments_message = i['message']
                messages.comments_payload = i['payload']
                messages.comments_room_id = i['room_id']
                messages.comments_room_name = i['room_name']
                messages.comments_timestamp = i['timestamp']
                messages.comments_topic_id = i['topic_id']
                messages.comments_type = i['type']
                messages.comments_unique_temp_id = i['unique_temp_id']
                messages.comments_unix_timestamp = i['unix_timestamp']
                messages.comments_user_avatar_url = i['user_avatar_url']
                messages.comments_user_id = i['user_id']
                messages.comments_username = i['username']
                messages.comments_info_as_json = json.dumps(result['results']['comments'])
                message_details.append(messages)
            message.messages = message_details
            message.comments_as_json = json.dumps(requests.json())
            return message
        else:
            message = Response()
            message.error_message = result['error']['message']
            message.error_info_as_json = json.dumps(requests.json())
            message.error_status_code = requests.status_code
            return message
