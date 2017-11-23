#!/usr/bin/env python
# Copyright Christian Bryn 2016-2017 <chr.bryn@gmail.com>

import os
import yaml
import logging
from slackclient import SlackClient

class SlackUp():
    """ Wrapper around SlackClient """
    def __init__(self, config={}):
        loglevel = 'warning'
        loglevel_numeric = getattr(logging, loglevel.upper(), None)
        if not isinstance(loglevel_numeric, int):
            raise ValueError('Invalid log level: %s' % loglevel)
        logging.basicConfig(level=loglevel_numeric)
        ## config defaults
        self.cfg = {
            'slack_token': '',
            'slack_channel': '#general',
            'slack_username': 'slackup',
            'slack_emoji': ':robot_face:'
        }

        ## read config from config file
        config_path = os.path.expanduser("~/.slackup.yml")
        if not os.path.exists(config_path):
            config_path = "/etc/slackup.yml"
        if os.path.exists(config_path):
            if oct(os.stat(config_path).st_mode)[-4:] != '0644':
                print('%s does not have the correct permissions - should be 0644' % (config_path))
                sys.exit(1)
            with open(config_path, 'r') as ymlfile:
                yml = yaml.load(ymlfile)
                # merge config:
                self.cfg.update(yml)
        else:
            # XXX: this is not true since we continue to pick up config:
            print('no config file found at %s, using defaults' % config_path)

        ## read config from environment
        if 'SLACK_TOKEN' in os.environ:
            self.cfg['slack_token'] = os.environ['SLACK_TOKEN']
        if 'SLACK_CHANNEL' in os.environ:
            self.cfg['slack_channel'] = os.environ['SLACK_CHANNEL']
        if 'SLACK_USERNAME' in os.environ:
            self.cfg['slack_username'] = os.environ['SLACK_USERNAME']
        if 'SLACK_EMOJI' in os.environ:
            self.cfg['slack_emoji'] = os.environ['SLACK_EMOJI']
        if 'SLACK_MESSAGE' in os.environ:
            self.cfg['slack_message'] = os.environ['SLACK_MESSAGE']

        ## finally, read config passed directly on invocation of class
        if config:
            self.cfg.update(config)

        if not self.cfg['slack_channel'].startswith('#'):
            self.cfg['slack_channel'] = '#' + self.cfg['slack_channel']


        ## validate config:
        # XXX: Improve this
        if not self._validate():
            print('Missing config options - bailing')
            raise ValueError
        self.slack = SlackClient(self.cfg['slack_token'])

    def _validate(self):
        if self.cfg['slack_token'] == '':
          return False
        if self.cfg['slack_channel'] == '':
          return False
        return True
    def post(self, message):
        """ Post to slack with current config """
        response = self.slack.api_call(
            "chat.postMessage", channel=self.cfg['slack_channel'], text=message,
            username=self.cfg['slack_username'], icon_emoji=self.cfg['slack_emoji']
        )
        if 'ok' in response:
            if response['ok']:
              return True
            else:
              logging.error("Error sending message: %s" % (response['error']))
              return False
        else:
            return False
    def post_attachment(self, message):
        """ Post to slack with 'message' as attachment with current config """
        response = self.slack.api_call(
            "chat.postMessage", channel=self.cfg['slack_channel'], attachments=[{"text": message}],
            username=self.cfg['slack_username'], icon_emoji=self.cfg['slack_emoji']
        )
        if 'ok' in response:
            if response['ok']:
              return True
            else:
              logging.error("Error sending message: %s" % (response['error']))
              return False
        else:
            return False
