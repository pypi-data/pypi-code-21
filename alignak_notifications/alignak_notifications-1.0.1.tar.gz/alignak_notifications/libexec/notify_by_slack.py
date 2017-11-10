#!/usr/bin/env python
# -*-coding:utf-8-*-
# Copyright (C) 2016:
#    Frédéric Mohier, frederic.mohier@gmail.com
#
# This file is part of Alignak notifications.
#
# Alignak notifications is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Alignak notifications is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with (WebUI).  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import socket
import logging
import getpass
import urllib
from optparse import OptionParser, OptionGroup

# Slack API
try:
    from slacker import Slacker
except Exception as e:
    sys.exit("[ERROR] Missing Slacker module. You must install Slacker (pip install slacker) to use this script. (%s)" % e)

# Global var
image_dir = '/var/lib/shinken/share/images'
customer_logo = 'customer_logo.jpg'
webui_config_file = '/etc/shinken/modules/webui.cfg'

webui2_config_file = '/etc/shinken/modules/webui2.cfg'
webui2_image_dir = '/var/lib/shinken/share/photos'


# Set up root logging
def setup_logging():
    log_level = logging.INFO
    if opts.debug:
        log_level = logging.DEBUG
    if opts.logfile:
        logging.basicConfig(filename=opts.logfile, level=log_level, format='%(asctime)s:%(levelname)s: %(message)s')
    else:
        logging.basicConfig(level=log_level, format='%(asctime)s:%(levelname)s: %(message)s')


# Get WebUI information
def get_webui_logo():
    company_logo = ''

    try:
        webui_config_fh = open(webui2_config_file)
    except IOError:
        # WebUI2 not installed ...
        full_logo_path = os.path.join(image_dir, customer_logo)
        if os.path.isfile(full_logo_path):
            return full_logo_path

    if opts.webui:
        # WebUI2 installed
        logging.debug('Webui2 is installed')
        webui_config = webui_config_fh.readlines()
        for line in webui_config:
            if 'company_logo' in line:
                company_logo = line.rsplit('company_logo')[1].strip()
                company_logo += '.png'
        logging.debug('Found company logo property: %s', company_logo)
        if company_logo:
            full_logo_path = os.path.join(webui2_image_dir, company_logo)
            if os.path.isfile(full_logo_path):
                logging.debug('Found company logo file: %s', full_logo_path)
                return full_logo_path
            else:
                logging.debug('File %s does not exist!', full_logo_path)
                return ''

    return company_logo


def get_webui_port():
    port = ''

    try:
        webui_config_fh = open(webui2_config_file)
    except IOError:
        # WebUI2 not installed, try WebUI1
        try:
            webui_config_fh = open(webui_config_file)
        except IOError:
            # No WebUI
            return ''
        else:
            # WebUI1 installed
            logging.debug('Webui1 is installed')
    else:
        # WebUI2 installed
        logging.debug('Webui2 is installed')

    logging.debug('Webui file handler: %s' % (webui_config_fh))
    webui_config = webui_config_fh.readlines()
    # logging.debug('Webui config: %s' % (webui_config))
    for line in webui_config:
        if 'port' in line:
            port = line.rsplit('port')[1].strip()
    return port


def get_webui_url():
    if opts.webui:
        hostname = socket.gethostname()
        webui_port = get_webui_port()
        if not webui_port:
            return

        if opts.webui_url:
            url = '%s/%s/%s' % (opts.webui_url, opts.notification_object, urllib.quote(host_service_var['Hostname']))
        else:
            url = 'http://%s:%s/%s/%s' % (hostname, webui_port, opts.notification_object, urllib.quote(host_service_var['Hostname']))

        # Append service if we notify a service object
        if opts.notification_object == 'service':
            url += '/%s' % (urllib.quote(notification_object_var['service']['Service description']))

        return url


if __name__ == "__main__":
    parser = OptionParser(description='Send notifications to a slack (https://slack.com/) platform.')

    group_debug = OptionGroup(parser, 'Debugging and test options', 'Useful to debug script when launched by the monitoring framework. Useful to just make a standalone test of script to see what it looks like.')
    group_host_service = OptionGroup(parser, 'Host/service macros to specify concerned object.', 'Used to specify usual macros for notification. If not specified then the script will try to get them from environment variable. You need to enable_environment_macros in alignak.cfg if you want to use them. It is not recommended to use environment variables in large environment. You would better use option -n, -c and -o depending upon which object is concerned.')
    group_webui = OptionGroup(parser, 'Web User Interface.', 'Used to include some Web User Interface information in the notifications.')
    group_slack = OptionGroup(parser, 'Slack options.', 'Used to specify the behaviour of the slack interactions.')

    # Debug and test options
    group_debug.add_option('-d', '--debug', dest='debug', default=False,
                      action='store_true', help='Set log level to debug (verbose mode)')
    group_debug.add_option('-t', '--test', dest='test', default=False,
                      action='store_true', help='Generate a test mail message')
    group_debug.add_option('-l', '--logfile', dest='logfile',
                      help='Specify a log file. Default: log to stdout.')

    # Host/service options
    group_host_service.add_option('-n', '--notification-object', dest='notification_object', type='choice', default='host',
                      choices=['host', 'service'], help='Choose between host or service notification.')
    group_host_service.add_option('-c', '--commonmacros', dest='commonmacros',
                      help='Double comma separated macros in this order : "NOTIFICATIONTYPE$,,$HOSTNAME$,,$HOSTADDRESS$,,$LONGDATETIME$".')
    group_host_service.add_option('-o', '--objectmacros', dest='objectmacros',
                      help='Double comma separated object macros in this order : "$SERVICEDESC$,,$SERVICESTATE$,,$SERVICEOUTPUT$,,$SERVICEDURATION$" for a service object and "$HOSTSTATE$,,$HOSTDURATION$" for an host object')
    # WebUI options
    group_webui.add_option('-w', '--webui', dest='webui', default=False,
                      action='store_true', help='Include link to the problem in WebUI.')
    group_webui.add_option('-u', '--url', dest='webui_url',
                      help='WebUI URL as http://my_webui:port/url')

    # Slack options
    group_slack.add_option('-K', '--key', dest='api_key',
                      help='Provide Slack API key')
    group_slack.add_option('-C', '--channel', dest='channel', default='alignak',
                      help='Slack channel, default is alignak, else specify a public channel (eg. #public-channel)')
    group_slack.add_option('-F', '--sender', dest='sender_id', default='@'.join((getpass.getuser(), socket.gethostname())),
                      help='Sender user name, default is current user (username@hostname)')
    group_slack.add_option('-I', '--sender-icon', dest='sender_icon', default=':exclamation:',
                      help='Sender icon, default is default BOT icon. Icon may be an emoji (eg. :ghost:) or the URL of an image file')
    group_slack.add_option('-T', '--title', dest='title', default=None,
                      help='Message title. Default is None')

    parser.add_option_group(group_debug)
    parser.add_option_group(group_host_service)
    parser.add_option_group(group_webui)
    parser.add_option_group(group_slack)

    (opts, args) = parser.parse_args()

    setup_logging()

    # Check and process arguments
    #
    # Retrieve and setup macros that make the message content
    if not opts.commonmacros:
        host_service_var = {
            'Notification type': os.getenv('NAGIOS_NOTIFICATIONTYPE'),
            'Hostname': os.getenv('NAGIOS_HOSTNAME'),
            'Host address': os.getenv('NAGIOS_HOSTADDRESS'),
            'Date': os.getenv('NAGIOS_LONGDATETIME')
        }
    else:
        macros = opts.commonmacros.split(',,')
        host_service_var = {
            'Notification type': macros[0],
            'Hostname': macros[1],
            'Host address': macros[2],
            'Date': macros[3]
        }

    if not opts.objectmacros:
        notification_object_var = {
            'service': {
                'Service description': os.getenv('NAGIOS_SERVICEDESC'),
                'Service state': os.getenv('NAGIOS_SERVICESTATE'),
                'Service output': os.getenv('NAGIOS_SERVICEOUTPUT'),
                'Service state duration': os.getenv('NAGIOS_SERVICEDURATION')
            },
            'host': {
                'Host state': os.getenv('NAGIOS_HOSTSTATE'),
                'Host state duration': os.getenv('NAGIOS_HOSTDURATION')
            }
        }
    else:
        macros = opts.objectmacros.split(',,')
        if opts.notification_object == 'service':
            notification_object_var = {
                'service': {
                    'Service description': macros[0],
                    'Service state': macros[1],
                    'Service output': macros[2],
                    'Service state duration': macros[3]
                },
                'host': {
                    'Host state': '',
                    'Host state duration': ''
            }

            }
        else:
            notification_object_var = {
                 'service': {
                    'Service description': '',
                    'Service state': '',
                    'Service output': '',
                    'Service state duration': ''
                },'host': {
                    'Host state': macros[0],
                    'Host state duration': macros[1]
                }
            }

    # Load test values
    if opts.test:
        notification_object_var = {
            'service': {
                'Service description': 'Test_Service',
                'Service state': 'TEST',
                'Service output': 'Houston, we got a problem here! Oh, wait. No. It\'s just a test.',
                'Service state duration': '00h 00min 10s'
            },
            'host': {
                'Hostname': 'Test_Host',
                'Host state': 'TEST',
                'Host state duration': '00h 00h 20s'
            }
        }

        host_service_var = {
            'Hostname': 'alignak',
            'Host address': '127.0.0.1',
            'Notification type': 'TEST',
            'Date': 'Now, test'
        }
    else:
        host_service_var.update(notification_object_var[opts.notification_object])

    logging.debug('notification_object_var: %s', notification_object_var)
    logging.debug('host_service_var: %s', host_service_var)

    if not host_service_var or not host_service_var['Hostname']:
        logging.error('You must define at least some host/service information (-c) or specify test mode (-t)')
        sys.exit(6)

    # check required arguments
    if not opts.api_key:
        logging.error('You must define at least an API key using -K')
        sys.exit(5)

    logging.debug('Slack API key: %s', opts.api_key)
    logging.debug('Slack channel: %s', opts.channel)
    logging.debug('Slack user: %s, icon: %s', opts.sender_id, opts.sender_icon)

    # Create text message
    logging.debug('Create notification skeleton')
    if opts.title:
        txt_content = [opts.title]
    else:
        txt_content = []

    mail_subject = {
        'host': 'Host %s alert for %s since %s' % (
            notification_object_var['host']['Host state'],
            host_service_var['Hostname'],
            notification_object_var['host']['Host state duration']
        ),
        'service': '%s on Host: %s about service %s since %s' % (
            notification_object_var['service']['Service state'],
            host_service_var['Hostname'],
            notification_object_var['service']['Service description'],
            notification_object_var['service']['Service state duration']
        )
    }

    txt_content.append(mail_subject[opts.notification_object])

    # Get url and add it in footer
    url = get_webui_url()
    logging.debug('Grabbed Shinken URL : %s' % url)
    if url:
        txt_content.append('More details on <%s|Shinken WebUI>' % url)

    message = '\r\n'.join(txt_content)
    logging.debug('Notification: %s', message)

    icon_url = 'http://lorempixel.com/48/48'
    icon_emoji = None
    if opts.sender_icon:
        if opts.sender_icon[:1] != ':':
            icon_url = opts.sender_icon
        else:
            icon_emoji = opts.sender_icon
    logging.debug('Slack icon: %s / %s', icon_url, icon_emoji)

    try:
        # Slack connection
        slack = Slacker(opts.api_key, timeout=10)

        # Send a message to the channel
        # Post as a bot
        slack.chat.post_message(
            '#%s' % opts.channel,
            message,
            username=opts.sender_id,
            as_user=False,
            icon_url=icon_url,
            icon_emoji=icon_emoji
        )
    except Exception as e:
        logging.error('Slack API problem: %s', e)
        exit(1)
