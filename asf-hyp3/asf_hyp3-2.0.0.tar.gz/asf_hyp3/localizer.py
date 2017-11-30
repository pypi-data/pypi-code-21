# localizer.py
# Rohan Weeden
# Created: July 21, 2017

# Load output messages for a certain language

import json
from os.path import join as os_join


class Localizer(object):
    def __init__(self, filename, does_raise=False):
        self.localization_file = filename
        self.messages = {}
        self.raise_on_missing_key = does_raise

    def load_from(self, path, fallback_locale):
        try:
            with open(os_join(path, self.localization_file)) as f:
                self.messages.update(json.load(f))
        except OSError:
            try:
                with open(os_join(path, fallback_locale)) as f:
                    self.messages.update(json.load(f))
            except:
                raise

    def to_local(self, message_name, *args):
        split_path = message_name.split(".")
        try:
            message = self.messages
            for path_component in split_path:
                message = message[path_component]
            return message.format(*args)
        except:
            if self.raise_on_missing_key is True:
                raise
            else:
                return message_name
