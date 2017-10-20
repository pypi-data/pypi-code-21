from abc import ABCMeta, abstractmethod
from time import sleep
import logging

from chatbot.models.response_message import ResponseMessage
from chatbot.utils.database_utils import DatabaseUtils
from chatbot.utils.facebook_utils import FacebookUtils

class ContentGenerator(object):

    __metaclass__ = ABCMeta

    def __init__(self, config):
        self.db_utils = DatabaseUtils(config.database, config.facebook['access_token'])
        self.fb_utils = FacebookUtils(config.facebook['access_token'])
        # self.mobile_utils = MobileUtils(constants)
        # self.web_utils = WebUtils(constants)
        # self.kik_utils = KikUtils(constants)

    @abstractmethod
    def run_method(self, name, data):
        """Run method that is required"""
        pass

    @abstractmethod
    def parse_input(self, message):
        """Parse user input to check if it matches expected input."""
        pass

    @abstractmethod
    def text_response(self, response):
        pass

    def handle_input(self, message):
        """Decide what kind of response is needed."""
        if self.db_utils.is_chatbot_active(message.sender) is not True:
            logging.error('{}: Chatbot status: is_chatbot_active is not True!'.format(message.sender))
            return
        if message.message_type == 'USER_TEXT':
            if self.db_utils.is_input_expected(message.sender):
                response = ResponseMessage(message.sender, message.message_service(), message.message, None, None)
                logging.info('{}: Expected input = True, Running method parse_input.'.format(message.sender))
                self.run_method("parse_input", response)
            else:
                res = dict()
                if message.entities is not None:
                    res['entity'] = "text_response"
                    res['confidence'] = 0
                    res['value'] = ''
                    for entity, value in message.entities.items():
                        if value[0].get('suggested') is True:
                            continue
                        if value[0].get('confidence') > res['confidence']:
                            res['confidence'] = value[0].get('confidence')
                            res['entity'] = entity
                            res['value'] = value[0].get('value')
                    logging.info('{}: NLP = entity: {}, value: {}, confidence: {}'.format(message.sender, res['entity'], res['value'], res['confidence']))
                    response = ResponseMessage(message.sender, message.message_service(), message.message, res['entity'] + '_' + res['value'], None)
                    logging.info('{}: Running method {}.'.format(message.sender, res['entity']))
                    self.run_method(res['entity'], response)
                else:
                    response = ResponseMessage(message.sender, message.message_service(), message.message, "text_response", None)
                    logging.info('{}: Running method text_response.'.format(message.sender))
                    self.run_method("text_response", response)
        else:
            response = ResponseMessage(message.sender, message.message_service(), message, None, None)
            logging.info('{}: Running method {}.'.format(message.sender, message.message_type.lower()))
            self.run_method(message.message_type, response)

    def sleep_and_typing(self, response, time):
        logging.info('{}: Sleep and typing for {}.'.format(response.sender, time))
        if response.service == 'facebook':
            self.fb_utils.typing_on(response.sender)
            sleep(time)

    def send_response(self, response, time):
        if response.service == 'facebook':
            self.fb_utils.typing_on(response.sender)
            sleep(time)
            data = self.fb_utils.generate_response(response)
            logging.info('{}: Sending response = {}.'.format(response.sender, data))
            self.send_fb_response(response.sender, data)
        # if response.service == 'mobile':
        #     data = self.mobile_utils.generate_response(response)
        #     self.send_mobile_response(response.sender, data)
        # if response.service == 'web':
        #     data = self.web_utils.generate_response(response)
        #     self.send_web_response(response.sender, data)
        # if response.service == 'kik':
        #     data = ""
        #     self.send_kik_response(response.sender, data)

    def send_fb_response(self, sender, data):
        self.fb_utils.quick_answer(sender, data)

    # def send_mobile_response(self, sender, data):
    #     self.mobile_utils.send(sender, data)
    #
    # def send_web_response(self, sender, data):
    #     self.web_utils.send(sender, data)
    #
    # def send_kik_response(self, sender, data):
    #     self.kik_utils.send(sender, data)

    def create_button(self, type, text=None, payload=None, url=None, wv_height=None, extensions=None, fallback=None):
        button = dict()
        if type == 'text' or type == 'postback' or type == 'phone_number':
            button['type'] = type
            button['title'] = text
            button['payload'] = payload
        elif type == 'web_url':
            button['type'] = type
            button['title'] = text
            button['url'] = url
            if wv_height:
                button['webview_height_ratio'] = wv_height
            if extensions:
                button['messenger_extensions'] = extensions
            if fallback:
                button['fallback_url'] = fallback
        elif type == 'location':
            button['type'] = 'location'
            button['title'] = text
            button['payload'] = payload
        elif type == 'element_share':
            button['type'] = type
        return button

    def create_default_action(self, type, url, extensions=None, wv_height=None, fallback=None):
        action = dict()
        action['type'] = type
        # action['title'] = title
        action['url'] = url
        if wv_height:
            action['webview_height_ratio'] = wv_height
        if extensions:
            action['messenger_extensions'] = extensions
        if fallback:
            action['fallback_url'] = fallback
        return action

    def create_element(self, title, subtitle=None, image_url=None, attachment=None, buttons=None, default_action=None):
        message = dict()
        message['title'] = title
        if subtitle:
            message['subtitle'] = subtitle
        if attachment:
            print("attachment_id = " + attachment)
            message['attachment_id'] = attachment
        if image_url:
            message['image_url'] = image_url
        if buttons:
            message['buttons'] = buttons
        if default_action:
            message['default_action'] = default_action
        return message

