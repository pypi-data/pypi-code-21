# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017,BGI ltd.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may not
#   use this file except in compliance with the License. You may obtain a copy
#   of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

from __future__ import print_function, unicode_literals, division, absolute_import
import sys

reload(sys)
sys.setdefaultencoding('utf8')
import argparse
import logging
from bgionline.version import client_version
from bgionline.cli import *

logging.basicConfig(level=logging.DEBUG, )

args_list = sys.argv[1:]


class BOArgumentParser(argparse.ArgumentParser):
    def _print_message(self, message, tty=None):
        print(message)

    def _check_value(self, action, value):

        # converted value must be one of the choices (if specified)
        if action.choices is not None and value not in action.choices:
            choices = ("(choose from {})".format(", ".join(action.choices)))
            msg = "invalid choice: {choice}\n{choices}".format(choice=value, choices=choices)

            err = argparse.ArgumentError(action, msg)

    def exit(self, status=0, message=None):
        if isinstance(status, basestring):
            message = message + status if message else status
            status = 1
        if message:
            self._print_message(message, sys.stderr)
        sys.exit(status)

    def error(self, message):
        self.exit(2, '{help}\n{prog}: error: {msg}\n'.format(help=self.format_help(),
                                                             prog=self.prog,
                                                             msg=message))


class PrintVersion(argparse.Action):
    # Prints to stdout instead of the default stderr that argparse
    # uses (note: default changes to stdout in 3.4)
    def __call__(self, parser, namespace, values, option_string=None):
        print('bgonline command line client v%s' % (client_version))
        parser.exit(0)


parser = argparse.ArgumentParser(description="BGI Online Command line client, version %s" % client_version,
                                 usage="%(prog)s [-h] [--version] command ...")

parser.add_argument("--version", action=PrintVersion, nargs=0, help="show program's version number and exit")
parser.add_argument('--config',help='Configuration Files folder')
subparsers = parser.add_subparsers(title="available commands", dest="command", parser_class=BOArgumentParser)

# login
parser_login = subparsers.add_parser("login",
                                     help="Log in (interactively or with an existing API token)",
                                     description="Log in interactively and acquire credentials.  "
                                                 "Use --token to log in with an existing API token."
                                                 "Use case to view here:https://www.bgionline.cn/docs.html#/handbook/instructions",
                                     prog="bo login",
                                     parents=[])
parser_login.add_argument('--token', help='Authentication token to use')
host_action = parser_login.add_argument('--host', help='Log into the given auth server host (port must also be given)')
port_action = parser_login.add_argument('--port', type=int,
                                        help='Log into the given auth server port (host must also be given)')
protocol_action = parser_login.add_argument('--protocol',
                                            help='Used in conjunction with host and port arguments, gives the protocol to use when contacting auth server',
                                            default='https')
storage_host_action = parser_login.add_argument('--storage', help='Object Storage Service Host')
storage_host_action.help = host_action.help = port_action.help = protocol_action.help = argparse.SUPPRESS
parser_login.add_argument('--noprojects', dest='projects', help='Do not select available projects',
                          action='store_false')
parser_login.set_defaults(func=login)

# logout
parser_logout = subparsers.add_parser("logout",
                                      help="Log out and remove credentials",
                                      description='Log out and remove credentials'
                                                  "Use case to view here:https://www.bgionline.cn/docs.html#/handbook/instructions",
                                      prog="bo logout",
                                      parents=[])

parser_logout.set_defaults(func=logout)

# new
parser_new = subparsers.add_parser("new",
                                   help="Create a new user/project/analysis from scratch ",
                                   description="Use case to view here:https://www.bgionline.cn/docs.html#/handbook/instructions",
                                   prog="bo new",
                                   )

subparsers_new = parser_new.add_subparsers(title="create a new project/analysis from scratch",
                                           parser_class=BOArgumentParser)

# new user
parser_new_user = subparsers_new.add_parser("user", help="Create a new user account",
                                            description="Create a new user account"
                                                        "Use case to view here:https://www.bgionline.cn/docs.html#/handbook/instructions",
                                            prog="bo new user")

parser_new_user.add_argument("--password",
                             help="password for new user, default=<random generated>")

parser_new_user.add_argument("--email",
                             help="email address of new user, default=<random generated>")

parser_new_user.add_argument("name", help="name of the new user")

parser_new_user.set_defaults(func=new_user)

# new project
parser_new_project = subparsers_new.add_parser("project", help="Create a new user project",
                                               description="Create a new user project"
                                                           "Use case to view here:https://www.bgionline.cn/docs.html#/handbook/instructions",
                                               prog="bo new project")

parser_new_project.add_argument("name", help="name of the new project")
parser_new_project.add_argument("--desc", help="description of the new project")
parser_new_project.add_argument("-s", "--select", help="choose this new created as working project",
                                action='store_true')
parser_new_project.set_defaults(func=new_project)

# list and select projects
parser_select = subparsers.add_parser("select",
                                      help="List and select a project to switch to",
                                      description='Interactively list and select a project to switch to.'
                                                  "Use case to view here:https://www.bgionline.cn/docs.html#/handbook/instructions",
                                      prog="bo select",
                                      parents=[])

parser_select.add_argument('project', help='Name or ID of a project to switch to; '
                                           'if not provided a list will be provided for you', nargs='?', default=None)
parser_select.set_defaults(func=select)

# pwd
parser_pwd = subparsers.add_parser("pwd",
                                   help="Print current working directory",
                                   description="Print current working directory"
                                               "Use case to view here:https://www.bgionline.cn/docs.html#/handbook/instructions",
                                   prog="bo pwd", )
parser_pwd.set_defaults(func=pwd)

parser_whoami = subparsers.add_parser("whoami", prog="bo whoami")
parser_whoami.set_defaults(func=whoami)

parser_sh = subparsers.add_parser('sh', help='bo shell interpreter',
                                  description='This command launches an interactive shell.'
                                              "Use case to view here:https://www.bgionline.cn/docs.html#/handbook/instructions",
                                  prog="bo sh", )
parser_sh.set_defaults(func=sh)

parser_tree = subparsers.add_parser("tree",
                                    help="List folders and objects in a tree",
                                    description="List folders and objects in a tree"
                                                "Use case to view here:https://www.bgionline.cn/docs.html#/handbook/instructions",
                                    prog="bo tree",
                                    parents=[])
parser_tree.add_argument('path',
                         help='Folder (possibly in another project) to list the contents of, '
                              'default is the current directory in the current project. ',
                         nargs='?')
parser_tree.add_argument('--id', help='show file ID', action='store_true')
parser_tree.add_argument('-f', '--file', help='Show the file', action='store_true')
parser_tree.set_defaults(func=tree)

parser_ls = subparsers.add_parser("ls",
                                  help="List folders and/or objects in a folder",
                                  description='List folders and/or objects in a folder'
                                              "Use case to view here:https://www.bgionline.cn/docs.html#/handbook/instructions",
                                  prog="bo ls",
                                  parents=[])
parser_ls.add_argument('path',
                       help='Folder (possibly in another project) to list the contents of, '
                            'default is the current directory in the current project.  ',
                       nargs='?')
parser_ls.add_argument('-f', '--folders', help='show only folders', action='store_true')
parser_ls.add_argument('--id', help='show file ID', action='store_true')
parser_ls.set_defaults(func=ls)

parser_cd = subparsers.add_parser("cd",
                                  help="Change the current working directory",
                                  description='Change the current working directory'
                                              "Use case to view here:https://www.bgionline.cn/docs.html#/handbook/instructions",
                                  prog="bo cd",
                                  parents=[])
parser_cd.add_argument('path',
                       help='Folder (possibly in another project) to which to change the current working directory, '
                            'default is "/" in the current project')
parser_cd.set_defaults(func=cd)

parser_mkdir = subparsers.add_parser("mkdir",
                                     help="Create a new folder",
                                     description="Create a new folder"
                                                 "Use case to view here:https://www.bgionline.cn/docs.html#/handbook/instructions",
                                     prog="bo mkdir")
parser_mkdir.add_argument("-p", "--parents", help="no error if existing, create parent directories as needed",
                          action='store_true')
parser_mkdir.add_argument('paths', help='Paths to folders to create', metavar='path')
parser_mkdir.set_defaults(func=mkdir)

parser_rm = subparsers.add_parser('rm',
                                  help='Remove data objects and folders',
                                  description='Remove data objects and folders.'
                                              "Use case to view here:https://www.bgionline.cn/docs.html#/handbook/instructions",
                                  prog='bo rm', )
parser_rm.add_argument('path', nargs='?',
                       help='Remove file or directory by path,path end with "/" means directory, '
                            'and path end without "/" means file')
parser_rm.add_argument("-i", "--id", help="Remove file or directory ID")
parser_rm.set_defaults(func=rm)

parser_mv = subparsers.add_parser('mv', help='Move or rename objects and/or folders inside a project',
                                  formatter_class=argparse.RawTextHelpFormatter,
                                  description='Move or rename data objects and/or folders inside a single project.  '
                                              "Use case to view here:https://www.bgionline.cn/docs.html#/handbook/instructions",
                                              #'To copy data between different projects, use \'bo cp\' instead.',
                                  prog='bo mv', )
parser_mv.add_argument('sources', help='file and/or folder names to move', metavar='source')
parser_mv.add_argument('destination', help='Folder into which to move the sources or new pathname .  '
                                           'Must be in the same project.'
                                           'destination end with is not "/" execute rename,')
parser_mv.set_defaults(func=mv)

parser_upload = subparsers.add_parser("upload",
                                      help="Upload file(s) or directory",
                                      description="Upload local file(s) or directory.  "
                                                  "Use case to view here:https://www.bgionline.cn/docs.html#/handbook/instructions",
                                      prog="bo upload")
parser_upload.add_argument('local_path', help='Local file or directory to upload')
parser_upload.add_argument('bgionline_path',
                           help='BGIonline path to upload file(s) to '
                                '(default uses current project if not provided)'
                                'The default Project,Syntax:/folder/'
                                'Other projects, Syntax:projectID:/folder/')
parser_upload.add_argument('-c', '--concurrent',
                           help='The number of concurrent tasks, the default is 1, the maximum is 5',
                           type=int, default=1)
parser_upload.add_argument('-m', '--metadata', action='append', default=[],
                           help='key1=value1  ,Meta data to be associated (can have multiple -m options)',
                           )
parser_upload.add_argument('-w', '--wildcard', help='Use wildcard characters within the conditions '
                                                    'of file filters to perform pattern matching of file names')
parser_upload.add_argument('-mf', '--metadatafile',
                           help='Metadata\'s filepath'
                                '(Must be a CSV file)')
parser_upload.add_argument('-f', '--force', help='Force to upload, never prompt', action='store_true')
parser_upload.set_defaults(func=upload)

parser_download = subparsers.add_parser("download",
                                        help="Download file(s) or directory ",
                                        description="Download the contents of a file object or multiple objects."
                                                    "Use case to view here:https://www.bgionline.cn/docs.html#/handbook/instructions",
                                        prog="bo download")
parser_download.add_argument('bgionline_path',
                             help='download file or directory by path,path end with "/" means download directory, '
                                  'and path end without "/" means download file'
                                  'The default Project,Syntax:/folder/'
                                  'Other projects, Syntax:projectID:/folder/')
parser_download.add_argument('local_path',
                             help='Local filename or directory ')


parser_download.add_argument('-f', '--force', help='Force to download, never prompt', action='store_true')
parser_download.add_argument('-w', '--wildcard', help='Use wildcard characters within the conditions '
                                                      'of file filters to perform pattern matching of file names')
parser_download.add_argument('-c', '--concurrent',
                             help='The number of concurrent tasks, the default is 1, the maximum is 5',
                             type=int, default=1)
parser_download.set_defaults(func=download)

parser_find = subparsers.add_parser("find",
                                    help="Find data/job/app/project",
                                    description="Find data/job/app/project"
                                                "Use case to view here:https://www.bgionline.cn/docs.html#/handbook/instructions",
                                    prog="bo find", )

subparsers_find = parser_find.add_subparsers(title="create a new project/analysis from scratch",
                                             parser_class=BOArgumentParser)

parser_find_data = subparsers_find.add_parser("data", help="Find data",
                                              description="Find data"
                                                          "Use case to view here:https://www.bgionline.cn/docs.html#/handbook/instructions",
                                              prog="bo find data")

parser_find_data.add_argument('--path',
                              help='Folder in which to restrict the results'
                                   'default is "/" in the current project', default='/')
parser_find_data.add_argument('-m', '--metadata', action='append', default=[],
                              help='Key-value pair of a metadata or simply a metadata key; '
                                   'if only a key is metadata, matches a result that has the key with any value; '
                                   'repeat as necessary, e.g. "--metadata key1=val1 --metadata key2')
parser_find_data.add_argument('--name',
                              help='Name of the object')

parser_find_data.set_defaults(func=find_data)

parser_find_job = subparsers_find.add_parser("job", help="Find job",
                                             description="Find job"
                                                         "Use case to view here:https://www.bgionline.cn/docs.html#/handbook/instructions",
                                             prog="bo find job")

parser_find_job.add_argument('-p', '--project',
                             help='project ID,default uses current BGIonline project if not provided')

parser_find_job.set_defaults(func=find_job)

parser_find_app = subparsers_find.add_parser("app", help="Find app",
                                             description="Find app"
                                                         "Use case to view here:https://www.bgionline.cn/docs.html#/handbook/instructions",
                                             prog="bo find app")

parser_find_app.add_argument('-p', '--project',
                             help='project ID,default uses current BGIonline project if not provided')

parser_find_app.set_defaults(func=find_app)


parser_find_project = subparsers_find.add_parser("project", help="Find project",
                                             description="Find project"
                                                         "Use case to view here:https://www.bgionline.cn/docs.html#/handbook/instructions",
                                             prog="bo find project")

parser_find_project.set_defaults(func=find_project)


# parser_download = subparsers.add_parser("add",
#                                       help="Download file(s) or directory ",
#                                       description="Download the contents of a file object or multiple objects.  Use \"-o -\" to direct the output to stdout.",
#                                       prog="bo download")
#
#
# parser_download = subparsers.add_parser("delete",
#                                       help="",
#                                       description="Download the contents of a file object or multiple objects.  Use \"-o -\" to direct the output to stdout.",
#                                       prog="bo download")
#
parser_transfer = subparsers.add_parser("transfer",
                                        help="transfer project to user",
                                        description="Use case to view here:https://www.bgionline.cn/docs.html#/handbook/instructions",
                                        prog="bo transfer")
parser_transfer.add_argument('username',
                             help='Accept the username')
parser_transfer.add_argument('-p', '--project',
                             help='Need transfer project ID,default uses current BGIonline project if not provided')

parser_transfer.add_argument('--remain',
                             help='Remain in your project', action='store_true')

parser_transfer.set_defaults(func=transfer)


# def main(args_list):
def main():
    if OSTYPE == 'windows':
        import unicodedata
        import chardet

        class UnicodeStreamFilter:
            def __init__(self, target):
                self.target = target
                self.encoding = 'utf-8'
                self.errors = 'replace'
                self.encode_to = self.target.encoding

            def write(self, s):
                if type(s) == str:
                    s = s.decode("utf-8")
                s = s.encode(self.encode_to, self.errors).decode(self.encode_to)
                self.target.write(s)

        def getCharset(s):
            return chardet.detect(s)['encoding']

        if sys.stdout.encoding == 'cp936':
            sys.stdout = UnicodeStreamFilter(sys.stdout)

        if sys.getdefaultencoding() != 'gbk':
            reload(sys)
            sys.setdefaultencoding('gbk')
    args_list = sys.argv[1:]
    args = None
    logging.debug(args_list)
    if len(args_list) > 0:
        args = parser.parse_args(args_list)
    else:
        parser.print_help()

    if hasattr(args, 'func'):
        try:
            args.func(args)
            sys.stdout.flush()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
