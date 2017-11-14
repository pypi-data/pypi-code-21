# ****************       BEGIN-STANDARD-COPYRIGHT      ***************
#
# Copyright (c) 2017, Spirent Communications.
#
# All rights reserved. Proprietary and confidential information of Spirent Communications.
#
#  ***************        END-STANDARD-COPYRIGHT       ***************

""" Private SLC configuration access functions."""

import os

def _get_int_var(name, default):
    """Returns the value an environment variable with the given name as integer, or the default value.

    Arguments:
    name -- env var name
    default -- default value

    Returns the value of the varibale, if it exists and can be converted to integer. Otherwise, returns the default
    value.
    """

    try:
        return int(os.getenv(name, default))
    except ValueError:
        return default

def get_agent_path():
    """Returns the agent location as a path to the Velocity agent folder."""
    return os.getenv('SPIRENT_SLC_AGENT_PATH', 'velocity-agent')

def get_agent_host_port():
    """Returns 'host:port' string, which points to the SLC host.

    May return 'local', which means to run the standalone host.
    """
    return os.getenv('SPIRENT_SLC_HOST', 'local')

def get_local_agent_host_port():
    """Returns 'host:port' string, which specifies on which network interface/port the standalone agent should bind."""
    return os.getenv('SPIRENT_SLC_LOCAL_HOST', 'localhost:9002')

def get_agent_password():
    """Returns the password to connect to an SLC host.

    May return None, in which case no password is required.
    """
    return os.getenv('SPIRENT_SLC_PASSWORD')

def get_agent_start_timeout():
    """Returns for how many seconds we should wait for the standalone agent to start before concluding the agent is
    failed to start.
    """
    return _get_int_var('SPIRENT_SLC_AGENT_START_TIMEOUT', 60)

def get_itar_path():
    """Returns the path to folder where iTars are placed."""
    res = os.getenv('ITAR_PATH')
    if res is None:
        return os.getcwd()
    return res

def get_license_server():
    """Returns license server in a form "host:port"""
    server = os.getenv('SPIRENT_SLC_LICENSE_SERVER')
    if server != None and len(server.strip()) == 0:
        return None
    return server

def get_license_proxy():
    """Returns license proxy in a form "host:port"""
    proxy = os.getenv('SPIRENT_SLC_LICENSE_PROXY')
    if proxy != None and len(proxy.strip()) == 0:
        return None
    return proxy

def is_verbose_mode():
    """Returns True if SPIRENT_SLC_VERBOSE proprty is defined """
    return os.getenv('SPIRENT_SLC_VERBOSE') != None
