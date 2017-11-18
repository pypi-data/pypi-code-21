import re
from utils.const import TYPES, PMESSAGE_FORMAT

FORMAT = PMESSAGE_FORMAT


def set_format(new_format: 'dict of str: str'):
    for response_type, response_format in TYPES.items():
        FORMAT[response_type] = response_format


class Response:
    """Represents any form of response from IRC server.

    Supported Operations:

    +-----------+------------------------------------------------+
    | Operation |                 Description                    |
    +===========+================================================+
    | str(x)    | Returns pretty representation of the response. |
    +-----------+------------------------------------------------+
    | repr(x)   | Returns raw representation of the response.    |
    +-----------+------------------------------------------------+

    Attributes
    -----------
    raw_msg : str
        Raw message response from Twitch IRC server.
    """

    def __init__(self, raw_msg: str):
        self.raw_msg = raw_msg

        # Detect and separate TAGS
        (tags, no_tag_part) = self._separate_tags(raw_msg)
        self.tags = tags

        # Define the type
        (self.type, inspection) = self._define_the_type(no_tag_part)

        # Set variable parameters
        if self.type == 'CONNECTION':
            self.code = inspection.group(1)
            self.user = inspection.group(2)
            self.message = inspection.group(3)
        elif self.type == 'USER_LIST':
            self.code = '353'
            self.user = inspection.group(1)
            self.channel = inspection.group(2)
            self.viewers = []
            for user in (inspection.group(3)).split(' '):
                self.viewers.append(user)
            self.pviewers = ''
            for user in self.viewers:
                self.pviewers += (user + ', ')
            self.pviewers = self.pviewers[:-2]
            self.viewers.sort()
        elif self.type == 'USER_LIST_END':
            self.code = '366'
            self.message = 'End of /NAMES list'
        elif self.type == 'INVALID_CMD':
            self.code = '421'
            self.user = inspection.group(1)
            self.command = inspection.group(2)
        elif self.type == 'CAPABILITY_REG':
            if inspection.group(1) == 'ACK':
                self.success = True
                self.psuccess = 'accepted'
            elif inspection.group(1) == 'NAK':
                self.success = False
                self.psuccess = 'not accepted'
            else:
                self.type = 'UNDEFINED'
            self.capability = inspection.group(2)
        elif self.type in ['JOIN', 'PART']:
            self.user = inspection.group(1)
            self.channel = inspection.group(2)
        elif self.type == 'PRIVMSG':
            self.user = inspection.group(1)
            self.channel = inspection.group(2)
            self.message = inspection.group(3)
        elif self.type in ['OP', 'DEOP']:
            self.channel = inspection.group(1)
            self.user = inspection.group(2)
        elif self.type == 'NOTICE':
            self.notice_id = inspection.group(1)
            self.channel = inspection.group(2)
            self.message = inspection.group(3)
        elif self.type == 'HOSTSTART':
            self.channel = inspection.group(1)
            self.target_channel = inspection.group(2)
            self.viewers = inspection.group(3)
        elif self.type == 'HOSTEND':
            self.channel = inspection.group(1)
            self.viewers = inspection.group(2)
        elif self.type == 'BAN':
            self.channel = inspection.group(1)
            self.user = inspection.group(2)
        elif self.type in ['USERSTATE', 'ROOMSTATE']:
            self.channel = inspection.group(1)
        elif self.type == 'SUB':
            self.channel = inspection.group(1)
            self.message = inspection.group(2)
        elif self.type == 'USERNOTICE':
            self.channel = inspection.group(1)
        elif self.type == 'GLOBALUSERSTATE':
            pass

    def __str__(self):
        if self.type == 'UNDEFINED':
            return self.raw_msg

        if self.type == 'BAN':
            if 'ban-duration' in self.tags.keys():
                self.ban_duration = self.tags['ban-duration']
                self.type = 'TIMEOUT'

        try:
            pmessage = str(FORMAT[self.type]).format(self)

        except Exception:
            # TODO: Throw custom exception with more details
            try:
                pmessage = str(PMESSAGE_FORMAT[self.type]).format(self)
            except Exception:
                return self.raw_msg
        return pmessage

    def __repr__(self):
        return self.raw_msg

    @staticmethod
    def _separate_tags(raw_msg):
        tags_pattern = re.compile(r'^@(\S+) :.+')
        tags_part = re.compile(r'^@(\S+) ')
        inspection = re.search(tags_pattern, raw_msg)
        if inspection is not None:
            tags = dict()
            for pair in inspection.group(1).split(';'):
                tags[str(pair.split('=')[0])] = str(pair.split('=')[1])
            return tags.copy(), tags_part.sub('', raw_msg)
        else:
            return dict(), raw_msg

    @staticmethod
    def _define_the_type(response):
        (response_type, inspection) = 'UNDEFINED', None
        for response_type, patt in TYPES.items():
            inspection = re.search(patt, response)
            if inspection is not None:
                break
        return response_type, inspection
