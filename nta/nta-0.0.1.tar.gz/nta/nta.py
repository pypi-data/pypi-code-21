# -*- encoding:utf-8 -*-
import sys
import json
import re
import requests

from .payload import *
from .utils import _byteify


class Event(object):
    def __init__(self, data=None):
        if data is None:
            data = {}

        self.data = data
        self.matched_callbacks = []
        self.first_visit = False

    @property
    def user_id(self):
        return self.data.get("user")

    @property
    def event(self):
        return self.data.get("event")

    @property
    def text_content(self):
        return self.data.get("textContent", {})

    @property
    def text(self):
        return self.text_content.get("text")

    @property
    def code(self):
        return self.text_content.get('code')

    @property
    def input_type(self):
        return self.text_content.get('inputType')

    @property
    def options(self):
        return self.data.get('options', {})

    @property
    def inflow(self):
        return self.options.get('inflow')

    @property
    def referer(self):
        return self.options.get('referer')

    @property
    def is_code(self):
        return self.code is not None and self.code != ""

    @property
    def is_open(self):
        return self.event == 'open'

    @property
    def is_leave(self):
        return self.event == 'leave'

    @property
    def is_event_friend(self):
        return self.event == 'friend'

    @property
    def is_send(self):
        return self.event == 'send'

    @property
    def is_pay(self):
        return self.event == 'pay_complete'

    @property
    def is_profile(self):
        return self.event == 'profile'

    @property
    def is_inflow_button(self):
        return self.inflow == 'button'

    @property
    def is_inflow_list(self):
        return self.inflow == 'list'

    @property
    def is_inflow_none(self):
        return self.inflow == 'none'

    @property
    def is_friend(self):
        return self.options.get('friend')

    @property
    def is_under14(self):
        return self.options.get('under14')

    @property
    def is_under19(self):
        return self.options.get('under19')

    @property
    def add_friend(self):
        return self.options.get('set') == "on"

    @property
    def delete_friend(self):
        return self.options.get('set') == "off"

    @property
    def enter_typing(self):
        return self.input_type == "typing"

    @property
    def enter_button(self):
        return self.input_type == 'button'

    @property
    def enter_sticker(self):
        return self.input_type == 'sticker'

    @property
    def enter_inquiry(self):
        return self.input_type == 'inquiry'

    @property
    def enter_vphone(self):
        return self.input_type == 'vphone'

    @property
    def pay_result(self):
        return self.options.get('paymentResult', {})

    @property
    def pay_success(self):
        return self.pay_result.get("code") == "Success"

    @property
    def pay_fail(self):
        return self.pay_result.get("code") == "Fail"

    @property
    def pay_message(self):
        return self.pay_result.get("message", "There is no message")

    @property
    def merchantPayKey(self):
        return self.pay_result.get("merchantPayKey")

    @property
    def merchantUserKey(self):
        return self.pay_result.get("merchantUserKey")

    @property
    def user_cellphone(self):
        return self.options.get('cellphone')


class Talk(object):
    def __init__(self, naver_talk_access_token, **options):
        self.naver_talk_access_token = naver_talk_access_token
        self._after_send = options.pop('after_send', None)

    _webhook_handlers = {}
    _default_button_callback = None
    _button_callbacks = {}
    _button_callbacks_key_regex = {}

    _before_process = None
    _after_send = None

    def _call_handler(self, name, func, *args, **kwargs):
        if func is not None:
            func(*args, **kwargs)
        elif name in self._webhook_handlers:
            self._webhook_handlers[name](*args, **kwargs)
        else:
            print("There's no matching %s handler" % name)

    def handle_webhook(self, payload, enter=None, leave=None, send=None, friend=None,
                       profile=None, pay=None, pay_success=None, pay_fail=None):
        if sys.version_info < (3, 0):
            data = json.loads(payload, object_hook=_byteify)
        else :
            data = json.loads(payload)

        event = Event(data)
        if self._before_process is not None:
            self._before_process(event)
        if event.is_code:
            event._matched_callbacks = self.get_code_callbacks(event)
            if not event._matched_callbacks:
                self._call_handler('send', send, event)
            else :
                for callback in event._matched_callbacks:
                    callback(event)
        elif event.is_send:
            self._call_handler('send', send, event)
        elif event.is_open:
            self._call_handler('open', enter, event)
        elif event.is_leave:
            self._call_handler('leave', leave, event)
        elif event.is_event_friend:
            self._call_handler('friend', friend, event)
        elif event.is_profile:
            self._call_handler('profile', profile, event)
        elif event.is_pay:
            if event.pay_success:
                self._call_handler('pay_success', pay_success, event)
            elif event.pay_fail:
                self._call_handler('pay_fail', pay_fail, event)
        else:
            print("Webhook received unknown messagingEvent:", event.event)

    def _send(self, payload, callback=None):
        r = requests.post("https://gw.talk.naver.com/chatbot/v1/event",
                          data=payload,
                          headers={'Content-type': 'application/json;charset=UTF-8',
                                   'Authorization': self.naver_talk_access_token})

        if r.status_code != requests.codes.ok:
            print(r.text)

        if callback is not None:
            callback(payload, r)

        if self._after_send is not None:
            self._after_send(payload, r)

    def send(self, user_id, message, quick_replies=None, notification=False, callback=None):
        payload = Payload(user_id=user_id, message=message,
                          quick_replies=quick_replies, notification=notification)

        self._send(payload.to_json(), callback=callback)

    def send_raw(self, user_id, type, message, event='send'):
        payload = {'user': user_id, 'event': event, type: message}

        self._send(json.dumps(payload))

    def invoke_profile(self, user_id, field="nickname", agreements=None):
        """
        Request for profile event
        Will invoke profile event from navertalk server
        :param user_id: Target user id
        :param field: nickname | phone | address
        :param agreements: [nickname, phone, address]
        """
        if agreements is None:
            agreements = ['cellphone', 'address']
        data = {
            "event": "profile",
            "user": user_id,
            "options": {
                "field": field,
                "agreements": agreements
            }
        }
        r = requests.post("https://gw.talk.naver.com/chatbot/v1/event",
                          data=data,
                          headers={'Content-type': 'application/json;charset=UTF-8',
                                   'Authorization': self.naver_talk_access_token})

        if r.status_code != requests.codes.ok:
            print(r.text)

    """
    decorations
    """

    def handle_open(self, func):
        self._webhook_handlers['open'] = func

    def handle_send(self, func):
        self._webhook_handlers['send'] = func

    def handle_leave(self, func):
        self._webhook_handlers['leave'] = func

    def handle_friend(self, func):
        self._webhook_handlers['friend'] = func

    def handle_profile(self, func):
        self._webhook_handlers['profile'] = func

    def handle_pay_success(self, func):
        self._webhook_handlers['pay_success'] = func

    def handle_pay_fail(self, func):
        self._webhook_handlers['pay_fail'] = func

    def handle_pay(self, func):
        self._webhook_handlers['pay'] = func

    def after_send(self, func):
        self._after_send = func

    def before_process(self, func):
        self._before_process = func

    def callback(self, *args):
        def wrapper(func):
            if len(args) <= 0:
                raise IndexError('Default callback can be used without ()')
            if not isinstance(args[0], list):
                raise ValueError("Callback params must be List")
            for arg in args[0]:
                self._button_callbacks[arg] = func

        if len(args) == 1 and callable(args[0]):
            self._default_button_callback = args[0]
        else:
            return wrapper

    def get_code_callbacks(self, event):
        callbacks = []
        for key in self._button_callbacks.keys():
            if key not in self._button_callbacks_key_regex:
                self._button_callbacks_key_regex[key] = re.compile(key + '$')
            if self._button_callbacks_key_regex[key].match(event.code):
                callbacks.append(self._button_callbacks[key])

        if not callbacks:
            if self._default_button_callback is not None:
                callbacks.append(self._default_button_callback)
        return callbacks
