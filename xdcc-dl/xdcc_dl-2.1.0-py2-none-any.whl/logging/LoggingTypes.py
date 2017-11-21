u"""
Copyright 2016-2017 Hermann Krumrey

This file is part of xdcc-dl.

xdcc-dl is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

xdcc-dl is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with xdcc-dl.  If not, see <http://www.gnu.org/licenses/>.
"""


class FGColors(object):
    u"""
    Foreground Colours for colouring console output
    """

    DEFAULT = u'\033[39m'
    BLACK = u'\033[30m'
    RED = u'\033[31m'
    GREEN = u'\033[32m'
    YELLOW = u'\033[33m'
    BLUE = u'\033[34m'
    MAGENTA = u'\033[35m'
    CYAN = u'\033[36m'
    LIGHT_GRAY = u'\033[37m'
    DARK_GRAY = u'\033[90m'
    LIGHT_RED = u'\033[91m'
    LIGHT_GREEN = u'\033[92m'
    LIGHT_YELLOW = u'\033[93m'
    LIGHT_BLUE = u'\033[94m'
    LIGHT_MAGENTA = u'\033[95m'
    LIGHT_CYAN = u'\033[96m'
    WHITE = u'\033[97m'


class BGColors(object):
    u"""
    Background Colours for colouring console output
    """

    DEFAULT = u'\033[49m'
    BLACK = u'\033[40m'  # WHITE
    RED = u'\033[41m'
    GREEN = u'\033[42m'  # YELLOW
    YELLOW = u'\033[43m'
    BLUE = u'\033[44m'
    MAGENTA = u'\033[45m'
    CYAN = u'\033[46m'
    LIGHT_GRAY = u'\033[47m'
    DARK_GRAY = u'\033[100m'
    LIGHT_RED = u'\033[101m'
    LIGHT_GREEN = u'\033[102m'
    LIGHT_YELLOW = u'\033[103m'
    LIGHT_BLUE = u'\033[104m'
    LIGHT_MAGENTA = u'\033[105m'
    LIGHT_CYAN = u'\033[106m'
    WHITE = u'\033[107m'


class LoggingTypes(object):
    u"""
    The different logging types.

    Each logging type is assigned a background and foreground colour and a
    priority.
    The priority determines if the type of logging element is shown at all.
    In General, the logging levels mean:

        0: Must be shown under all circumstances except pure GUI output
        1: Will definitely be shown in a CLI environment
        2: Will generally be shown in a CLI environment
        3: Will be shown in environments where detailed output is desired
        4: Will generally not be shown, may lead to excessive amount of output
        5: Shows all undefined events. WILL lead to excessive output
        6: Has nothing to do with the task at hand

    Colour Coding:

        YELLOW/L_YELLOW BG:                    DCC / Downloads
        CYAN BG:                               WHOIS
        GREEN BG:                              CHANNELS
        BLUE BG:                               Messages
        DEFAULT BG + GREY/L_GREY/WHITE FG:     Welcome Messages,
                                               Message of the day,
                                               CTCP Version
        DEFAULT BG + DEFAULT/L_GREEN/L_RED FG: Connection
        DEFAULT BG + BLUE/L_BLUE FG:           Private Message/Notice
        DEFAULT BG + YELLOW/L_YELLOW FG:       Public Message/Notice
        DEFAULT BG + MANGENTA/L_MAGENTA FG:    Undefined events
    """

    INVISIBLE            = {u"bg_color": BGColors.DEFAULT,      u"fg_color": FGColors.DEFAULT,        u"priority": 0}
    DEFAULT              = {u"bg_color": BGColors.DEFAULT,      u"fg_color": FGColors.DEFAULT,        u"priority": 1}

    CONNECTION_ATTEMPT   = {u"bg_color": BGColors.DEFAULT,      u"fg_color": FGColors.DEFAULT,        u"priority": 2}
    CONNECTION_SUCCESS   = {u"bg_color": BGColors.DEFAULT,      u"fg_color": FGColors.LIGHT_GREEN,    u"priority": 2}
    CONNECTION_FAILURE   = {u"bg_color": BGColors.DEFAULT,      u"fg_color": FGColors.LIGHT_RED,      u"priority": 2}
    BANNED               = {u"bg_color": BGColors.LIGHT_RED,    u"fg_color": FGColors.LIGHT_MAGENTA,  u"priority": 1}

    WHOIS_SEND           = {u"bg_color": BGColors.CYAN,         u"fg_color": FGColors.BLACK,          u"priority": 2}
    WHOIS_SUCCESS        = {u"bg_color": BGColors.CYAN,         u"fg_color": FGColors.WHITE,          u"priority": 2}
    WHOIS_NO_RESULT      = {u"bg_color": BGColors.CYAN,         u"fg_color": FGColors.LIGHT_RED,      u"priority": 2}
    WHOIS_USER           = {u"bg_color": BGColors.CYAN,         u"fg_color": FGColors.DARK_GRAY,      u"priority": 4}
    WHOIS_SERVER         = {u"bg_color": BGColors.CYAN,         u"fg_color": FGColors.LIGHT_GRAY,     u"priority": 4}

    CHANNEL_JOIN_ATTEMPT = {u"bg_color": BGColors.GREEN,        u"fg_color": FGColors.BLACK,          u"priority": 2}
    CHANNEL_JOIN_SUCCESS = {u"bg_color": BGColors.GREEN,        u"fg_color": FGColors.LIGHT_GREEN,    u"priority": 2}
    CHANNEL_USERS        = {u"bg_color": BGColors.GREEN,        u"fg_color": FGColors.LIGHT_BLUE,     u"priority": 6}
    CHANNEL_TOPIC        = {u"bg_color": BGColors.GREEN,        u"fg_color": FGColors.MAGENTA,        u"priority": 6}
    CHANNEL_QUIT         = {u"bg_color": BGColors.GREEN,        u"fg_color": FGColors.RED,            u"priority": 6}
    CHANNEL_PART         = {u"bg_color": BGColors.GREEN,        u"fg_color": FGColors.LIGHT_MAGENTA,  u"priority": 6}
    CHANNEL_KICK         = {u"bg_color": BGColors.GREEN,        u"fg_color": FGColors.LIGHT_RED,      u"priority": 6}
    CHANNEL_MODE_CHANGE  = {u"bg_color": BGColors.GREEN,        u"fg_color": FGColors.LIGHT_YELLOW,   u"priority": 6}
    CHANNEL_ACTION       = {u"bg_color": BGColors.GREEN,        u"fg_color": FGColors.YELLOW,         u"priority": 6}
    CHANNEL_NICK_CHANGED = {u"bg_color": BGColors.GREEN,        u"fg_color": FGColors.LIGHT_CYAN,     u"priority": 6}

    MESSAGE_SEND         = {u"bg_color": BGColors.BLUE,          u"fg_color": FGColors.BLACK,         u"priority": 1}
    MESSAGE_RETRY        = {u"bg_color": BGColors.BLUE,          u"fg_color": FGColors.WHITE,         u"priority": 1}

    ALREADY_REQUESTED    = {u"bg_color": BGColors.BLUE,          u"fg_color": FGColors.LIGHT_RED,     u"priority": 2}

    INCORRECT_FILE       = {u"bg_color": BGColors.YELLOW,        u"fg_color": FGColors.LIGHT_MAGENTA, u"priority": 1}
    DCC_SEND_HANDSHAKE   = {u"bg_color": BGColors.YELLOW,        u"fg_color": FGColors.BLACK,         u"priority": 2}
    DCC_RESUME_REQUEST   = {u"bg_color": BGColors.YELLOW,        u"fg_color": FGColors.DARK_GRAY,     u"priority": 2}
    DCC_RESUME_SUCCESS   = {u"bg_color": BGColors.YELLOW,        u"fg_color": FGColors.WHITE,         u"priority": 2}
    DCC_RESUME_FAILED    = {u"bg_color": BGColors.YELLOW,        u"fg_color": FGColors.LIGHT_RED,     u"priority": 2}

    DOWNLOAD_START       = {u"bg_color": BGColors.LIGHT_YELLOW,  u"fg_color": FGColors.LIGHT_GREEN,   u"priority": 1}
    DOWNLOAD_RESUME      = {u"bg_color": BGColors.LIGHT_YELLOW,  u"fg_color": FGColors.LIGHT_BLUE,    u"priority": 1}
    DOWNLOAD_PROGRESS    = {u"bg_color": BGColors.LIGHT_YELLOW,  u"fg_color": FGColors.BLACK,         u"priority": 1}
    DOWNLOAD_WAS_DONE    = {u"bg_color": BGColors.LIGHT_YELLOW,  u"fg_color": FGColors.RED,           u"priority": 1}
    DOWNLOAD_INCOMPLETE  = {u"bg_color": BGColors.LIGHT_YELLOW,  u"fg_color": FGColors.LIGHT_RED,     u"priority": 2}

    PRIVATE_NOTICE       = {u"bg_color": BGColors.DEFAULT,      u"fg_color": FGColors.BLUE,           u"priority": 3}
    PRIVATE_MESSAGE      = {u"bg_color": BGColors.DEFAULT,      u"fg_color": FGColors.LIGHT_BLUE,     u"priority": 3}
    PUBLIC_NOTICE        = {u"bg_color": BGColors.DEFAULT,      u"fg_color": FGColors.YELLOW,         u"priority": 4}
    PUBLIC_MESSAGE       = {u"bg_color": BGColors.DEFAULT,      u"fg_color": FGColors.LIGHT_YELLOW,   u"priority": 4}

    MESSAGE_OF_THE_DAY   = {u"bg_color": BGColors.DEFAULT,      u"fg_color": FGColors.LIGHT_GRAY,     u"priority": 4}
    WELCOME              = {u"bg_color": BGColors.DEFAULT,      u"fg_color": FGColors.DARK_GRAY,      u"priority": 4}
    CTCP_VERSION         = {u"bg_color": BGColors.DEFAULT,      u"fg_color": FGColors.WHITE,          u"priority": 4}
    PING                 = {u"bg_color": BGColors.LIGHT_GREEN,  u"fg_color": FGColors.BLACK,          u"priority": 4}

    EVENT                = {u"bg_color": BGColors.DEFAULT,      u"fg_color": FGColors.MAGENTA,        u"priority": 5}
    EVENT_TEXT           = {u"bg_color": BGColors.DEFAULT,      u"fg_color": FGColors.LIGHT_MAGENTA,  u"priority": 5}
