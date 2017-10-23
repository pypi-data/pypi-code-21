import requests
import logging
import json

from chatbot.models.facebook_message import FacebookMessage

class FacebookUtils(object):
    def __init__(self, fbaccesstoken):
        self.fbaccesstoken = fbaccesstoken

    def generate_response(self, response):
        if response.response_type == 'text':
            return {"text": response.message}
        elif response.response_type == 'image':
            return {"attachment": {"type": "image", "payload": {"url": response.message}}}
        elif response.response_type == 'image_reusable':
            return {"attachment": {"type": "image", "payload": {"attachment_id": response.message}}}
        elif response.response_type == 'video':
            return {"attachment": {"type": "video", "payload": {"url": response.message}}}
        elif response.response_type == 'audio':
            return {"attachment": {"type": "audio", "payload": {"url": response.message}}}
        elif response.response_type == 'file':
            return {"attachment": {"type": "file", "payload": {"url": response.message}}}
        elif response.response_type == 'text_buttons':
            buttons = []
            for button in response.message['buttons']:
                if button['type'] == 'web_url':
                    b = {"type": button['type'], "title": button['title'], "url": button['url'],
                         "webview_height_ratio": button['webview_height_ratio']}
                    buttons.append(b)
                else:
                    b = {"content_type": button['type'], "title": button['title'], "payload": button['payload']}
                    buttons.append(b)
            data = {"text": response.message['text'], "quick_replies": buttons}
            return data
        elif response.response_type == 'horizontal_list' or response.response_type == 'horizontal_list_square':
            if response.response_type == 'horizontal_list_square':
                image_type = 'square'
            else:
                image_type = 'horizontal'
            elements = []
            for element in response.message:
                e = dict()
                e['title'] = element['title']
                if element.get('subtitle'):
                    e["subtitle"] = element['subtitle']
                if element.get('image_url'):
                    e["image_url"] = element['image_url']
                if element.get('attachment_id'):
                    e["attachment_id"] = element['attachment_id']
                if element.get('default_action'):
                    e["default_action"] = element['default_action']
                if element.get('buttons'):
                    buttons = []
                    for button in element['buttons']:
                        buttons.append(button)
                    e["buttons"] = buttons
                elements.append(e)
            data = {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "image_aspect_ratio": image_type,
                        "elements": elements
                    }
                }
            }
            return data
        elif response.response_type == 'vertical_list_cover' or response.response_type == 'vertical_list':
            elements = []
            for element in response.message:
                e = dict()
                if 'title' in element:
                    e['title'] = element['title']
                if element.get('subtitle'):
                    e["subtitle"] = element['subtitle']
                if element.get('image_url'):
                    e["image_url"] = element['image_url']
                if element.get('default_action'):
                    e["default_action"] = element['default_action']
                if element.get('buttons'):
                    buttons = []
                    for button in element['buttons']:
                        buttons.append(button)
                    e["buttons"] = buttons
                elements.append(e)
            if response.response_type == 'vertical_list':
                data = {
                    "attachment": {
                        "type": "template",
                        "payload": {
                            "template_type": "list",
                            "top_element_style": "compact",
                            "elements": elements
                        }
                    }
                }
            else:
                data = {
                    "attachment": {
                        "type": "template",
                        "payload": {
                            "template_type": "list",
                            "elements": elements
                        }
                    }
                }
            return data
        elif response.response_type == 'button':
            buttons = []
            for button in response.message['buttons']:
                    b = {"type": button['type'], "title": button['title'], "payload": button['payload']}
                    buttons.append(b)
            return {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "button",
                        "text": response.message['text'],
                        "buttons": buttons
                    }
                }
            }

    def parse_fb_message(self, data):
        """Parse Facebook message and return custom message object."""
        if data['object'] == 'page':
            for messagings in (entry['messaging'] for entry in data['entry']):
                for messaging in messagings:
                    sender = messaging['sender']['id']
                    message_type = None
                    message = None
                    image = None
                    location = None
                    entities = None
                    if messaging.get('message'):
                        if messaging['message'].get('text'):
                            message = messaging['message']['text']
                            if messaging['message'].get('nlp'):
                                entities = messaging['message']['nlp']['entities']
                            if messaging['message'].get('quick_reply'):
                                message_type = messaging['message']['quick_reply'].get('payload')
                                return FacebookMessage(sender, message, message_type, image, location, entities)
                            else:
                                message_type = "USER_TEXT"
                        elif messaging['message'].get('attachments'):
                            for attachment in messaging['message']['attachments']:
                                if attachment['type'] == 'image':
                                    image = attachment["payload"]['url']
                                    message_type = "USER_IMAGE"
                                elif attachment['type'] == 'location':
                                    location = {"type": "location", "data": {
                                        "coordinates": attachment["payload"]['coordinates']}}
                                    message_type = "USER_LOCATION"
                    elif messaging.get('delivery'):
                        pass
                    elif messaging.get('option'):
                        pass
                    elif messaging.get('postback'):
                        message_type = messaging['postback'].get('payload')
                    return FacebookMessage(sender, message, message_type, image, location, entities)

    def typing_on(self, user_id):
        data = {
            "recipient": {"id": user_id},
            "sender_action": "typing_on"
        }
        requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + self.fbaccesstoken,
                      json=data)
        logging.debug('{}: Typing ON.'.format(user_id))

    def typing_off(self, user_id):
        data = {
            "recipient": {"id": user_id},
            "sender_action": "typing_off"
        }
        requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + self.fbaccesstoken,
                      json=data)
        logging.debug('{}: Typing OFF.'.format(user_id))

    def whitelist(self, whitelist):
        resp = requests.post(
            "https://graph.facebook.com/v2.6/me/messenger_profile?access_token=" + self.fbaccesstoken,
            json=whitelist)
        logging.info('Whitelist = {}'.format(resp.content))

    def quick_answer(self, sender, data):
        response = {
            "recipient": {"id": sender},
            "message": data
        }
        resp = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + self.fbaccesstoken,
                             json=response)
        self.typing_off(sender)
        logging.debug('{}: Outgoing message \nMessage = {}'.format(sender, json.dumps(response, sort_keys=True, indent=4)))
        logging.debug('{}: Quick answer = {}'.format(sender, resp.content))


    def seen(self, user_id):
        data = {
            "recipient": {"id": user_id},
            "sender_action": "mark_seen"
        }
        resp = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + self.fbaccesstoken,
                             json=data)
        logging.info('{}: Seen = {}'.format(user_id, resp.content))

    def get_started_button(self, getstarted):
        resp = requests.post(
            "https://graph.facebook.com/v2.6/me/messenger_profile?access_token=" + self.fbaccesstoken, json=getstarted)
        logging.info('Get Started button = {}'.format(resp.content))

    def setup_persistant_menu(self, menu):
        resp = requests.post(
            "https://graph.facebook.com/v2.6/me/messenger_profile?access_token=" + self.fbaccesstoken, json=menu)
        logging.info('Persistant menu = {}'.format(resp.content))

    def setup_home_url(self, home_url):
        resp = requests.post(
            "https://graph.facebook.com/v2.6/me/messenger_profile?access_token=" + self.fbaccesstoken, json=home_url)
        logging.info('Home URL = {}'.format(resp.content))

    def upload_image(self, image):
        response = {
            "message": {
                "attachment": {
                    "type": "image",
                    "payload": {
                        "url": image,
                        "is_reusable": True,
                    }
                }
            }
        }
        resp = requests.post(
            "https://graph.facebook.com/v2.6/me/message_attachments?access_token=" + self.fbaccesstoken,
            json=response)
        logging.info('Upload image = {}'.format(resp.content))
        return resp
