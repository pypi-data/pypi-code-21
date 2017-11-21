# Copyright 2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Modifications made by Cloudera are:
#     Copyright (c) 2016 Cloudera, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import os

from altuscli import ALTUS_ACCESS_KEY_ID_KEY_NAME, ALTUS_PRIVATE_KEY_KEY_NAME
from altuscli.compat import compat_input
from altuscli.exceptions import ProfileNotFound
from altuscli.extensions.commands import BasicCommand
from altuscli.extensions.configure import CREDENTIAL_FILE_COMMENT
from altuscli.extensions.configure.get import ConfigureGetCommand
from altuscli.extensions.configure.list import ConfigureListCommand
from altuscli.extensions.configure.set import ConfigureSetCommand
from altuscli.extensions.configure.writer import ConfigFileWriter

from . import mask_value


class InteractivePrompter(object):

    def get_value(self, current_value, config_name, prompt_text=''):
        if config_name in (ALTUS_ACCESS_KEY_ID_KEY_NAME, ALTUS_PRIVATE_KEY_KEY_NAME):
            current_value = mask_value(current_value)
        interactive_long_input = False
        if config_name == ALTUS_PRIVATE_KEY_KEY_NAME:
            # See THUN-222 for context on why this is necessary
            interactive_long_input = True
        response = compat_input(
            "%s [%s]: " % (prompt_text, current_value),
            interactive_long_input)
        if not response:
            # If the user hits enter, we return a value of None
            # instead of an empty string.  That way we can determine
            # whether or not a value has changed.
            response = None
        return response


class ConfigureCommand(BasicCommand):
    NAME = 'configure'
    DESCRIPTION = BasicCommand.FROM_FILE()
    SYNOPSIS = ('altus configure [--profile profile-name]')
    EXAMPLES = (
        'To create a new configuration::\n'
        '\n'
        '    $ altus configure\n'
        '    Altus Access Key ID [None]: accesskey\n'
        '    Altus Private Key [None]: privatekey\n'
        '\n'
        'To update just the access key id::\n'
        '\n'
        '    $ altus configure\n'
        '    Altus Access Key ID [***]:\n'
        '    Altus Private Key [****]:\n'
    )
    SUBCOMMANDS = [
        {'name': 'list', 'command_class': ConfigureListCommand},
        {'name': 'get', 'command_class': ConfigureGetCommand},
        {'name': 'set', 'command_class': ConfigureSetCommand},
    ]

    # If you want to add new values to prompt, update this list here.
    VALUES_TO_PROMPT = [
        # (logical_name, config_name, prompt_text)
        (ALTUS_ACCESS_KEY_ID_KEY_NAME, "Altus Access Key ID"),
        (ALTUS_PRIVATE_KEY_KEY_NAME, "Altus Private Key")
    ]

    def __init__(self, prompter=None, config_writer=None):
        super(ConfigureCommand, self).__init__()
        if prompter is None:
            prompter = InteractivePrompter()
        self._prompter = prompter
        if config_writer is None:
            config_writer = ConfigFileWriter()
        self._config_writer = config_writer

    def _run_main(self, client_creator, parsed_args, parsed_globals):
        # Called when invoked with no args "altus configure"
        new_values = {}
        # This is the config from the config file scoped to a specific
        # profile.
        try:
            context = client_creator.context
            config = context.get_scoped_config()
        except ProfileNotFound:
            config = {}
        for config_name, prompt_text in self.VALUES_TO_PROMPT:
            current_value = config.get(config_name)
            new_value = self._prompter.get_value(current_value, config_name,
                                                 prompt_text)
            if new_value is not None and new_value != current_value:
                new_values[config_name] = new_value
        config_filename = os.path.expanduser(
            context.get_config_variable('config_file'))
        if new_values:
            self._write_out_creds_file_values(context,
                                              new_values,
                                              parsed_globals.profile)
            if parsed_globals.profile is not None:
                new_values['__section__'] = (
                    'profile %s' % parsed_globals.profile)
            self._config_writer.update_config(new_values, config_filename)

    def _write_out_creds_file_values(self, context, new_values, profile_name):
        # The access_key/private_key are now *always* written to the shared
        # credentials file (~/.altus/credentials).
        credential_file_values = {}
        if ALTUS_ACCESS_KEY_ID_KEY_NAME in new_values:
            credential_file_values[ALTUS_ACCESS_KEY_ID_KEY_NAME] = new_values.pop(
                ALTUS_ACCESS_KEY_ID_KEY_NAME)
        if ALTUS_PRIVATE_KEY_KEY_NAME in new_values:
            credential_file_values[ALTUS_PRIVATE_KEY_KEY_NAME] = new_values.pop(
                ALTUS_PRIVATE_KEY_KEY_NAME)
        if credential_file_values:
            if profile_name is not None:
                credential_file_values['__section__'] = profile_name
            shared_credentials_filename = os.path.expanduser(
                context.get_config_variable('credentials_file'))
            self._config_writer.update_config(
                credential_file_values,
                shared_credentials_filename,
                config_file_comment=CREDENTIAL_FILE_COMMENT)
