#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016: Alignak contrib team, see AUTHORS.txt file for contributors
#
# This file is part of Alignak contrib projet.
#
# AlignakBackend is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# AlignakBackend is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with AlignakBackend.  If not, see <http://www.gnu.org/licenses/>.
"""
This file is used to send an Alignak notification by email
"""

import argparse
import smtplib
import time
import traceback
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate


def main():
    """
    Main function used to create and send mail

    :return: None
    """
    args = parse_args()
    msg = prepare_notification(args)
    return send(msg, args)

def parse_args():
    """
    Parse the arguments

    :return:
    """
    parser = argparse.ArgumentParser()
    # required=True
    # General arguments
    parser.add_argument('-d', '--debug', dest="debug",
                        help='Debug mode to see all information')
    # Currently unused options
    # parser.add_argument('-l', '--logfile', dest="logfile",
    #                     help='Define file to put logs. By default log to stdout')
    # parser.add_argument('-tt', '--test', dest="test",
    #                     help='Use a test notification (so with default values)')

    # Mail definition
    parser.add_argument('-fh', '--formathtml', action="store_true", dest="formathtml",
                        help="Use email in HTML format. By default, it's in text format")
    parser.add_argument('-fr', '--from', dest="From", required=True,
                        help="Email of the mail author")
    parser.add_argument('-to', '--to', dest="To", required=True,
                        help="Recipients emails. At least one email address but you can specify a "
                             "comma-separated list of email addresses.")
    parser.add_argument('-pr', '--prefix', dest="prefix", default='',
                        help="Define a prefix in the email subject")
    parser.add_argument('-u', '--urllogo', dest="urllogo",
                        default='https://raw.githubusercontent.com/Alignak-monitoring-contrib/'
                                'alignak-notifications/master/alignak.png',
                        help="URL of the logo for HTML email (size 120x35 px)")

    # SMTP parameters
    parser.add_argument('-S', '--SMTP', dest="smtp",
                        help='Define SMTP server address')
    parser.add_argument('-ST', '--SMTPPORT', dest="smtp_port",
                        help='Define SMTP server address')
    parser.add_argument('-SL', '--SMTPLOGIN', dest="smtp_login",
                        help='Define the login account for the SMTP server')
    parser.add_argument('-SP', '--SMTPPASSWORD', dest="smtp_password",
                        help='Define the password for the SMTP server')

    # Alignak / monitoring information
    parser.add_argument('-t', '--type', dest="type", required=True,
                        choices=['host', 'service'], help="Type of object")
    parser.add_argument('-nt', '--notificationtype', dest="notificationtype", required=True,
                        help="Type of the notification")
    parser.add_argument('-nc', '--notificationcount', dest="notificationcount", type=int,
                        help="Notification count")
    parser.add_argument('-hn', '--hostname', dest="hostname", required=True,
                        help="Name of the host")
    parser.add_argument('-sn', '--servicename', dest="servicename",
                        help="Name of the service")
    parser.add_argument('-ha', '--hostaddress', dest="hostaddress",
                        default='n/a', help="Address (IP) of the host")
    parser.add_argument('-s', '--state', dest="state", required=True,
                        help="State of the host / service")
    parser.add_argument('-ls', '--laststate', dest="laststate", required=True,
                        help="Last state of the host / service")
    parser.add_argument('-o', '--output', dest="output", required=True,
                        help="Output of the check plugin")
    parser.add_argument('-dt', '--durationtime', dest="durationtime", type=int, default=0,
                        help="Duration of the provided state in seconds")
    parser.add_argument('-db', '--datebegin', dest="datebegin", type=float, required=True,
                        help="Date + time of the beginning of the current state")
    parser.add_argument('-p', '--perfdata', dest="perfdata",
                        help="Performance data string returned by the check plugin")
    parser.add_argument('-i', '--impact', dest="impact",
                        help="Impact")
    parser.add_argument('-w', '--webui_url', dest="webui_url",
                        help="URL of the host/service in the Web User Interface")
    return parser.parse_args()


def prepare_notification(args):
    """
    Prepare the notification message (mails)

    :param args:
    :type args:
    :return: the message
    :rtype: MIMEMultipart
    """
    msg = MIMEMultipart('alternative')

    msg['Subject'] = args.prefix + subject(args)
    msg['From'] = args.From
    msg['To'] = args.To
    msg['Date'] = formatdate()

    text_msg = generate_text(args)
    part1 = MIMEText(text_msg, 'plain', 'utf-8')
    msg.attach(part1)
    if args.formathtml:
        html_msg = generate_html(args)
        part2 = MIMEText(html_msg, 'html', 'utf-8')
        msg.attach(part2)
    return msg


def subject(args):
    """
    Create the subject of the notifications

    :param args:
    :type args:
    :return: subject of the mail
    :rtype: str
    """
    title = []
    if args.type == 'host':
        title.append('%s - Host %s is %s' % (args.notificationtype, args.hostname, args.state))
    elif args.type == 'service':
        title.append('%s - Host %s , service %s is %s' % (args.notificationtype, args.hostname,
                                                          args.servicename, args.state))
    if args.durationtime:
        title.append(' since %s' % (time.strftime("%Hh%Mm%Ss", time.gmtime(args.durationtime))))

    if args.notificationcount and args.notificationcount > 1:
        title.append(', notification #%s' % (args.notificationcount))

    return ''.join(title)


def generate_html(args):
    """
    Create the HTML message for the email

    :param args:
    :type args:
    :return: the message in HTML format
    :rtype: str
    """

    state_color = get_state_color(args.state)
    last_state_color = get_state_color(args.laststate)

    html_content = ['<html>', '<head>',
                    '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">',
                    '</head>', '<body style="font-family: Helvetica;">']

    # css
    css_table = 'border-collapse: collapse;width: 650px;'
    css_table_title = 'border-radius: 6px;background-color: #0e7099;color: white;height: 60px;'
    css_state = 'height: 30px;background-color: %s;text-align: center;' \
                'font-size: 18px;' % state_color
    css_point = 'height: 20px;width: 20px;border-radius: 100%%;background-color: %s;' % state_color
    css_past = 'display: block;width: 100%%;height: 1px;border: 0;border-top: 2px solid %s;' \
               'margin: 0;padding: 0;' % state_color
    css_laststate = 'display: block;width: 100%%;height: 1px;border: 0;border-top: 2px solid %s;' \
                    'margin: 0;padding: 0;' % last_state_color
    css_future = 'display: block;width: 100%;height: 1px;border: 0;border-top: 2px dotted #ccc;' \
                 'margin: 1em 0;padding: 0;'
    css_point_title = 'text-align: center;font-size: 12px;color: #acacac;'
    css_length = 'text-align: center;vertical-align: bottom;font-size: 12px;' \
                 'color: %s;' % state_color
    css_end = 'width: 628px;display: block;height: 1px;border: 0;border-top: 1px solid #0e7099;'
    css_footer = 'padding-left: 10px;display: block;font-size: 11px;color: #0e7099;height: 30px;'
    css_separator = 'display: block;width: 180px;height: 2px;border: 0;' \
                    'border-top: 2px solid #ccc;margin: 10;padding: 10;'
    css_background = 'background-color: #f8f8f8;width: 648px;border-left: 1px solid #ccc;' \
                     'border-right: 1px solid #ccc;border-bottom: 1px solid #ccc;' \
                     'border-bottom-left-radius: 6px;border-bottom-right-radius: 6px;'

    # Head of the email
    html_content.append('<table style="%s %s">' % (css_table, css_table_title))
    html_content.append('<tr style="height: 60px">')
    html_content.append('<td rowspan="2" style="width:160px">')
    html_content.append('<img alt="Alignak" title="Alignak" width="120" '
                        'height="35" src="%s"/>' % args.urllogo)
    html_content.append('</td>')
    html_content.append('<td style="width:100px;height: 30px;font-size: 18px;">')
    html_content.append('<strong>Host</strong>')
    html_content.append('</td>')
    html_content.append('<td style="font-size: 18px;">')
    html_content.append(args.hostname)
    html_content.append('</td>')
    html_content.append('</tr>')

    html_content.append('<tr>')
    html_content.append('<td style="height: 30px;font-size: 18px;">')
    if args.type == 'service':
        html_content.append('<strong>Service</strong>')
    html_content.append('</td>')
    html_content.append('<td style="font-size: 18px;">')
    if args.type == 'service':
        html_content.append(args.servicename)
    html_content.append('</td>')
    html_content.append('</tr>')

    # State
    html_content.append('<tr style="height: 30px">')
    html_content.append('<td colspan="3" style="%s"><strong>' % css_state)
    html_content.append(args.state)
    html_content.append('</strong></td>')
    html_content.append('</tr>')

    html_content.append('</table>')

    # Second part with output of check
    html_content.append('<div style="%s">' % css_background)
    html_content.append('<table style="%sheight: 100px;">' % css_table)
    html_content.append('<tr>')
    html_content.append('<td style="width: 20px;">')
    html_content.append('</td>')
    html_content.append('<td style="width: 120px;">')
    html_content.append('<strong>Message</strong>')
    html_content.append('</td>')
    html_content.append('<td style="width: 510">')
    html_content.append(args.output)
    html_content.append('</td>')
    html_content.append('</tr>')

    if args.perfdata:
        html_content.append('<tr style="height: 10px;">')
        html_content.append('<td colspan=4>')
        html_content.append('</td>')
        html_content.append('</tr>')

        html_content.append('<tr>')
        html_content.append('<td style="width: 20px;">')
        html_content.append('</td>')
        html_content.append('<td style="width: 120px;">')
        html_content.append('<strong>Perfdata</strong>')
        html_content.append('</td>')
        html_content.append('<td style="width: 510">')
        html_content.append(args.perfdata)
        html_content.append('</td>')
        html_content.append('</tr>')

    if args.impact:
        html_content.append('<tr style="height: 10px;">')
        html_content.append('<td colspan=4>')
        html_content.append('</td>')
        html_content.append('</tr>')
        
        html_content.append('<tr>')
        html_content.append('<td style="width: 20px;">')
        html_content.append('</td>')
        html_content.append('<td style="width: 120px;">')
        html_content.append('<strong>Impact</strong>')
        html_content.append('</td>')
        html_content.append('<td style="width: 510">')
        for _ in range(int(args.impact)):
            html_content.append('&#9733;')
        html_content.append('</td>')
        html_content.append('</tr>')

    html_content.append('</table>')

    # separator with notification type
    html_content.append('<table style="%s">' % css_table)
    html_content.append('<tr>')
    html_content.append('<td style="width: 200px;">')
    html_content.append('<hr style="%s"/>' % css_separator)
    html_content.append('</td>')
    html_content.append('<td style="width: 250px;text-align: center;">')
    html_content.append('<strong>Notification type</strong> ')
    html_content.append(args.notificationtype)
    html_content.append('</td>')
    html_content.append('<td style="width: 200px;">')
    html_content.append('<hr style="%s"/>' % css_separator)
    html_content.append('</td>')
    html_content.append('</tr>')
    html_content.append('</table>')
    html_content.append('<br/>')
    html_content.append('<br/>')
    html_content.append('<br/>')

    # default, for durationtime < 3600 seconds
    line_width = 150
    if args.durationtime >= 86400:
        line_width = 500
    elif args.durationtime >= 3600:
        line_width = 300

    # timeline
    html_content.append('<table style="%s">' % css_table)
    html_content.append('<tr>')
    html_content.append('<td style="width: 25px;">')
    html_content.append('</td>')
    html_content.append('<td style="%swidth: 70px;"><strong>' % css_point_title)
    html_content.append(time.strftime("%a %d %b %H:%M:%S", time.gmtime(args.datebegin)))
    html_content.append('</strong></td>')
    html_content.append('<td style="%swidth: %dpx;">' % (css_length, (line_width - 50)))
    html_content.append(time.strftime("%Hh%Mm%Ss", time.gmtime(args.durationtime)))
    html_content.append('</td>')
    html_content.append('<td style="">')
    html_content.append('</td>')
    html_content.append('</tr>')
    html_content.append('</table>')

    html_content.append('<table style="%s">' % css_table)
    html_content.append('<tr>')
    html_content.append('<td style="width: 10px;">')
    html_content.append('</td>')
    html_content.append('<td style="width: 40px;padding:0;margin:0;">')
    html_content.append('<hr style="%s"/>' % css_laststate)
    html_content.append('</td>')
    html_content.append('<td style="width: 20px;padding:0;margin:0;">')
    html_content.append('<div style="%s"></div>' % css_point)
    html_content.append('</td>')
    html_content.append('<td style="width: %dpx;padding:0;margin:0;">' % line_width)
    html_content.append('<hr style="%s"/>' % css_past)
    html_content.append('</td>')
    html_content.append('<td style="padding:0;margin:0;">')
    html_content.append('<hr style="%s"/>' % css_future)
    html_content.append('</td>')
    html_content.append('<td style="width: 10px;">')
    html_content.append('</td>')
    html_content.append('</tr>')
    html_content.append('</table>')

    html_content.append('<table style="%sheight: 120px;">' % css_table)
    html_content.append('<tr>')
    html_content.append('<td style="width: 20px;">')
    html_content.append('</td>')
    html_content.append('<td">')
    if args.webui_url:
        html_content.append('To view more information: <a href="%s" target="_blank">'
                            '<img src="https://raw.githubusercontent.com/'
                            'Alignak-monitoring-contrib/alignak-webui/develop/alignak_webui/'
                            'htdocs/images/logo_webui_xxs.png"></a>' % args.webui_url)
    html_content.append('</td>')
    html_content.append('<td style="width: 20px;">')
    html_content.append('</td>')
    html_content.append('</table>')

    # footer
    html_content.append('<hr style="%s"/>' % css_end)
    html_content.append('<div style="%s">' % css_footer)
    html_content.append('This email was generated by Alignak on ')
    html_content.append(formatdate())
    html_content.append('</div>')

    html_content.append('</div>')
    html_content.append('</body></html>')

    # Create a unique message
    return '\r\n'.join(html_content)


def get_state_color(state):
    """
    Get right color for the state

    :param state: the state
    :type state: str
    :return: the color related of the state
    :rtype: str
    """
    # default state color => OK / UP
    state_color = '#27ae60'
    if state in ['WARNING', 'UNREACHABLE']:
        state_color = '#e67e22'
    if state in ['CRITICAL', 'DOWN']:
        state_color = '#e74c3c'
    if state == 'UNKNOWN':
        state_color = '#2980b9'
    if state == 'ACKNOWLEDGE':
        state_color = '#95a5a6'
    if state == 'DOWNTIME':
        state_color = '#9b59b6'
    return state_color


def generate_text(args):
    """
    Create the TEXT message for the email

    :param args:
    :type args:
    :return: the message in TEXT format
    :rtype: str
    """
    text_content = []

    # Head of the email
    text_content.append("      _       __    _                          __      ")
    text_content.append("     / \     [  |  (_)                        [  |  _  ")
    text_content.append("    / _ \     | |  __   .--./) _ .--.   ,--.   | | / ] ")
    text_content.append("   / ___ \    | | [  | / /'`\;[ `.-. | `'_\ :  | '' <  ")
    text_content.append(" _/ /   \ \_  | |  | | \ \._// | | | | // | |, | |`\ \ ")
    text_content.append("|____| |____|[___][___].',__` [___||__]\'-;__/[__|  \_]")
    text_content.append("                      ( ( __))                         ")
    text_content.append("")
    text_content.append('Host: %s' % args.hostname)
    if args.type == 'service':
        text_content.append('Service: %s' % args.servicename)
    text_content.append("")
    text_content.append("###########################################################")
    text_content.append('State: %s' % args.state)
    text_content.append("###########################################################")
    text_content.append("")
    text_content.append('Message: %s' % args.output)
    text_content.append("")
    if args.perfdata:
        text_content.append('Perfdata: %s' % args.perfdata)
        text_content.append("")
    if args.impact:
        impact = ''
        for _ in range(int(args.impact)):
            impact += '★'
        text_content.append('Impact: %s' % impact)
        text_content.append("")

    text_content.append("---------- Notification type %s ----------" % args.notificationtype)
    text_content.append("")

    # default, for durationtime < 3600 seconds
    line_width = 150
    if args.durationtime >= 86400:
        line_width = 500
    elif args.durationtime >= 3600:
        line_width = 300

    text_content.append('since date: %s' % time.strftime("%a %d %b %H:%M:%S", time.gmtime(args.datebegin)))
    text_content.append('since: %s' % time.strftime("%Hh%Mm%Ss", time.gmtime(args.durationtime)))
    text_content.append("")

    if args.webui_url:
        text_content.append('To view more information: %s' % args.webui_url)
        text_content.append("")

    # footer
    text_content.append('This email was generated by Alignak on %s' % formatdate())

    # Create a unique message
    return '\r\n'.join(text_content)


def send(msg, args):
    """
    Send the mail

    :param msg:
    :type msg:
    :param args:
    :type args:
    :return: None
    """
    if args.smtp:
        try:
            smtp = smtplib.SMTP(args.smtp, args.smtp_port)
            smtp.starttls()
            if args.smtp_login:
                smtp.login(args.smtp_login, args.smtp_password)
            smtp.sendmail(args.From, args.To, msg.as_string())
            smtp.quit()
        except Exception as exp:
            print("Exception: %s" % str(exp))
            print(traceback.format_exc(exp))
            # Return 3 as UNKNOWN
            return 3

        # Return 0 as OK
        return 0

    # Return 3 as UNKNOWN
    return 3


if __name__ == '__main__':
    exit_code = main()
    exit(exit_code)
