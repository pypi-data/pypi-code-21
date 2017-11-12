#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading

from cloudshell.cli.cli import CLI
from cloudshell.cli.session_pool_manager import SessionPoolManager
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.shell.core.session.logging_session import LoggingSessionContext
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters, SNMPV2ReadParameters, SNMPV2WriteParameters


def get_cli(session_pool_size, pool_timeout=100):
    session_pool = SessionPoolManager(max_pool_size=session_pool_size, pool_timeout=pool_timeout)
    return CLI(session_pool=session_pool)


def get_logger_with_thread_id(context):
    """
    Create QS Logger for command context AutoLoadCommandContext, ResourceCommandContext
    or ResourceRemoteCommandContext with thread name
    :param context:
    :return:
    """
    logger = LoggingSessionContext.get_logger_for_context(context)
    child = logger.getChild(threading.currentThread().name)
    for handler in logger.handlers:
        child.addHandler(handler)
    child.level = logger.level
    for log_filter in logger.filters:
        child.addFilter(log_filter)
    return child


def get_api(context):
    """

    :param context:
    :return:
    """

    return CloudShellSessionContext(context).get_api()


def get_snmp_parameters_from_command_context(resource_config, api, force_decrypt=False):
    """
    :param ResourceCommandContext resource_config: command context
    :return:
    """

    if '3' in resource_config.snmp_version:
        return SNMPV3Parameters(ip=resource_config.address,
                                snmp_user=resource_config.snmp_v3_user or '',
                                snmp_password=api.DecryptPassword(resource_config.snmp_v3_password).Value or '',
                                snmp_private_key=resource_config.snmp_v3_private_key or '',
                                auth_protocol=resource_config.snmp_v3_auth_protocol or 'No Authentication Protocol',
                                private_key_protocol=resource_config.snmp_v3_priv_protocol or 'No Privacy Protocol')
    else:
        if resource_config.shell_name or force_decrypt:
            write_community = api.DecryptPassword(resource_config.snmp_write_community).Value or ''
        else:
            write_community = resource_config.snmp_write_community or ''

        if write_community:
            return SNMPV2WriteParameters(ip=resource_config.address, snmp_write_community=write_community)
        else:
            if resource_config.shell_name or force_decrypt:
                read_community = api.DecryptPassword(resource_config.snmp_read_community).Value or ''
            else:
                read_community = resource_config.snmp_read_community or ''

            return SNMPV2ReadParameters(ip=resource_config.address, snmp_read_community=read_community)


def parse_custom_commands(command, separator=";"):
    """Parse run custom command string into the commands list

    :param str command: run custom [config] command(s)
    :param str separator: commands separator in the string
    :rtype: list[str]
    """
    if not command:
        return []

    return command.strip(separator).split(separator)
