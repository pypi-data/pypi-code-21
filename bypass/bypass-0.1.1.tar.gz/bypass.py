#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# bypass: Copyright (C) 2017, Richard Berry

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments
# pylint: disable=invalid-name

import csv
import json
import os
import random
import re
import shutil
import string
from subprocess import run
from subprocess import Popen
from subprocess import PIPE
from subprocess import DEVNULL
import sys
from types import SimpleNamespace

import click
from gnupg import GPG
from pbr.version import VersionInfo
from ruamel import yaml

try:
    import pyotp
    import qrcode
    TOTP_ENABLED = True
except ImportError:
    TOTP_ENABLED = False

WIN = True if re.match(r'^win32|^cygwin', sys.platform) else False
MAC = True if re.match(r'^darwin', sys.platform) else False
NIX = True if not (WIN and MAC) else False

if WIN:
    import win32clipboard


__version__ = VersionInfo('bypass').semantic_version().release_string()
if WIN:
    BYPASS_CONFIG_HOME = os.path.expanduser('~/Documents/bypass')
else:
    BYPASS_CONFIG_HOME = os.path.expanduser('~/.config/bypass')
BYPASS_CONFIG = os.path.join(BYPASS_CONFIG_HOME, 'config.yaml')
BYPASS_FILE_EXTENSION = '.yaml.asc'

if os.path.isfile(BYPASS_CONFIG):
    with open(BYPASS_CONFIG, 'rb') as cfg:
        CONTEXT_SETTINGS = {'default_map': yaml.safe_load(cfg)}
else:
    CONTEXT_SETTINGS = {'default_map': {}}


def init_gpg():
    """ Instantiate the GnuPG-v2.x binding object.
    """
    gpg2binary = 'gpg2'
    gpgbinary = 'gpg'

    if check_cmd(gpg2binary, raise_error=False):
        binary = gpg2binary
    else:
        proc = run([gpgbinary, '--version'], stdout=PIPE)
        if check_gpg2_from_version(proc.stdout):
            binary = gpgbinary
        else:
            msg = "Cannot find a version of GPG greater than 2.0."
            raise click.ClickException(msg)

    return GPG(gpgbinary=binary)


def check_cmd(binary, raise_error=True):
    """ Aborts the CLI if the system can't find a given binary.
    """
    if WIN:
        cmd = f'WHERE {binary}'
    else:
        cmd = f'command -v {binary}'
    proc = run(cmd.split(' '), stdout=DEVNULL, stderr=DEVNULL)
    if proc.returncode == 0:
        return True
    elif raise_error:
        raise click.ClickException(f"The system can't find '{binary}'.")


def check_gpg2_from_version(gpg_version_output):
    """ Parses output from 'gpg --version' to verify GPG version 2.x.
    """
    if re.match(r'gpg \(GnuPG\) 2.[0-9].[0-9]',
                gpg_version_output.decode('utf-8')):
        return True


def gen_pass(length=None,
             lowercase=True,
             uppercase=True,
             digits=True,
             additional=None):
    """ Generate a password using /dev/urandom.
    """
    length = int(length) if length is not None else 20
    lowercase = string.ascii_lowercase if lowercase else ''
    uppercase = string.ascii_uppercase if uppercase else ''
    digits = string.digits if digits else ''
    additional = str(additional) if additional is not None else ''

    return ''.join(
        random.SystemRandom().choice(lowercase +\
                                     uppercase +\
                                     digits +\
                                     additional) for _ in range(length)
    )


def find_key(fingerprint, gpgobj=None):
    """ Find a key from a fingerprint short.
    """
    if gpgobj is None:
        gpgobj = init_gpg()

    keys = gpgobj.list_keys().key_map
    for fp, key in keys.items():
        if fp[-8: ] == fingerprint:
            return key


def get_pstore():
    """ Checks whether a password store has been initiated.
    """
    content = os.listdir(BYPASS_CONFIG_HOME)
    for item in content:
        if re.match('^p[A-Z0-9]{8}$', item):
            return item


def check_init(click_context):
    """ Exit the CLI if the password store has not been initiated.
    """
    if click_context.obj.path is None:
        raise click.ClickException("bypass has not been initialized.")


def decrypt_file(filepath, gpgobj=None):
    """ Decrypt an ASCII-armored GPG file.
    """
    if gpgobj is None:
        gpgobj = init_gpg()

    with open(filepath, 'rb') as encryptedfile:
        raw_content = encryptedfile.read()

    decrypt = gpgobj.decrypt(raw_content)
    if decrypt.status == 'decryption ok':
        return decrypt.data
    else:
        raise click.ClickException("Decryption failed.")


def encrypt(raw_string, key, gpgobj=None):
    """ Encrypt a string.
    """
    if gpgobj is None:
        gpgobj = init_gpg()

    encrypt = gpgobj.encrypt(raw_string, key['uids'])
    if encrypt.status == 'encryption ok':
        return encrypt.data
    else:
        raise click.ClickException("Encryption failed.")


class Credential(object):
    """ The core credential file class.

    This class handles creation and updating of ASC credential files.
    The only required argument during instantiation is the desired
    filepath of the credential file. If this file exists, it is
    decrypted and its raw YAML data is parsed and used to set attributes
    for the instance. If any of the option keyword arguments are passed
    during instantiation, these take precedence over read properties.
    No attributes are saved to the file until Credential.write is called.

    Examples
    --------

    1. Create a new credential file for GitHub with a username and
       password. Assuming you are using a GPG key with ID ABCD1234,
       then pstore = 'pABCD1234'.
        >>> cred_filepath = os.path.join(BYPASS_CONFIG_HOME, pstore,
        ...                              gh.yaml.asc)
        >>> github = Credential(cred_filepath,
        ...                     username="handle@email.com",
        ...                     password="P@s5w0rd!==ins3cure")
        >>> github.write()

       Add a URL to the instantiated GitHub credential object.
        >>> github.url = 'https://github.com'
        >>> github.write()

       This entry is now available via the commandline.
        $ bp view gh
        gh: {
            "username": "handle@email.com",
            "password": "P@s5w0rd!==ins3cure",
            "url": "https://github.com"
        }
    """

    properties = ['username', 'password', 'url', 'totp']

    def __init__(self,
                 credfilepath,
                 key=None,
                 gpg=None,
                 username=None,
                 password=None,
                 url=None,
                 totp=None):
        self._loc = credfilepath
        self._key = key

        if gpg is None:
            self._gpg = init_gpg()
        else:
            self._gpg = gpg

        if os.path.isfile(self._loc):
            self._dict = yaml.safe_load(decrypt_file(credfilepath, self._gpg))
        else:
            self._dict = {}

        self._username = username
        self._password = password
        self._url = url
        self._totp = totp

        for prop in self.properties:
            # First, potentially override entries in the credential dictionary
            val = getattr(self, '_' + prop)
            if val is not None:
                self._dict[prop] = val
            # Finally, update instance attributes with up-to-date credentials
            try:
                setattr(self, '_' + prop, self._dict[prop])
            except KeyError:
                pass

    def write(self):
        """ Write updates to an encrypted credential file.
        """
        if not os.path.isfile(self._loc):
            dirname = os.path.dirname(self._loc)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)

        credfile_content = yaml.round_trip_dump(self._dict)
        encrypted_credfile_content = encrypt(credfile_content,
                                             self._key,
                                             self._gpg)

        with open(self._loc, 'wb') as encryptedfile:
            encryptedfile.write(encrypted_credfile_content)

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, val):
        self._dict['username'] = str(val)
        self._username = str(val)

    @username.deleter
    def username(self):
        del self._dict['username']
        self._username = None

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, val):
        self._dict['password'] = str(val)
        self._password = str(val)

    @password.deleter
    def password(self):
        del self._dict['password']
        self._password = None

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, val):
        self._dict['url'] = str(val)
        self._url = str(val)

    @url.deleter
    def url(self):
        del self._dict['url']
        self._url = None

    @property
    def totp(self):
        if TOTP_ENABLED:
            return self._totp
        else:
            msg = "TOTP support for bypass is not enabled on your system."
            raise click.ClickException(msg)

    @totp.setter
    def totp(self, val):
        self._dict['totp'] = val
        self._totp = val

    @totp.deleter
    def totp(self):
        del self._dict['totp']
        self._totp = None

    def __str__(self):
        output = json.dumps(self._dict, indent=4).split('\n')
        for index, line in enumerate(output):
            match = re.match(r'^[ ]{4}\"(.*)\": \"(.*)\"([,]?)$', line)
            if match:
                lvalue = match.groups()[0]
                rvalue = match.groups()[1]
                comma = match.groups()[2]
                output[index] = f'    \033[1m{lvalue}\033[0m: {rvalue}{comma}'

        return '\n'.join(output)


def get_credential(pstore, entry, gpg=None):
    """ Instantiate Credential for a given entry.
    """
    credfilepath = os.path.join(pstore, entry + BYPASS_FILE_EXTENSION)

    # First, deal with a longform entry
    if os.path.isfile(credfilepath):
        return Credential(credfilepath, gpg=gpg)

    # Now assume the entry is shortform
    for f in sorted(get_files(pstore)):
        if not f.endswith(BYPASS_FILE_EXTENSION):
            continue
        if os.path.basename(f) == entry + BYPASS_FILE_EXTENSION:
            return Credential(f, gpg=gpg)

    raise click.BadParameter(f"Cannot find '{entry}'.")


def get_files(path):
    """ Build a list of *all* files under a path.
    """
    files = []
    for subpath, _, filenames in os.walk(path):
        for filename in filenames:
            files.append(os.path.join(subpath, filename))

    return files


def make_totp_dictionary(totp_tuple):
    """ Build a dictionary from a TOTP tuple (passed with click).
    """
    if totp_tuple:
        totp_keys = ['secret', 'username', 'title']
        totp_d = {}
        for t in totp_tuple:
            if t[0] not in totp_keys:
                raise click.BadOptionUsage(f"Unknown key '{t[0]}' for TOTP.")
            else:
                totp_d[t[0]] = t[1]
        if 'secret' not in totp_d:
            raise click.BadOptionUsage("TOTP requires a secret.")

        return totp_d


def tree(path):
    """ Run the tree command on the given directory.
    """
    check_cmd('tree')
    tree_cmd = f'tree -C {path}'.split(' ')
    proc = run(tree_cmd, stdout=PIPE)
    if proc.returncode == 0:
        return proc.stdout
    else:
        raise click.ClickException


def format_tree_output(raw_output, path, root=True):
    """ Format the raw output from the 'tree' function.
    """
    output = raw_output.decode('utf-8')
    key_id = os.path.basename(path)[1: ]

    if root:
        # Sub the bypass password store path
        output = re.sub(path, f'bypass: {key_id}', output)
    else:
        # Sub the realpath for its basename
        output = re.sub(path, os.path.basename(path), output)

    # Clear tail-end of tree output
    output = re.sub(r'\n[0-9]+ director(y|ies), [0-9]+ file[s]?\n', '', output)
    # Remove the store entry extensions
    output = re.sub(BYPASS_FILE_EXTENSION, '', output)

    return output


def update_credential(ctx, username, password, url, totp, force, entry):
    """ Writes parameters to a credential file.
    """
    # Arrange TOTP dictionary
    totp_d = make_totp_dictionary(totp)

    # Setup the credential object
    credfilepath = os.path.join(ctx.obj.path, entry + BYPASS_FILE_EXTENSION)
    if not force:
        if os.path.isfile(credfilepath):
            msg = f"An entry for '{entry}' already exists."
            raise click.BadArgumentUsage(msg)
    cred = Credential(credfilepath,
                      gpg=ctx.obj.gpg,
                      key=ctx.obj.key,
                      username=username,
                      password=password,
                      url=url,
                      totp=totp_d)
    cred.write()


# -- click CLI

@click.group(context_settings=CONTEXT_SETTINGS,
             no_args_is_help=True,
             invoke_without_command=True)
@click.pass_context
@click.option('--version', '-V', is_flag=True, help="Print bypass version.")
def bypass(ctx, version):
    """ bypass: CLI password management with GPG-based encryption.
    """
    if version:
        click.echo(__version__)
        ctx.exit(0)

    gpg = init_gpg()
    _pstore = get_pstore()
    if _pstore:
        path = os.path.join(BYPASS_CONFIG_HOME, _pstore)
        key = find_key(_pstore[1: ])
    else:
        path = None
        key = None

    ctx.obj = SimpleNamespace(gpg=gpg, path=path, key=key)


@bypass.command()
@click.pass_context
@click.option('--field', '-f',
              type=click.Choice(['username', 'password', 'url', 'totp']),
              default='password',
              help="The credential field to copy.")
@click.option('--selection', '-s',
              type=click.Choice(['primary', 'secondary', 'clipboard']),
              default='clipboard',
              help="The desired X selection.")
@click.option('--timeout', '-t',
              type=click.INT, default=10,
              help="Clipboard clear time in seconds.")
@click.argument('entry', type=click.STRING)
def copy(ctx, field, selection, timeout, entry):
    """ Copy a credential field to the clipboard.
    """
    check_init(ctx)

    if NIX:
        check_cmd('xclip')  # Will exit if xclip can't be found
    cred = get_credential(ctx.obj.path, entry, ctx.obj.gpg)
    field_content = getattr(cred, field)
    if field_content is None:
        raise click.UsageError(f"'{entry}' does not have data for '{field}'.")
    if field == 'totp':
        field_content = TOTP(field_content['secret']).now()

    # Copy the field to the clipboard
    if WIN:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(field_content.encode('utf-8'))
        win32clipboard.CloseClipboard()
    else:
        if MAC:
            copy_cmd = 'pbcopy'
        else:
            copy_cmd = f'xclip -selection {selection}'.split(' ')
        run(copy_cmd, input=field_content.encode('utf-8'))

    # Print a confirmation that the clipboard copy worked
    msg1 = \
        (f"Copied \033[1m{field}\033[0m for "
         f"\033[1m{entry}\033[0m to the clipboard. ")
    msg2 = \
        f"Clearing in \033[1m{timeout}\033[0m seconds." if timeout != (-1) else ''
    click.echo(msg1 + msg2)

    # Prep the clipboard clear
    if timeout != -1:
        if WIN:
            clear_cmd = f'TIMEOUT /NOBREAK /T {timeout} && echo off | clip'
        elif MAC:
            clear_cmd = f'sleep {timeout} && echo | pbcopy'
        else:
            clear_cmd =\
                f'sleep {timeout} && xclip -selection {selection} -i /dev/null'
        # shell=True is *required* in the following subprocess only
        Popen(clear_cmd, stdout=DEVNULL, stderr=DEVNULL, shell=True)


@bypass.command()
@click.pass_context
@click.option('--length', '-l',
              type=click.INT,
              help="Length of password to generate.")
@click.option('--additional', '-a',
              type=click.STRING,
              help="Additional characters to use for generation.")
@click.option('--no-lowercase',
              is_flag=True,
              help="Do not use lowercase A-Z in generation.")
@click.option('--no-uppercase',
              is_flag=True,
              help="Do not use uppercase A-Z in generation.")
@click.option('--no-digits',
              is_flag=True,
              help="Do not use digits 0-9 in generation.")
@click.option('--add-user', '-u', 'username',
              type=click.STRING,
              help="Add a username to the credential entry.")
@click.option('--add-url', '-U', 'url',
              type=click.STRING,
              help="Add a URL to the credential entry.")
@click.option('--add-totp', '-t', 'totp',
              nargs=2, multiple=True, type=click.STRING,
              help="Add TOTP data to the credential entry.")
@click.option('--force', '-f',
              is_flag=True,
              help="Bypass any warnings.")
@click.argument('entry', type=click.STRING)
def gen(ctx,
        length,
        additional,
        no_lowercase,
        no_uppercase,
        no_digits,
        username,
        url,
        totp,
        force,
        entry):
    """ Generate a password and create an entry.
    """
    check_init(ctx)

    # Negate CLI flags
    lowercase = not no_lowercase
    uppercase = not no_uppercase
    digits = not no_digits

    # Gen password
    password = gen_pass(length=length,
                        lowercase=lowercase,
                        uppercase=uppercase,
                        digits=digits,
                        additional=additional)

    update_credential(ctx, username, password, url, totp, force, entry)


@bypass.command()
@click.pass_context
@click.argument('entry', type=click.STRING)
def goto(ctx, entry):
    """ Launch a URL in the browser.
    """
    check_init(ctx)

    cred = get_credential(ctx.obj.path, entry, ctx.obj.gpg)
    if cred.url is None:
        raise click.BadArgumentUsage(f"'{entry}' has no URL.")
    if not (cred.url.startswith('http') or cred.url.startswith('www')):
        raise click.BadArgumentUsage(f"The URL for '{entry}' is invalid.")

    if WIN:
        cmd = f'explorer {cred.url}'.split(' ')
    elif MAC:
        cmd = f'open {cred.url}'.split(' ')
    else:
        cmd = f'xdg-open {cred.url}'.split(' ')

    run(cmd, stdout=DEVNULL, stderr=DEVNULL)


@bypass.command()
@click.pass_context
@click.argument('key', type=click.STRING)
def init(ctx, key):
    """ Setup the password vault.
    """
    if ctx.obj.path:
        raise click.ClickException("A password store already exists.")

    if find_key(key) is None:
        raise click.BadParameter(f'"{key}" is not a valid gpg key.')

    pstore = os.path.join(BYPASS_CONFIG_HOME, 'p' + key)
    os.makedirs(pstore)
    os.chmod(pstore, 0o700)


@bypass.command()
def lock():
    """ Remove the GPG passphrase from the cache.
    """
    check_init(ctx)

    # FIXME: forget password only for the key required for the bypass store
    cmd = 'gpgconf --reload gpg-agent'.split(' ')
    run(cmd)


@click.group()
@click.pass_context
def migrate(ctx):
    """ Migrate to bypass from other password managers.
    """
    check_init(ctx)


@migrate.command()
@click.pass_context
@click.argument('csvfile', type=click.File('r'))
def keepass(ctx, csvfile):
    reader = csv.DictReader(csvfile)
    for row in reader:
        entry = row['Group'] + '/' + row['Title']
        username = row['Username']
        password = row['Password']
        url = row['URL']

        update_credential(ctx, username, password, url, None, False, entry)


bypass.add_command(migrate)


@bypass.command()
@click.pass_context
@click.argument('entry', type=click.STRING)
def qr(ctx, entry):
    """ Generate a scannable QR code from TOTP data.
    """
    check_init(ctx)

    cred = get_credential(ctx.obj.path, entry, ctx.obj.gpg)
    if cred.totp is None:
        raise click.BadArgumentUsage(f"'{entry}' has no TOTP data.")

    title = os.path.basename(entry)
    qrcode.make(pyotp.TOTP(cred.totp['secret']).provisioning_uri(title)).show()


@bypass.command()
@click.pass_context
@click.option('--recursive', '-r',
              is_flag=True,
              help="Recursively remove groups and entries.")
@click.argument('entry', type=click.STRING)
def rm(ctx, recursive, entry):
    """ Remove a credential from the password store.
    """
    check_init(ctx)

    pstore_entry = os.path.join(ctx.obj.path, entry)

    if os.path.isdir(pstore_entry):
        if not recursive:
            raise click.BadOptionUsage(f"'{entry} is a credential group.")
        shutil.rmtree(pstore_entry)
        click.echo(f"Permanently removed credential group '{entry}'.")

    elif os.path.isfile(pstore_entry + BYPASS_FILE_EXTENSION):
        os.remove(pstore_entry + BYPASS_FILE_EXTENSION)
        click.echo(f"Permanently removed credential '{entry}'.")

    else:
        raise click.BadArgumentUsage(f"Cannot find '{entry}'.")


@bypass.command()
@click.pass_context
@click.option('--username', '-u', 'username',
              type=click.STRING,
              help="Add a username to the credential entry.")
@click.option('--password', '-p',
              type=click.STRING,
              help="Add a password to the credential entry.")
@click.option('--url', '-U', 'url',
              type=click.STRING,
              help="Add a URL to the credential entry.")
@click.option('--totp', '-t', 'totp',
              nargs=2, multiple=True, type=click.STRING,
              help="Add TOTP data to the credential entry.")
@click.option('--force', '-f',
              is_flag=True,
              help="Bypass any warnings.")
@click.argument('entry', type=click.STRING)
def update(ctx,
           username,
           password,
           url,
           totp,
           force,
           entry):
    """ Manually update an entry.
    """
    check_init(ctx)

    update_credential(ctx, username, password, url, totp, force, entry)


@bypass.command()
@click.pass_context
@click.argument('entry', type=click.STRING, required=False)
def view(ctx, entry):
    """ View the contents of the password store.
    """
    check_init(ctx)

    if entry is None:
        raw_tree_output = tree(ctx.obj.path)
        tree_output = format_tree_output(raw_tree_output, ctx.obj.path)
        click.echo(tree_output)

    else:
        pstore_entry = os.path.join(ctx.obj.path, entry)

        if os.path.isdir(pstore_entry):
            raw_tree_output = tree(pstore_entry)
            tree_output = format_tree_output(raw_tree_output,
                                             pstore_entry,
                                             root=False)
            click.echo(tree_output)

        else:
            cred = get_credential(ctx.obj.path, entry, ctx.obj.gpg)
            click.echo('\033[1;34m' + entry + '\033[0m' + ': ' + str(cred))
