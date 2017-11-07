
import copy
from functools import wraps
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging as logger
import hashlib
import random
import string

log = logger.getLogger(__name__)

def transform_keyboard_to_inline(keyboard):
    for_transform = copy.deepcopy(keyboard)
    def recurent_transform(keyboard):
        if not keyboard:
            raise ValueError
        if isinstance(keyboard, list):
            for key in keyboard:
                if not isinstance(key, list):
                    keyboard[keyboard.index(key)] = InlineKeyboardButton(str(key), callback_data=str(key))
                else:
                    recurent_transform(key)
            return keyboard
    return recurent_transform(for_transform)

def hash_pwd(text):
    return hashlib.md5(str(text).encode('utf-8')).hexdigest()

def property_from_class(cls):
    return property(doc=cls.__doc__, **dict_from_class(cls))

def dict_from_class(cls):
     return dict(
         (key, value)
         for (key, value) in cls.__dict__.items()
         if key not in set(type('A', (object,), {}).__dict__.keys())
         )

def send_action(action):
    def argswrap(func):
        @wraps(func)
        def decorator(self, *args, **kwargs):
            self.bot.send_chat_action(chat_id=self.chat_id, action=action)
            #sleep(0.5)
            return func(self, *args, **kwargs)
        return decorator
    return argswrap


def extract_chat_and_user(update):
    user = None
    chat = None

    if update.message:
        user = update.message.from_user
        chat = update.message.chat

    elif update.edited_message:
        user = update.edited_message.from_user
        chat = update.edited_message.chat

    elif update.inline_query:
        user = update.inline_query.from_user

    elif update.chosen_inline_result:
        user = update.chosen_inline_result.from_user

    elif update.callback_query:
        user = update.callback_query.from_user
        chat = update.callback_query.message.chat if update.callback_query.message else None

    return chat, user

def randomword(length):
   return ''.join(random.choice(string.hexdigits) for i in range(length))
