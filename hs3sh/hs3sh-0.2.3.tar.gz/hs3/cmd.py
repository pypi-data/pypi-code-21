# The MIT License (MIT)
#
# Copyright (c) 2016-2017 Thorsten Simons (sw@snomis.de)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import cmd
import logging
import os
import sys
import time
from collections import OrderedDict
from pprint import pprint
from urllib.parse import urlsplit, urlunsplit
from threading import Lock
import boto3
import botocore
from boto3.s3.transfer import S3Transfer
from botocore.client import Config
from botocore.utils import fix_s3_host
from botocore.vendored.requests.packages.urllib3 import disable_warnings

from hs3 import calctime, _print, _
import hs3.init
import hs3.conf
import hs3.parse

PIPE = '|'  # output shall be piped
OUTFILE = '>'  # output shall be written to a file
EXTENDFILE = '>>'  # output shall extend a file


# noinspection PyUnresolvedReferences
class HS3shell(cmd.Cmd):
    intro = hs3.init.INTRO

    prompt = '--> '

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.endpoint = None  # the S3 endpoint
        self.mode = None  # 'aws' or 'compatible'
        self.ssl = True  # if https shall be used
        self.session = None  # the boto3 session
        self.s3 = None  # the connection
        self.bucket = None  # the bucket object to work with
        self.bucketname = None  # its name
        self.encrypted = False  # if objects shall be server side encrypted
        self.profiles = None  # a dict of dicts per profile in .hs3sh.conf
        self.profile = None  # the profile in use

    def preloop(self):
        disable_warnings()
        # read the configuration file(s)
        try:
            self.profiles = hs3.conf.readconf()
        except Exception as e:
            sys.exit('error: no config file loaded...\n\thint: {}'.format(e))

        # if we have a ~/.hs3shrc file, read it and execute the commands...
        # noinspection PyBroadException
        try:
            startupfile = os.path.join(os.path.expanduser("~"), ".hs3shrc")
            with open(startupfile, 'r') as inhdl:
                for cmnd in inhdl.readlines():
                    cmnd = cmnd.strip()
                    # skip comments and empty lines
                    if cmnd and not cmnd.startswith('#'):
                        self.cmdqueue.append('_exec ' + cmnd.strip())
        except Exception:
            pass

    def precmd(self, arg):
        """
        This overwrites the pre-command hook to strip off redirections from a
        command and sys.stdout accordingly accordingly.

        We are relying on everything being printed to sys.std. We realize
        redirections by simply mapping sys.stdout to a different file handle.

        :param arg:     the paramaters given with the command
        :return:        the command w/o the redirection or an empty string
                        if parsing failed
        """

        # first let's see if we need to look for pipe/outfile
        redir_type = redir_arg = None
        try:
            if arg.find(EXTENDFILE) != -1:
                redir_type = EXTENDFILE
                arg, redir_arg = arg.split(EXTENDFILE)
                redir_arg = redir_arg.strip()
            elif arg.find(OUTFILE) != -1:
                redir_type = OUTFILE
                arg, redir_arg = arg.split(OUTFILE)
                redir_arg = redir_arg.strip()
            elif arg.find(PIPE) != -1:
                redir_type = PIPE
                arg, redir_arg = arg.split(PIPE)
                redir_arg = redir_arg.strip()
        except Exception as e:
            _print('parsing redirction failed...\nhint: {}'.format(e))
            return ''

        if redir_type and arg.split()[0] in hs3.init.no_redir_cmds:
            print('error: no redirection for command "{}"...'
                  .format(arg.split()[0]))
            return ''

        if redir_type and not redir_arg:
            print('error: redirection without arguments...')
            return ''

        if redir_type == PIPE:
            try:
                sys.stdout = os.popen(redir_arg, 'w')
            except Exception as e:
                _print('redirection error...\nhint: {}'.format(e))
                return ''
        elif redir_type == OUTFILE:
            try:
                sys.stdout = open(redir_arg, 'w')
            except Exception as e:
                _print('redirection error...\nhint: {}'.format(e))
                return ''
        elif redir_type == EXTENDFILE:
            try:
                sys.stdout = open(redir_arg, 'a')
            except Exception as e:
                _print('redirection error...\nhint: {}'.format(e))
                return ''

        return arg

    def postcmd(self, stop, line):
        """
        This overwrites the ppst-command hook to reset sys.stdout to what it
        should be after a command with redirection was executed.
        """
        # make sure we flush the file handle to which sys.stdout points to at
        # the moment.
        print('', end='', flush=True)
        if sys.stdout != sys.__stdout__:
            sys.stdout.close()
            sys.stdout = sys.__stdout__
        return stop

    def emptyline(self):
        """Disable repetition of last command by pressing Enter"""
        pass

    def do__exec(self, arg):
        # Run a command given as parameters, but make sure to print a prompt
        # before. This is for running scripted commands (~/.hs3shrc)

        self.logger.debug('--> called "_run {}"'.format(arg))

        p = arg.split(maxsplit=1)
        command, params = p if len(p) > 1 else (arg, '')

        if command:
            print(self.prompt + arg, flush=True)
            return eval('self.do_{}("{}")'.format(command, params))
        else:
            return

    def do_acl(self, arg):
        'acl -b|-o name [-g user permission [, user permission]* '\
        '[-s canned ACL]\n' \
        '    Set Access Control Lists on a bucket or an object\n' \
        '    -b name = bucket\n' \
        '    -o name = object (needs to start with a "/"\n' \
        '    -g set per-user permission(s)\n' \
        '       permissions is one of full_control, write, write_acp,\n' \
        '       read, read_acp\n' \
        '    -s set canned ACL\n' \
        '       a canned ACLs is one of private, public-read,\n' \
        '       public-read-write, authenticated-read\n' \
        '    user is either:\n' \
        '       **for AWS**: a user\'s email address\n' \
        '       **for HCP**: a local HCP user name or an Active Directory '
        'user\n' \
        '       (if HCP is integrated with AD) like this: aduser@domain.com\n' \
        '       **for other S3 storage**: refer to the respective manual on '\
        'how to\n' \
        '       specify its users\n' \
        '       and **for all S3 stores**: one of allusers, authenticateduser,'\
        ' logdelivery\n' \
        '\n' \
        '*   If neither -g nor -s is given, list the actual ACLs\n' \
        '*   -g and -s are exclusive\n' \
        '*   If any specifier holds characters outside the ascii alphabet and '\
        'the\n' \
        '    underscore, surrond it with "quotation marks"'

        self.logger.info('--> called "acl {}"'.format(arg))

        if not self.profile:
            print('error: you need to connect, first...', file=sys.stderr)
            return

        try:
            para = hs3.parse.parse_acl(arg)
        except Exception as e:
            print('error: while parsing parameters...\nhint: {}'.format(e),
                  file=sys.stderr)
            return
        else:
            if hs3.parse.OBJECT in para.flags and not self.bucket:
                print('error: you need to attach a bucket, first...',
                      file=sys.stderr)
                return

        if para.isbucket:  # working on a bucket
            try:
                acl = self.s3.Bucket(para.name).Acl()
                acl.load()
            except Exception as e:
                _print('error: unable to access bucket ACLs...\nhint: {}'
                       .format(e), file=sys.stderr)
                return
            else:
                # we just list what we have
                if hs3.parse.GRANT not in para.flags and not para.canned:
                    print('ACLs for bucket {}'.format(para.name))
                    out = {'Owner': acl.owner, 'Grants': acl.grants}
                    pprint(out)
                elif para.canned and para.pairs:
                    print('error: -g and -s are exclusive...')
                elif para.canned:
                    # set canned ACL
                    if para.canned:
                        try:
                            acl.put(ACL=para.canned)
                        except Exception as e:
                            _print('error: setting a canned bucket ACL failed.'
                                   '..\nhint: {}'.format(e), file=sys.stderr)
                elif para.pairs:
                    newgrants = acl.grants

                    for g, p in para.pairs:
                        if g.lower() in hs3.init.AWSGROUPS.keys():
                            newgrants.append(
                                {'Grantee': {'URI': hs3.init.AWSGROUPS[g.lower()],
                                             'Type': 'Group',
                                             },
                                 'Permission': p})
                        else:
                            newgrants.append(
                                {'Grantee': {'EmailAddress': g,
                                             'Type': 'AmazonCustomerByEmail',
                                             },
                                 'Permission': p})

                    # To make sure we apply to the XSD found at
                    # https://admin.<yourhcp>.<yourdomain>.<tld>/static/xsd/AmazonS3.xsd,
                    # we need to sort all the entries accordingly
                    aclowner, newgrants = hs3.parse.aclcleanup(acl.owner, newgrants)

                    try:
                        _ACP = OrderedDict([('Owner', aclowner),
                                            ('Grants', newgrants)])
                        acl.put(AccessControlPolicy=_ACP)
                    except Exception as e:
                        _print(
                            'error: setting per-user bucket ACL failed...'
                            '\nhint: {}'.format(e), file=sys.stderr)
        else:  # working on an object
            try:
                acl = self.s3.Object(self.bucketname, para.name).Acl()
                acl.load()
            except Exception as e:
                _print('error: unable to access bucket ACLs...\nhint: {}'
                       .format(e), file=sys.stderr)
                return
            else:
                pprint(OrderedDict([('Owner', acl.owner),
                                    ('Grants', acl.grants)]))

    def do_attach(self, bucket):
        'attach <bucket_name>\n' \
        '    Attaches the bucket to be used by further commands. Think of\n' \
        '    change directory...'
        self.logger.info('--> called "attach {}"'.format(bucket))

        if not self.profile:
            print('error: you need to connect, first...', file=sys.stderr)
            return

        try:
            self.bucket = self.s3.Bucket(bucket)
            # switch this of, as it causes an error (404) when attaching a
            # bucket which is not owned by this user
            # self.bucket.load()
        except Exception as e:
            _print('error: attach of bucket "{}" failed\nhint: {}'
                   .format(bucket, e), file=sys.stderr)
        else:
            self.bucketname = bucket

    def do_bucket(self, arg):
        'bucket [-c|-cv|-r|-v] bucketname\n' \
        '    create or remove a bucket\n' \
        '    -c create <bucketname>\n' \
        '    -r remove bucket (needs to be empty)\n' \
        '    -v toggle versioning\n' \
        '    without any flags, the bucket\'s versioning status is shown'
        self.logger.info('--> called "bucket {}"'.format(arg))

        if not self.profile:
            print('error: you need to connect, first...', file=sys.stderr)
            return

        try:
            para = hs3.parse.paramcheck(arg, flags='cvr')
        except Exception as e:
            print('error: while parsing parameters...\nhint: {}'.format(e),
                  file=sys.stderr)
            return
        else:
            if not len(para.args):
                print('error: no bucketname specified...', file=sys.stderr)
                return
            else:
                bucket = para.args[0]
            if 'v' in para.flags and 'r' in para.flags:
                print('error: -v not possible with -r', file=sys.stderr)
                return

            if 'c' in para.flags:  # create bucket
                try:
                    bkt = self.s3.Bucket(bucket)
                    eval('bkt.create({})'.format(
                        'CreateBucketConfiguration={"LocationConstraint": "' +
                        self.profiles[self.profile]['region'] + '"}' if
                        self.profiles[self.profile]['region'] else ''))
                except Exception as e:
                    _print('error: create bucket failed...\nhint: {}'
                           .format(e), file=sys.stderr)
                else:
                    if 'v' in para.flags:
                        try:
                            bv = bkt.Versioning()
                            bv.enable()
                        except Exception as f:
                            _print(
                                'error: enabling versioning failed...\n'
                                'hint: {}'.format(f), file=sys.stderr)
                return
            if 'r' in para.flags:  # remove bucket
                try:
                    bkt = self.s3.Bucket(bucket)
                    bkt.delete()
                except Exception as e:
                    _print(
                        'error: delete bucket failed...\nhint: {}'.format(e),
                        file=sys.stderr)
                return

            # get info about versioning status
            try:
                bkt = self.s3.Bucket(bucket)
                bv = bkt.Versioning()
            except Exception as e:
                _print('error: can\'t get versioning status...\nhint: {}'
                       .format(e), file=sys.stderr)
                return

            if 'v' in para.flags and 'c' not in para.flags:
                # toggle versioning
                try:
                    if bv.status == 'Enabled':
                        bv.suspend()
                        bv.reload()
                        print('versioning is now {}'.format(
                            bv.status.lower() if bv.status else 'disabled'))
                    else:
                        bv.enable()
                        bv.reload()
                        print('versioning is now {}'.format(
                            bv.status.lower() if bv.status else 'disabled'))
                    return
                except Exception as e:
                    _print('error: can\'t toggle versioning status...\nhint: {}'
                           .format(e), file=sys.stderr)
                    return

            if not para.flags:  # show bucket status
                try:
                    print('versioning status: {}'.format(
                        bv.status.lower() if bv.status else 'disabled'))
                except Exception as e:
                    _print('error: can\'t get versioning status...\nhint: {}'
                           .format(e), file=sys.stderr)
                return
        print('error: invalid parameters...', file=sys.stderr)
        return

    def do_bye(self, arg):
        'Exit hs3sh gracefully.'
        self.logger.info('--> called "bye {}"'.format(arg))

        print('Ending gracefully...')
        return True

    def do_connect(self, arg):
        'connect <profile_name>\n' \
        '    Connect to an S3 endpoint using profile <profile_name>\n' \
        '    from ~/.hs3sh.conf or ./.hs3sh.conf'
        self.logger.info('--> called "connect {}"'.format(arg))

        try:
            para = hs3.parse.paramcheck(arg, flags='')
        except Exception as e:
            print('error: parameters invalid...\nhint: {}'.format(e),
                  file=sys.stderr)
            return
        else:
            if len(para.args) != 1:
                print(
                    'error: a profile_name as explicit parameter is required',
                    file=sys.stderr)
                return
            if para.args[0] not in self.profiles.keys():
                print('error: unknown profile: {}'.format(para.args[0]),
                      file=sys.stderr)
                return
            else:
                self.profile = para.args[0]
                self.mode = self.profiles[self.profile]['type']

            self.logger.debug('using profile {}'
                              .format(self.profiles[self.profile]))
            try:
                if self.mode == 'aws':
                    self.session = boto3.session.Session(
                        aws_access_key_id=self.profiles[self.profile][
                            'aws_access_key_id'],
                        aws_secret_access_key=self.profiles[self.profile][
                            'aws_secret_access_key'],
                        region_name=self.profiles[self.profile]['region'])
                    self.s3 = self.session.resource('s3', config=Config(
                        signature_version='s3v4'))
                else:
                    endpoint = ('https://' if self.profiles[self.profile][
                        'https'] else 'http://') + self.profiles[self.profile][
                                   'endpoint']
                    if self.profiles[self.profile]['port']:
                        endpoint = '{}:{}'.format(endpoint,
                                                  self.profiles[self.profile][
                                                      'port'])
                    self.logger.debug('endpoint is "{}"'.format(endpoint))
                    self.session = boto3.session.Session(
                        aws_access_key_id=self.profiles[self.profile][
                            'aws_access_key_id'],
                        aws_secret_access_key=self.profiles[self.profile][
                            'aws_secret_access_key'],
                        region_name=self.profiles[self.profile]['region'])
                    self.s3 = self.session.resource('s3',
                                                    endpoint_url=endpoint,
                                                    verify=False,
                                                    config=Config(
                                                        signature_version='s3'))
                    self.s3.meta.client.meta.events.unregister(
                        'before-sign.s3',
                        fix_s3_host)
            except Exception as e:
                print('error: connect failed\nhint: {}'.format(e),
                      file=sys.stderr)
            else:
                self.bucket = self.bucketname = None

    def do_cp(self, arg):
        'cp [-v version_id] source target ["metakey:metavalue"]*\n' \
        '    Request the S3 service to perform a server-side copy of (a '\
        'defined\n' \
        '    version_id of) source to target object, replacing eventually\n' \
        '    existing source metadata pairs with the named metadata pairs,\n' \
        '    if given; else copy the existing metadata pairs, along with the\n'\
        '    object.\n\n' \
        '    You can use the copy command to copy the source object to\n' \
        '    itself to create a new version of the source object with\n' \
        '    changed metadata pairs.'
        self.logger.info('--> called "cp {}"'.format(arg))

        if not self.profile:
            print('error: you need to connect, first...', file=sys.stderr)
            return

        if not self.bucket:
            print('error: you need to attach to a bucket, first...',
                  file=sys.stderr)
            return

        try:
            para = hs3.parse.paramcheck(arg, flags='v', meta=True)
        except Exception as e:
            _print('error: parameters invalid...\nhint: {}'.format(e),
                   file=sys.stderr)
            return
        else:
            _version = True if 'v' in para.flags else False
            if len(para.args) < (3 if _version else 2):
                print('error: at least {} parameter are required'
                      .format('three' if _version else 'two'), file=sys.stderr)
                return
            else:
                if 'v' in para.flags:
                    _ver = para.args[0]
                    _src = para.args[1]
                    _tgt = para.args[2]
                else:
                    _ver = None
                    _src = para.args[0]
                    _tgt = para.args[1]

        try:
            obj = self.s3.Object(self.bucketname, _tgt)
            if para.metadict:
                response = obj.copy_from(CopySource={'Bucket': self.bucketname,
                                                     'Key': _src,
                                                     'VersionId': _ver},
                                         Metadata=para.metadict,
                                         MetadataDirective='REPLACE')
            else:
                response = obj.copy_from(CopySource={'Bucket': self.bucketname,
                                                     'Key': _src,
                                                     'VersionId': _ver},
                                         MetadataDirective='COPY')
            if 'CopySourceVersionId' in response:
                print('CopySourceVersionId: {}'
                      .format(response['CopySourceVersionId']))
            if 'VersionId' in response:
                print('          VersionId: {}'.format(response['VersionId']))
        except Exception as f:
            _print('error: copy_from failed...\nhint: {}'.format(f),
                   file=sys.stderr)

    def do_get(self, arg):
        'get [-v version_id] object [localfile]\n' \
        '    Get (read) the latest (or a named version_id) of object and\n' \
        '    print it. If localfile is specified, write the object to it.'
        self.logger.info('--> called "get {}"'.format(arg))

        if not self.profile:
            print('error: you need to connect, first...', file=sys.stderr)
            return

        if not self.bucket:
            print('error: you need to attach to a bucket, first...',
                  file=sys.stderr)
            return

        try:
            para = hs3.parse.paramcheck(arg, flags='v', meta=False)
        except Exception as e:
            _print('error: parameters invalid...\nhint: {}'.format(e),
                   file=sys.stderr)
            return
        else:
            _version = True if 'v' in para.flags else False
            if len(para.args) < (2 if _version else 1):
                print('error: at least {} parameter are required'
                      .format('two' if _version else 'one'), file=sys.stderr)
                return
            else:
                if 'v' in para.flags:
                    _ver = para.args[0]
                    _src = para.args[1]
                    _tgt = para.args[2] if len(para.args) > 2 else None
                else:
                    _ver = None
                    _src = para.args[0]
                    _tgt = para.args[1] if len(para.args) > 1 else None

        try:
            obj = self.s3.Object(self.bucketname, _src) if not _ver \
                else self.s3.ObjectVersion(self.bucketname, _src, _ver)
            response = obj.get()
            if _tgt:
                with open(_tgt, 'wb') as outhdl:
                    outhdl.write(response['Body'].read())
            else:
                print(response['Body'].read().decode())
        except Exception as e:
            _print('error: get failed...\nhint: {}'.format(e), file=sys.stderr)

    def do_help(self, arg):
        'List available commands with "help" or detailed help with "help cmd".'

        # This is the original code of the method; it needed to be overwritten
        # to get rid of listing undocumented commands.
        if arg:
            # XXX check arg syntax
            try:
                func = getattr(self, 'help_' + arg)
            except AttributeError:
                try:
                    doc = getattr(self, 'do_' + arg).__doc__
                    if doc:
                        self.stdout.write("%s\n" % str(doc))
                        return
                except AttributeError:
                    pass
                self.stdout.write("%s\n" % str(self.nohelp % (arg,)))
                return
            func()
        else:
            names = self.get_names()
            cmds_doc = []
            cmds_undoc = []
            help = {}
            for name in names:
                if name[:5] == 'help_':
                    help[name[5:]] = 1
            names.sort()
            # There can be duplicates if routines overridden
            prevname = ''
            for name in names:
                if name[:3] == 'do_':
                    if name == prevname:
                        continue
                    prevname = name
                    command = name[3:]
                    if command in help:
                        cmds_doc.append(command)
                        del help[command]
                    elif getattr(self, name).__doc__:
                        cmds_doc.append(command)
                    else:
                        cmds_undoc.append(command)
            self.stdout.write("%s\n" % str(self.doc_leader))
            self.print_topics(self.doc_header, cmds_doc, 15, 80)
            self.print_topics(self.misc_header, list(help.keys()), 15, 80)
            # self.print_topics(self.undoc_header, cmds_undoc, 15, 80)

    def do_ls(self, arg):
        'ls [-amv] [prefix]\n' \
        '    List the objects within the active bucket.\n' \
        '    -a print object acls,\n' \
        '    -m prints metadata pairs per object, if available,\n' \
        '    -v prints each object\'s versions, if there are some.\n' \
        '    If prefix is given, list objects starting with the prefifx, only.'
        self.logger.info('--> called "ls {}"'.format(arg))

        if not self.profile:
            print('error: you need to connect, first...', file=sys.stderr)
            return

        if not self.bucket:
            print('error: you need to attach to a bucket, first...',
                  file=sys.stderr)
            return

        try:
            para = hs3.parse.paramcheck(arg, flags='amv')
        except Exception as e:
            _print('error: parameters invalid...\nhint: {}'.format(e),
                   file=sys.stderr)
            return

        if len(para.args) > 1:
            print('error: maximal one parameter is required', file=sys.stderr)
            return
        else:
            prefix = '' if not len(para.args) else para.args[0]

        _acl = True if 'a' in para.flags else False
        _meta = True if 'm' in para.flags else False
        _versions = True if 'v' in para.flags else False

        try:
            if _versions:
                if _acl:
                    print('{:>17} {:>15} {:36} {} {}'
                          .format('last modified',
                                  'size',
                                  'version_id                   grantee',
                                  'A',
                                  'object name/metadata    ACLs' if _meta else 'object name             ACLs'))
                else:
                    print('{:>17} {:>15} {:36} {} {}'
                          .format('last modified', 'size', 'version_id', 'A',
                                  'object name/metadata' if _meta else 'object name'))
                print('-' * 17, '-' * 15, '-' * 36, '-', '-' * 28)
            else:
                if _acl:
                    print('{:>17} {:>15} {:36} {}'
                          .format('last modified', 'size', 'version_id',
                                  'object name/metadata    ACLs' if _meta else 'object name             ACLs'))
                else:
                    print('{:>17} {:>15} {:36} {}'
                          .format('last modified', 'size', 'version_id',
                                  'object name/metadata' if _meta else 'object name'))
                print('-' * 17, '-' * 15, '-' * 36, '-' * 28)

            # We have four different calls, depending on prefix and _versions
            # being asked for.
            if prefix:
                # this works for AWS, Cloudian and HCP
                # noinspection PyUnusedLocal
                query = self.bucket.objects.filter if not _versions else self.bucket.object_versions.filter
            else:
                # and this is required for ECS...
                # noinspection PyUnusedLocal
                query = self.bucket.objects.all if not _versions else self.bucket.object_versions.all

            for obj in eval('query({})'.format(('Prefix="' + prefix + '"')
                                               if prefix else '')):
                if not _versions:
                    obj = obj.Object()
                    obj.load()
                    # if not obj.last_modified:
                    #     setattr(obj, 'last_modified', time.localtime(0))
                    print('{:>17} {:>15,} {:36} {}'
                          .format('?' if (
                    obj.last_modified == None) else obj.last_modified.strftime(
                        '%y/%m/%d-%H:%M:%S'),
                                  obj.size or 0 if _versions else obj.content_length or 0,
                                  _(obj.version_id,
                                    36) or 'null',
                                  obj.key))
                else:
                    # if not obj.last_modified:
                    #     setattr(obj, 'last_modified', time.localtime(0))
                    print('{:>17} {:>15,} {:36} {} {}'
                          .format('?' if (
                    obj.last_modified == None) else obj.last_modified.strftime(
                        '%y/%m/%d-%H:%M:%S'),
                                  obj.size or 0 if _versions else obj.content_length or 0,
                                  _(obj.version_id,
                                    36),
                                  ' ' if not _versions
                                  else 'X' if obj.is_latest else ' ',
                                  obj.key))
                if _acl:
                    if _versions:
                        acl = obj.Object().Acl()
                    else:
                        acl = obj.Acl()
                    acl.load()
                    for g in acl.grants:
                        if g['Grantee']['Type'] == 'CanonicalUser':
                            print(' ' * 17, '{:15} {:>36} {}{:>28}'
                                  .format('',
                                          g['Grantee'][
                                              'DisplayName'] if 'DisplayName' in
                                                                g[
                                                                    'Grantee'].keys() else
                                          _(g['Grantee']['ID'], 36),
                                          '  ' if _versions else '',
                                          g['Permission']))
                        elif g['Grantee']['Type'] == 'Group':
                            print(' ' * 17, '{:15} {:>36} {}{:28}'
                                  .format('',
                                          g['Grantee']['URI'].split('/')[-1],
                                          '  ' if _versions else '',
                                          g['Permission']))
                        else:
                            print(' ' * 17, 'unknown')
                try:
                    if _meta:
                        if _versions:
                            resp = obj.head()
                            if resp['Metadata']:
                                print('{:>72} {}'.format('', resp['Metadata']))
                        else:
                            if obj.metadata:
                                print('{:>70} {}'.format('', obj.metadata))
                except Exception as f:
                    print(f, file=sys.stderr)
                    pass

        except Exception as e:
            import traceback
            traceback.print_exc()
            _print('error: ls failed\nhint: {}'.format(e), file=sys.stderr)

    def do_lsb(self, arg):
        'lsb [-a]\n' \
        '    List the buckets available through the connected endpoint.\n' \
        '    -a shows ACLs as well.'
        self.logger.info('--> called "lsb {}"'.format(arg))

        if not self.profile:
            print('error: you need to connect, first...', file=sys.stderr)
            return

        try:
            para = hs3.parse.paramcheck(arg, flags='a')
        except Exception as e:
            _print('error: parameters invalid...\nhint: {}'.format(e),
                   file=sys.stderr)
            return

        _acls = True if 'a' in para.flags else False

        # test to get access to the region in AWS
        if self.mode == 'aws':
            try:
                cl = botocore.session.Session().create_client('s3',
                                                              aws_access_key_id=
                                                              self.profiles[
                                                                  self.profile][
                                                                  'aws_access_key_id'],
                                                              aws_secret_access_key=
                                                              self.profiles[
                                                                  self.profile][
                                                                  'aws_secret_access_key'],
                                                              region_name=
                                                              self.profiles[
                                                                  self.profile][
                                                                  'region'])
            except Exception as e:
                _print('error: lsb failed...\nhint: {}'.format(e),
                       file=sys.stderr)
                return

        print('{:>17} {:30} {:14} {} {:38}'
              .format('created',
                      'owner|ID' + (' ' * 15 + 'grantee' if _acls else ''),
                      'region', 'V',
                      'bucket name' + (' ' * 25 + 'ACLs' if _acls else ''),
                      ))
        print('-' * 17, '-' * 30, '-' * 14, '-', '-' * 38)

        try:
            for b in self.s3.buckets.all():
                # noinspection PyUnboundLocalVariable
                location = 'compatible' if self.mode != 'aws' else \
                    cl.get_bucket_location(Bucket=b.name)['LocationConstraint']

                # get versioning status
                # noinspection PyBroadException
                try:
                    bv = b.Versioning()
                    version_state = 'X' if bv.status == 'Enabled' else ' '
                except Exception:
                    version_state = '?'

                try:
                    acl = b.Acl()
                    acl.load()
                    # noinspection PyBroadException
                    try:
                        owner = acl.owner['DisplayName']
                    except Exception:
                        owner = acl.owner['ID']
                    print('{:17} {:30} {:14} {} {:38}'
                          .format(b.creation_date.strftime('%y/%m/%d-%H:%M:%S'),
                                  _(owner, 30), location,
                                  version_state, b.name))
                except botocore.exceptions.ClientError:
                    acl = None
                    if self.mode == 'aws':
                        print('{:17} {:30} {:14} {} {:38}'
                              .format(
                            b.creation_date.strftime('%y/%m/%d-%H:%M:%S'),
                            '**not avail. through region**', location,
                            version_state, b.name))
                    else:
                        print('{:17} {:30} {:14} {} {:38}'
                              .format(
                            b.creation_date.strftime('%y/%m/%d-%H:%M:%S'),
                            '**GetBucketAcl not impl.**', location,
                            version_state, b.name))

                if _acls and acl:
                    for g in acl.grants:
                        if g['Grantee']['Type'] == 'CanonicalUser':
                            print(' ' * 17, '{:>30} {:14} {:>40}'
                                  .format(
                                g['Grantee']['DisplayName'] if 'DisplayName' in
                                                               g[
                                                                   'Grantee'].keys() else
                                _(g['Grantee']['ID'], 30),
                                '', g['Permission']))
                        elif g['Grantee']['Type'] == 'Group':
                            print(' ' * 17, '{:>30} {:14} {:>40}'
                                  .format(g['Grantee']['URI'].split('/')[-1],
                                          '', g['Permission']))
                        else:
                            print(' ' * 17, 'unknown')

        except Exception as e:
            _print('error: listing buckets failed...\nhint: {}'.format(e),
                   file=sys.stderr)

    def do_lsp(self, arg):
        'lsp\n' \
        '    show the loaded profiles'
        self.logger.info('--> called "lsp {}"'.format(arg))

        _print('{:1} {:26} {:>8}  {}'.format('C', 'profile', 'tag', 'value'))
        _print('{:1} {:26} {:8}- {}'.format('-', '-' * 26, '-' * 8, '-' * 39))
        for p in sorted(self.profiles.keys()):
            for tag in ['comment', 'endpoint', 'region', 'https']:
                if self.profiles[p][tag] or tag == 'https':
                    _print('{:1} {:26} {:>8}: {}'
                           .format('|' if p == self.profile else '',
                                   p if tag == 'comment' else '',
                                   tag,
                                   self.profiles[p][tag]))

    def do_put(self, arg):
        'put [-m] localfile object ["metakey:metavalue"]*\n' \
        '    Put (store) localfile as object into the attached bucket,\n' \
        '    adding metadata pairs, if specified.\n' \
        '    -m will try to do a multi-part put.'
        self.logger.info('--> called "put {}"'.format(arg))

        if not self.profile:
            print('error: you need to connect, first...', file=sys.stderr)
            return

        if not self.bucket:
            print('error: you need to attach to a bucket, first...',
                  file=sys.stderr)
            return

        try:
            para = hs3.parse.paramcheck(arg, flags='m', meta=True)
        except Exception as e:
            _print('error: parameters invalid...\nhint: {}'.format(e),
                   file=sys.stderr)
            return
        else:
            if len(para.args) != 2:
                print('error: at least 2 parameters are required...',
                      file=sys.stderr)
                return

            _src = para.args[0]
            _tgt = para.args[1]
            _metadict = para.metadict

            # try to acquire the size of the file to PUT
            fsize = 0
            try:
                fsize = os.stat(_src).st_size
            except Exception as e:
                _print('warning: can\'t stat({})...\nhint: {}'.format(_src,
                                                                      e))
            else:
                _print('sending file "{}" of size {}'.format(_src, fsize))


            if 'm' in para.flags:  # multipart upload
                try:
                    if self.mode == 'aws':
                        cl = self.session.client('s3',
                                                 aws_access_key_id=
                                                 self.profiles[self.profile][
                                                     'aws_access_key_id'],
                                                 aws_secret_access_key=
                                                 self.profiles[self.profile][
                                                     'aws_secret_access_key'],
                                                 region_name=
                                                 self.profiles[self.profile][
                                                     'region'],
                                                 config=Config(
                                                     signature_version='s3v4'))
                    else:
                        # endpoint = ('https://' if self.profiles[self.profile][
                        #     'https'] else 'http://') + \
                        #            self.profiles[self.profile]['endpoint']
                        endpoint = ('https://' if self.profiles[self.profile][
                            'https'] else 'http://') + \
                                   self.profiles[self.profile]['endpoint']
                        if self.profiles[self.profile]['port']:
                            endpoint = '{}:{}'.format(endpoint,
                                                      self.profiles[self.profile][
                                                          'port'])
                        cl = self.session.client('s3',
                                                 aws_access_key_id=
                                                 self.profiles[self.profile][
                                                     'aws_access_key_id'],
                                                 aws_secret_access_key=
                                                 self.profiles[self.profile][
                                                     'aws_secret_access_key'],
                                                 endpoint_url=endpoint,
                                                 verify=False,
                                                 config=Config(signature_version='s3'))
                        cl.meta.events.unregister('before-sign.s3',
                                                  fix_s3_host)
                except Exception as e:
                    _print('error: put -m failed...\nhint: {}'.format(e),
                           file=sys.stderr)
                    return

                try:
                    transfer = S3Transfer(cl)
                    transfer.upload_file(_src, self.bucketname, _tgt,
                                         extra_args={'Metadata': _metadict,},
                                                     # 'ContentLength': fsize},
                                         callback=ProgressPercentage(_src))
                    print(flush=True)
                except Exception as e:
                    print(flush=True)
                    _print('error: transfer failed...\nhint: {}'.format(e),
                           file=sys.stderr)
                    return
            else:  # standard upload
                try:
                    with open(_src, 'br') as inhdl:
                        obj = self.s3.Object(self.bucketname, _tgt)
                        response = obj.put(Body=inhdl.read(),
                                           Metadata=_metadict,
                                           ContentLength=fsize)
                        if 'VersionId' in response:
                            print(
                                'VersionId = {}'.format(response['VersionId']))
                except Exception as f:
                    _print('error: put failed...\nhint: {}'.format(f),
                           file=sys.stderr)

    def do_quit(self, arg):
        'Exit hs3sh gracefully.'
        self.logger.info('--> called "quit {}"'.format(arg))

        print('Ending gracefully...')
        return True

    def do_rm(self, arg):
        'rm object [version_id]\n' \
        '    Delete object (or it\'s version_id) from the attached bucket.'
        self.logger.info('--> called "rm {}"'.format(arg))

        if not self.profile:
            print('error: you need to connect, first...', file=sys.stderr)
            return

        if not arg:
            print('error: at least one parameter is required...',
                  file=sys.stderr)
            return

        if len(arg.split()) == 1:
            objct = arg
            # noinspection PyUnusedLocal
            version = None
            try:
                obj = self.s3.Object(self.bucketname, objct)
                response = obj.delete()
                print('deleted "{}", version_id {}'
                      .format(objct,
                              response[
                                  'VersionId'] if 'VersionId' in response else 'null'))
            except Exception as e:
                _print('error: delete failed...\nhint: {}'.format(e),
                       file=sys.stderr)
        else:
            try:
                objct, version = arg.split()
            except Exception as e:
                print('error: one or two parameters are required...\nhint: {}'
                      .format(e), file=sys.stderr)
            else:
                try:
                    obj = self.s3.Object(self.bucketname, objct)
                    response = obj.delete(VersionId=version)
                    print('deleted "{}", version_id {}'
                          .format(objct,
                                  response[
                                      'VersionId'] if 'VersionId' in response else 'null'))
                except Exception as e:
                    _print('error: delete failed...\nhint: {}'.format(e),
                           file=sys.stderr)

    def do_run(self, arg):
        'run <script>\n' \
        '    Run a batch of commands stored in file <script>.'
        try:
            para = hs3.parse.paramcheck(arg)
        except Exception as e:
            _print('error: parameters invalid...\nhint: {}'.format(e),
                   file=sys.stderr)
            return
        else:
            if not len(para.args):
                _print('error: at least one parameter required...',
                       file=sys.stderr)

        try:
            with open(para.args[0], 'r') as inhdl:
                for cmnd in inhdl.readlines():
                    cmnd = cmnd.strip()
                    # skip comments and empty lines
                    if cmnd and not cmnd.startswith('#'):
                        if cmnd.startswith('run'):
                            print('skipping "{}"...'.format(cmnd))
                        else:
                            self.cmdqueue.append('_exec ' + cmnd.strip())
        except Exception as e:
            _print('error: running script "{}" failed...\nhint: {}'
                   .format(para.args[0], e), file=sys.stderr)

    def do_status(self, arg):
        'status\n' \
        '    Show the session status (the connected endpoint and the\n' \
        '    attached bucket)'
        self.logger.info('--> called "status {}"'.format(arg))

        _print('{:>20} {}'.format('config item', 'value'))
        _print('-' * 20, '-' * 58)

        _print('{:>20} {}'.format('mode', self.mode or 'not set'))
        _print('{:>20} {}'.format('profile', self.profile or 'not set'))
        if self.profile:
            _print('{:>20} {}'.format('profile comment',
                                      '  ' + self.profiles[self.profile][
                                          'comment']))
            _print('{:>20} {}'.format('session mode',
                                      '  ' + 'secure (https)' if
                                      self.profiles[self.profile][
                                          'https'] else 'insecure (http)'))
            _print('{:>20} {}'.format('endpoint',
                                      '  ' + (self.profiles[self.profile][
                                                  'endpoint'] or 'Amazon S3')))
            _print('{:>20} {}'.format('region',
                                      '  ' + (self.profiles[self.profile][
                                                  'region'] or 'n/a')))
        _print('{:>20} {}'.format('attached bucket',
                                  self.bucketname or 'not set'))
        _print()

    def do_time(self, arg):
        'time <command args>\n' \
        '    measure the time <command> takes to complete'
        self.logger.info('--> called "time {}"'.format(arg))

        p = arg.split(maxsplit=1)
        command, params = p if len(p) > 1 else (arg, '')

        st = time.time()
        if command:
            try:
                result = eval('self.do_{}("{}")'.format(command, params))
            except Exception as e:
                print('error: time command failed...\n\thint: {}'.format(e),
                      file=sys.stderr)
            else:
                print('[time: {}]'.format(calctime(time.time() - st)), file=sys.stderr,
                      flush=True)
                return result
        else:
            print('error: time command failed - no command given...',
                  file=sys.stderr)

    def do_url(self, arg):
        'url [-e minutes] object\n' \
        '    Generate a pre-signed URL to access object\n' \
        '    -e set the expiration time for the URL to minutes\n' \
        '       (defaults to 60 minutes)\n' \
        '    -u generates a upload URL instead of a download URL'
        self.logger.info('--> called "url {}"'.format(arg))

        if not self.profile:
            print('error: you need to connect, first...', file=sys.stderr)
            return

        if not self.bucket:
            print('error: you need to attach to a bucket, first...',
                  file=sys.stderr)
            return

        try:
            para = hs3.parse.paramcheck(arg, flags='eu')
        except Exception as e:
            _print('error: parameters invalid...\nhint: {}'.format(e),
                   file=sys.stderr)
            return
        else:
            if 'e' in para.flags and len(para.args) != 2:
                print('error: exactly 2 parameters are required...',
                      file=sys.stderr)
                return
            elif 'e' not in para.flags and len(para.args) != 1:
                print('error: exactly 1 parameter is required...',
                      file=sys.stderr)
                return

            try:
                _expiresin = int(para.args[0]) if 'e' in para.flags else 3600
            except Exception as e:
                _print(
                    'error: expiration time is invalid...\nhint: {}'.format(e),
                    file=sys.stderr)
                return
            _key = para.args[1] if 'e' in para.flags else para.args[0]

            try:
                if self.mode == 'aws':
                    cl = self.session.client('s3',
                                             aws_access_key_id=
                                             self.profiles[self.profile][
                                                 'aws_access_key_id'],
                                             aws_secret_access_key=
                                             self.profiles[self.profile][
                                                 'aws_secret_access_key'],
                                             region_name=
                                             self.profiles[self.profile][
                                                 'region'])
                else:
                    endpoint = ('https://' if self.profiles[self.profile][
                        'https'] else 'http://') + \
                               self.profiles[self.profile]['endpoint']
                    cl = self.session.client('s3',
                                             config=Config(s3={'addressing_style': 'path'},
                                                           signature_version = 's3v4'),
                                             aws_access_key_id=
                                             self.profiles[self.profile][
                                                 'aws_access_key_id'],
                                             aws_secret_access_key=
                                             self.profiles[self.profile][
                                                 'aws_secret_access_key'],
                                             endpoint_url=endpoint)
                    # cl.meta.events.unregister('before-sign.s3', fix_s3_host)
            except Exception as e:
                _print('error: generation of pre-signed URL failed...\nhint: {}'
                       .format(e), file=sys.stderr)
                return
            try:
                url = cl.generate_presigned_url('get_object' if not 'u' in para.flags else 'put_object',
                                                Params={
                                                    'Bucket': self.bucketname,
                                                    'Key': _key},
                                                ExpiresIn=_expiresin * 60,
                                                HttpMethod=None)

                print(url)
            except Exception as e:
                _print('error: generation of pre-signed URL failed...\nhint: {}'
                       .format(e), file=sys.stderr)
                return


class ProgressPercentage(object):
    """
    Show file upload process - taken from
    https://boto3.readthedocs.org/en/latest/reference/customizations/s3.html
    """
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = Lock()

    def __call__(self, bytes_amount):
        # To simplify we'll assume this is hooked up
        # to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            print('\r{}  {:,} / {:,.0f}  ({:.2f}%)'.format(self._filename,
                                                           self._seen_so_far,
                                                           self._size,
                                                           percentage),
                  end='', flush=True)


def setdefaultattrs(obj, attrs):
    '''
     Sets the attributes in attr if they are not contained in obj.

    :param obj:     the object to check
    :param attrs:   a dict containing attributes to check as key and a default
                    value as value.
    :return:        a copy of the object containing the default values for
                    missing attributes
    '''

    for key in attrs.keys():
        if hasattr(obj, key):
            print('obj {} has {} ({})'.format(obj, key, getattr(obj, key)))
        else:
            print('obj {} doesn\'t have {} (default={})'.format(obj, key, attrs[key]))
            setattr(obj, key, attrs[key])
