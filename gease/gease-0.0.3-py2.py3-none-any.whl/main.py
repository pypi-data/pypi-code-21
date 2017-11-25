"""
    gease
    ~~~~~~~~~~~~~~~~~~~

    Make github release at command line

    :copyright: (c) 2017 by Onni Software Ltd.
    :license: MIT License, see LICENSE for more details

"""

import sys
import crayons

from gease._version import __version__, __description__
from gease.release import EndPoint
import gease.utils as utils
import gease.constants as constants
import gease.exceptions as exceptions

HELP = """%s. version %s

Usage: %s

where:

   release message is optional. It could be a quoted string or space separate
   string

Examples:

   gs gease v0.0.1 first great release
   gs gease v0.0.2 "second great release"
""" % (
    crayons.yellow('gease ' + __description__),
    crayons.magenta(__version__, bold=True),
    crayons.yellow('gs repo tag [release message]', bold=True),
)


def main():
    if len(sys.argv) < 3:
        if len(sys.argv) == 2:
            error(constants.NOT_ENOUGH_ARGS)
        print(HELP)
        sys.exit(-1)

    repo = sys.argv[1]
    tag = sys.argv[2]
    msg = " ".join(sys.argv[3:])
    try:
        user = get_default_user()
        if len(msg) == 0:
            msg = constants.DEFAULT_RELEASE_MESSAGE
        release = EndPoint(user, repo)
        url = release.publish(tag_name=tag, name=tag, body=msg)
        print(constants.MESSAGE_FMT_RELEASED % crayons.green(url))
    except exceptions.RepoNotFoundError:
        fatal("%s does not exist!" % repo)
    except exceptions.AbnormalGithubResponse as e:
        fatal(str(e))
    except exceptions.NoGeaseConfigFound as e:
        fatal(str(e))
    except exceptions.ReleaseExistException as e:
        fatal("Release %s exists" % tag)
    except KeyError as e:
        fatal("Key %s is not found" % str(e))


def get_default_user():
    return utils.get_info(constants.KEY_GEASE_USER)


def error(message):
    print('Error: %s' % crayons.red(message))


def fatal(message):
    error(message)
    sys.exit(-1)


if __name__ == '__main__':
    main()
