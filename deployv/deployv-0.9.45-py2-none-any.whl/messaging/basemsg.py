# coding: utf-8

from os import path
import base64
from datetime import datetime
import uuid
from deployv.base import commandv
from deployv.helpers import json_helper, utils
import multiprocessing
import simplejson as json
import time
import logging
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser


_logger = logging.getLogger('deployv')


class BaseWorker(multiprocessing.Process):

    def __init__(self, configuration_object, sender_class, receiver_class,
                 worker_id):
        multiprocessing.Process.__init__(self)
        self._use_template = configuration_object.config.getboolean('deployer', 'use_template')
        self._db_owner = configuration_object.config.get('postgres', 'db_user')
        self._db_owner_passwd = configuration_object.config.get('postgres', 'db_password')
        self._backup_folder = configuration_object.config.get('deployer', 'backup_folder')
        self._working_folder = configuration_object.config.get('deployer', 'working_folder')
        self._nginx_folder = configuration_object.config.get('deployer', 'nginx_folder')
        self._domain = configuration_object.config.get('deployer', 'domain')
        self._max_instances = int(configuration_object.config.get('deployer', 'max_instances'))
        self._docker_url = configuration_object.config.get('deployer', 'docker_url')
        self._use_nginx = configuration_object.\
            config.get('deployer', 'use_nginx').upper() == 'TRUE'
        self._wid = worker_id
        self._node_id = configuration_object.config.get('deployer', 'node_id')
        self.stop_working = multiprocessing.Event()
        self.count = 0
        self._config_class = configuration_object
        self._receiver = receiver_class(configuration_object, self._node_id)
        self._sender = sender_class(configuration_object, self._node_id)

    def run(self):
        """ This is the start up method
        """
        raise NotImplementedError

    def exit(self):
        """ Exit worker, blocks until worker is finished and dead """
        self.signal_exit()
        while self.is_alive():  # checking `is_alive()` on zombies kills them
            time.sleep(1)

    def kill(self):
        """ This kill immediately the process, should not be used """
        raise NotImplementedError

    def check_message(self, message):
        """ Check if the message is properly formed and can be parsed, if nt a message with the
            error will be generated

        :param message: The message to be checked
        :return: The message object (:class:`~deployv.messaging.messagev.BasicMessage`)
            if no error, else False
        """
        message = json_helper.load_json(message)
        if not isinstance(message, dict):
            return False
        res = BasicMessage(message)
        model_schema = json_helper.build_schema(message.get('res_model'))
        validation = json_helper.validate_schema(message, schema=model_schema)
        if validation.get('error'):
            res.set_message_body({
                'error': validation.get('error'),
                'command': (message.get('message_body') or {}).get('command'),
            }, message_type='error')
            result = res.build_message()
            self._sender.send_message(result)
            return False
        return res

    def execute_rpc(self, message):
        _logger.info('Executing rpc for message in worker %s', self._wid)
        _logger.debug('%s worker received "%s"', self._wid,
                      json.dumps(message.original_message, sort_keys=True, indent=4))
        if message.receiver_node_id != self._node_id:
            _logger.error('Message in the wrong queue, does not match my wid: %s', self._node_id)
            return False
        self._sender.send_message(message.get_ack_message())
        _logger.debug('Ack sent')
        module = message.message_body.get('module')
        command_name = message.message_body.get('command')
        parameters = message.message_body.get('parameters')
        parameters.get('container_config', {}).update({
            'backup_folder': self._backup_folder,
            'working_folder': self._working_folder,
            'domain': self._domain,
            'use_template': self._use_template,
            'db_owner': self._db_owner,
            'db_owner_passwd': self._db_owner_passwd
        })
        parameters.update({
            'node': {
                'max_instances': self._max_instances,
                'docker_url': self._docker_url,
                'use_nginx': self._use_nginx,
                'nginx_folder': self._nginx_folder
            }
        })
        if module == 'commandv':
            command = commandv.CommandV(parameters)
            if hasattr(command, command_name):
                function = getattr(command, command_name)
                _logger.debug('Parameters: %s',
                              json.dumps(parameters, sort_keys=True, indent=4))
                res = function()
                _logger.debug('Function result :%s',
                              json.dumps(res, sort_keys=True, indent=4))
                time.sleep(10)
                message_body = {
                    'command': command_name,
                    'module': module,
                }
                message_body.update(res)
                message.set_message_body(message_body,
                                         message_type='result')
                response = message.build_message()
                _logger.debug('Message to send %s',
                              json.dumps(response, sort_keys=True, indent=4))
            else:
                message_body = {
                    'command': command_name,
                    'module': module,
                }
                message_body.update({'error': 'Command {cmd} does dot exits in module {module}'
                                    .format(cmd=command, module=module)})
                message.set_message_body(message_body,
                                         message_type='error')
                response = message.build_message()
            self._sender.send_message(response)
        _logger.info('%s worker done', self._wid)


class BasicMessage(object):
    """ Basic unit of communication that will be used for remote communications, you need at least
    specify the sender, receiver and a message body (command, error, status, etc)::

        >>> message = basemsg.BasicMessage()
        >>> message.sender_node_id = 'me01'
        >>> message.receiver_node_id = 'you01'
        >>> res = message.build_message()

    The :func:`~deployv.base.messagev.BasicMessage.build_message` method generates the proper
    message according to the defines schema for the communication (check test_messagev.py
    in the tests folder)

    """

    def __init__(self, message=None):
        envelope = {
            'version': '0.1',
            'message_id': str(uuid.uuid1()),
            'res_id': None,
            'deploy_id': None,
            'orchest_pipe_id': None,
            'sender_node_id': None,
            'receiver_node_id': None,
            'timestamp': None,
            'response_to': None,
            'message_body': dict(),
            'res_model': None,
            'model': None
        }
        self.__dict__ = envelope.copy()
        self._envelope = envelope.copy()
        self._files = list()
        self._message_types = ['error', 'result', 'parameters']
        if message is None:
            self._original_message = None
        elif isinstance(message, str):
            self._original_message = json.loads(message)
        elif isinstance(message, dict):
            self._original_message = message.copy()
        else:
            raise TypeError('Message is in a unsupported type {}'.format(type(message)))
        if self._original_message is not None:
            for key in envelope:
                setattr(self, key, self._original_message.get(key))

    @property
    def original_message(self):
        return self._original_message

    def attach_file(self, file_name, mime_type=None):
        assert path.isfile(file_name)
        self._files.append((file_name, mime_type))

    def set_message_body(self, message_body, message_type):
        """ Define the message body to be send

        :param message_body: Message body according to the documentation
        :param message_type: Error, ack, response or parameters
        :return: None
        """
        if message_type not in self._message_types:
            raise ValueError('Message type must be one of: {}'.format(str(self._message_types)))
        self.message_body = message_body

    def set_command(self, module_command, parameters):
        """ Helper method to create the message for a command

        :param module_command: Execute the command from the specified module.
            Must be in the format module.command
        :param parameters: The parameters that will be passed to the command in a dict
        :return: None
        """
        assert len(module_command.split('.')) == 2
        assert isinstance(parameters, dict)
        res = {
            'module': module_command.split('.')[0],
            'command': module_command.split('.')[1],
            'parameters': parameters
        }
        self.message_body = res

    def build_message(self):
        """ Builds the message with the provided properties in the class and according to the type

        :return: The formatted message in a dict
        """
        res = dict()
        attachments = list()
        for key in self._envelope:
            res.update({key: getattr(self, key)})
        res.update({
            'timestamp': datetime.utcnow().isoformat()})
        for fname in self._files:
            with open(fname(0)) as fname_descriptor:
                coded_file = utils.decode(base64.b64encode(utils.encode(fname_descriptor.read())))
            attachments.append({
                'file_name': path.basename(fname(0)),
                'file': coded_file,
                'type': fname(1)
            })
        if self._original_message:
            res.update({
                'receiver_node_id': self._original_message.get('sender_node_id'),
                'sender_node_id':  self._original_message.get('receiver_node_id'),
                'res_model': (self._original_message.get('res_model') or
                              self._original_message.get('model'))
            })
        if res.get('message_body').get('error', False) and attachments:
            res.get('message_body').get('error').update({'attachments': attachments})
        elif res.get('message_body').get('result', False) and attachments:
            res.get('message_body').get('result').update({'attachments': attachments})
        return res

    def get_ack_message(self, send_to=None):
        """ When a message is provided in the constructor this method generates an ack response
        with the proper parameters

        :param send_to: message route if none is provided will use default
                        passed to the class constructor
        :return: The ack message
        """
        if self._original_message is None:
            res = self.build_message()
        else:
            res = self._original_message.copy()
        res.update({
            'receiver_node_id': res.get('receiver_node_id'),
            'sender_node_id':  res.get('sender_node_id') if send_to is None else send_to,
            'res_model': res.get('res_model'),
            'model': res.get('model'),
            'res_id': res.get('res_id'),
            'deploy_id': res.get('deploy_id'),
            'timestamp': self.timestamp,
            'response_to': res.get('message_id'),
            'message_id': str(uuid.uuid1()),
            'message_body': {
                'module': res.get('message_body').get('module'),
                'command': res.get('message_body').get('command'),
                'ack': {
                    'message': 'Message received'
                }
            }
        })
        return BasicMessage(message=res)

    def get_message_str(self):
        """ A simple helper method that returns the message as a str but being sure that it will
        be safe for rabbitmq

        :return: The string representing the message
        """
        return json.dumps(self.build_message(),
                          ensure_ascii=True,
                          check_circular=True,
                          encoding='utf-8')

    def __repr__(self):
        return self.get_message_str()


class BaseFileConfig(object):
    def __init__(self, config_file, result=False):
        assert path.isfile(config_file)
        self.config = ConfigParser()
        self._result = result
