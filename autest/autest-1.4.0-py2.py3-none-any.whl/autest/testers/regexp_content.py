import hosts.output as host
import re

from . import tester
from .file_callback import FileContentCallback
from autest.exceptions.killonfailure import KillOnFailureError

# this is around for backwards compatiblity. Ideally this is not needed
# given the better ExcludeExpression and ContainExpression
# see if we can weed this one out....


class RegexpContent(FileContentCallback):

    def __init__(self, regexp, description, killOnFailure=False, description_group=None):
        if isinstance(regexp, str):
            regexp = re.compile(regexp)
        self.__regexp = regexp
        super(RegexpContent, self).__init__(self.__check,
                                            description, killOnFailure, description_group)

    def __check(self, data):
        if not self.__regexp.search(data):
            return 'Search of regular expression "{0}" failed to find match'.format(self.__regexp.pattern)
