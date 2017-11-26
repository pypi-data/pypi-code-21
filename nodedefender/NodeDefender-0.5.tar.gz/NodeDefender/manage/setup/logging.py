from NodeDefender.manage.setup import (manager, print_message, print_topic,
                                       print_info)
from flask_script import prompt
import NodeDefender


supported_loggtypes = ['local', 'syslog']
supported_levels = ['debug', 'info', 'warning', 'error', 'critical']

@manager.command
def logging():
    print_topic("Logging")
    print_info("Logging to store runtime- information. If disabled it will be\
               printed to standard output")
    
    enabled = None
    while enabled is None:
        enabled = prompt("Enable Logging(Y/N)").upper()
        if 'Y' in enabled:
            enabled = True
        elif 'N' in enabled:
            enabled = False
        else:
            enabled = None
    NodeDefender.config.logging.set_cfg(enabled = enabled)

    if enabled:
        config_logging_type()
    return True

def config_logging_type():
    loggtype = None
    while loggtype is None:
        loggtype = prompt("Enter Logging Type(Syslog/Local)").lower()
        if loggtype not in supported_loggtypes:
            loggtype = None
    
    NodeDefender.config.logging.set_cfg(TYPE = loggtype)
    if loggtype == 'local':
        config_logging_filepath()
    elif loggtype == 'syslog':
        config_logging_host()
    config_logging_level()
    return True

def config_logging_filepath():
    filepath = None

    while not filepath:
        print_info("Enter filepath for loggingfile. Leading slah(/) for absolute-\
              path. Otherwise relative to current directory")
        filepath = prompt("Please Filename")

    if filepath[0] == '/':
        filepath = filepath
    else:
        filepath = NodeDefender.config.basepath + '/' + filepath
    NodeDefender.config.logging.set_cfg(filepath = filepath)

def config_logging_host():
    while not server:
        server = prompt('Enter Syslog IP')

    while not port:
        port = prompt('Enter Syslog Port')

    NodeDefender.config.set_cfg(server = server, port = port)
    return True

def config_logging_level():
    level = None
    print_info("Logging Level can be: debug, info, warning, error, critical")
    while level is None:
        level = prompt("Debug level").lower()
        if level not in supported_levels:
            level = None
    NodeDefender.config.logging.set_cfg(level = level)
    return True
