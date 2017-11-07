# Copyright 2017 Nokia
# Copyright 2016 Pierre-Yves David <pierre-yves.david@ens-lyon.org>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
"""monitor and enforce client configuration from a server (EXPERIMENTAL)

This extension allows a server to recommend or enforce some configuration values
to a client during push and pull operation. The server can also detect clients
not using the extension and take appropriate actions.


Basic Setup
===========

This extension will not work with old clients using bundle1 (older than hg-3.5), we recommend
blocking old clients from your server using this config::

  [server]
  bundle1 = False


By default, the server will issue a warning to clients pushing and pulling without
the extension. This behavior can be controlled with the following option::

  [configexpress]
  # Behavior for clients with the extension. Possible values:
  # * ignore:  do not do anything
  # * warning: print a warning to the client (default)
  # * abort:   refuse to interract with the client
  enforce=ignore


Server to Client
================

The server can recommend configuration to the client during ``pull`` and ``clone``.
Recommended config values are put into a dedicated file referenced in the
``configexpress:server2client`` section::

  [configexpress:server2client]
  # path is relative to the config file it is defined in.
  config-key=path/to/config/file.rc

When values specified in the file differ from the user configuration, a prompt
will offer to update that configuration::

  server suggests the following config changes:
    [section_a]
    entry-one=Babar
    entry-two=Celeste
    [section_b]
    other.entry=Other/Text
    some.entry=some text
  apply these changes to your repository config file (yn)

If the new config shadows some of the existing user config, the user will be
informed with the following message::

  this will overwrite these current user configurations:
    [section_a]
    entry2=barbar

Multiple entries can be specified, they will be evaluated independently and the
user will be able to accept or reject them independently.


Client to Server
================

Enabling this extension results in sending the Mercurial version to the server.
Additional information about local configuration can be sent using the
``configexpress:client2server`` section.

Example::

  [configexpress:client2server]
  somelist = ui.verbose ui.username diff.git
  otherlist = extensions.rebase extensions.histedit
  [configexpress]
  share-repo-format = yes # also share repository format data
  share-extensions = yes # also share details on enabled extensions

On the server side, the value sent by the client will be available to
transaction hooks through environment variables. environment variable are in
the form: ``CLIENTCONFIG_<SECTION>__<NAME>``. The Mercurial version used by the
client is available through: ``CLIENTCONFIG_hgversion``.
If the repository format data are shared they will be available in the form:
``CLIENTFORMAT_<NAME>__REPO``. The current user configuration for that format
is also available in ``__CONFIG`` and the current default of the Mercurial
version used on the client in ``__DEFAULT``.
If the extensions details are shared, they will be available in the form:
``CLIENTEXTENSION_<NAME>``. The value of such variable will be the version of
the extension. Extensions without version declaration will use 'unknown' as
version value. Extensions shipped with Mercurial will use 'hg-<version>' as
their version string.

(This only applies for push.)

Config
======

Detailed config help

``configexpress``
-----------------

Control generic behavior of the extension.

``enforce``
    level of enforcement to clients without the extension. Possible values:
    * ignore:  do not do anything
    * warning: print a warning to the client (default)
    * abort:   refuse to interact with the client

``enforcewarningmsg`
  custom warning message (optional). used when ``enforce=warning``

``enforceabortmsg`
  custom abort message (optional). used when ``enforce=abort``

``share-repo-format``
  Boolean, control if the client send information about the repository on-disk
  format to the server. (default: False)

``configexpress:server2client``
-------------------------------

``some-name``
    Configurations to be offered to the user. Value is a path to a config file.
    If the path is relative, it is interpreted relative to the file that
    defines it.

    Each individual entry will result in an independant check and prompt to the
    user.

``some-name:type``
    Control the type of the proposed config: by default, a regular config file
    is assumed.

    Alternatives are possible by specifying an explicit type, currently:
    * includes: check if a specific include path is present, otherwise warn.
      The configuration file should be a line-separated list of include paths.

``some-name:selection``
    Control what part of the proposed config is required: by default all
    configuration elements are required.
    This setting currently only has impact if the config type is 'includes'.

    Possible values:
    * any: require at least one of the specified includes to be in the user config
    * all: require all specified includes to be used (default)

``some-name:ignore``
    Ignore a specific configuration suggestion from the server.
    (client side configuration)

``configexpress:client2server``
-------------------------------

Control what local config value are sent to the server on pull/push. Entries
have an arbitrary name, values is a list of config option to be send::

Example::

  [configexpress:client2server]
  somelist = ui.verbose ui.username diff.git
  otherlist = extensions.rebase extensions.histedit
"""
from __future__ import absolute_import
import cStringIO as io
import os
import tempfile

from mercurial.i18n import _
from mercurial import (
    bundle2,
    config,
    error,
    exchange,
    extensions,
    scmutil,
    ui as uimod,
    util
)

try:
    from mercurial import upgrade
    upgrade.allformatvariant
except ImportError:
    # hg-4.2
    upgrade = None

__version__ = '0.3.0'
testedwith = '3.7.3 4.0.1 4.1.2 4.2.3 4.3.3 4.4'
minimumhgversion = '3.7.3'
buglink = 'https://bitbucket.org/Mathiasdm/hg-configexpress/issues'

CLIENT2SERVER_SECTION = 'configexpress:client2server'
SERVER2CLIENT_SECTION = 'configexpress:server2client'

try:
    from mercurial import registrar

    configtable = {}
    configitem = registrar.configitem(configtable)
    dynamicdefault = configitem.dynamicdefault # raise Attribute Error < 4.4
except (ImportError, AttributeError):
    pass # compat < hg-4.4
else:
    configitem('configexpress', 'enforce',
        # actual default is 'warning', use it when compat < hg-4.3 is dropped
        default=dynamicdefault,
    )
    configitem('configexpress', 'enforceabortmsg',
        # actual default is '_enforcemsgabort', use it when compat < hg-4.3 is dropped
        default=dynamicdefault,
    )
    configitem('configexpress', 'enforcewarningmsg',
        # actual default is '_enforcemsgwarn', use it when compat < hg-4.3 is dropped
        default=dynamicdefault,
    )
    configitem('configexpress', 'share-repo-format',
        default=False,
    )
    configitem('configexpress', 'share-extensions',
        default=False,
    )
    configitem(CLIENT2SERVER_SECTION, '.*',
        default=None,
        generic=True,
    )
    configitem(SERVER2CLIENT_SECTION, '.*',
        default=None,
        generic=True,
        priority=1,
    )
    configitem(SERVER2CLIENT_SECTION, '.*:type',
        default=None,
        generic=True,
        priority=0,
    )
    configitem(SERVER2CLIENT_SECTION, '.*:selection',
        default='all',
        generic=True,
        priority=0,
    )

def getconfigstr(configitems, ui=None):
    '''Given a set of configuration entries of the form (section, item, value),
       a string in the hgrc format is generated.
       Giving the 'ui' argument makes sure values are taken from that argument,
       ignoring the 'value' entries in configitems.'''
    data = []
    configitems.sort()
    previoussection = None
    for (section, item, value) in configitems:
        if ui and not ui.hasconfig(section, item):
            continue
        if not previoussection or section != previoussection:
            data.append("[%s]" % section)
        previoussection = section
        if ui:
            value = ui.config(section, item)
        if value is None:
            value = ""
        data.append("%s=%s" % (item, value))
    if not data:
        return ''
    data.append('') # final \n
    return '\n'.join(data)

def calculateconfigdiff(first, second, onlyfirst=True):
    '''Calculate differences in configuration between 2 configurations.

       onlyfirst -- only check configuration entries that occur in the first config'''
    add = [] # config items present in first, not in second
    diff1 = [] # config items in first that are different in second
    diff2 = [] # config items in second that are different in first
    remove = [] # config items present in second, not in first
    for (section, item, value) in first.walkconfig():
        if not second.hasconfig(section, item):
            add.append((section, item, value))
        elif second.config(section, item) != value:
            diff1.append((section, item, value))
    if not onlyfirst:
        for(section, item, value) in second.walkconfig():
            if not first.hasconfig(section, item):
                remove.append((section, item, value))
            elif first.config(section, item) != value:
                diff2.append((section, item, value))
    return (add, diff1, diff2, remove)

@exchange.b2partsgenerator('configexpress:clientinfo', idx=0)
def _getbundlesendisaminfo(pushop, bundler):
    '''Send an additional (optional) clientinfo bundle part to the server.
       This bundle part is optional to make sure the server doesn't error out.
    '''
    if 'clientinfo' in pushop.stepsdone:
        return
    pushop.stepsdone.add('clientinfo')

    configitems = []
    for key, _ in pushop.ui.configitems(CLIENT2SERVER_SECTION):
        for entry in pushop.ui.configlist(CLIENT2SERVER_SECTION, key):
            (section, element) = entry.split('.', 1)
            configitems.append((section, element, None))
    data = getconfigstr(configitems, pushop.ui)

    part = bundler.newpart('configexpress:clientinfo', mandatory=False, data=data)
    hgversion = str(util.version())
    part.addparam('hgversion', hgversion, mandatory=False)

    if pushop.ui.configbool('configexpress', 'share-repo-format'):
        if upgrade is None:
            pushop.ui.warn('cannot send repository format data to the server, '
                           'Mercurial version too old\n')
            pushop.ui.warn('(upgrade to Mercurial 4.2+ '
                           'or set config.express.share-repo-format=no)\n')
        else:
            data = []
            for fv in upgrade.allformatvariant:
                data.append("%s:repo=%i\n" % (fv.name, fv.fromrepo(pushop.repo)))
                data.append("%s:config=%i\n"
                            % (fv.name, fv.fromconfig(pushop.repo)))
                data.append("%s:default=%i\n" % (fv.name, fv.default))
            if data:
                part = bundler.newpart('configexpress:clientformat',
                                       mandatory=False, data=iter(data))

    if pushop.ui.configbool('configexpress', 'share-extensions'):
        data = []
        for extname in extensions.enabled():
            extmodule = extensions.find(extname)
            if extensions.ismoduleinternal(extmodule):
                extversion = 'hg-%s' % hgversion
            else:
                extversion = extensions.moduleversion(extmodule)
            if not extversion:
                extversion = 'unknown'
            data.append('%s=%s\n' % (extname, extversion))
        if data:
            part = bundler.newpart('configexpress:clientextensions',
                                   mandatory=False, data=iter(data))

@bundle2.parthandler('configexpress:clientinfo', ())
def bundle2getisaminfo(op, part):
    '''Retrieve a clientinfo part and store parameters as hook arguments'''
    tr = op.gettransaction()
    for key, value in part.advisoryparams:
        tr.hookargs["CLIENTCONFIG_%s" % key] = value
    data = part.read() #TODO: not very safe
    fp = io.StringIO(data)
    cfg = config.config()
    cfg.read(path="", fp=fp)

    for section in cfg.sections():
        for (item, value) in cfg.items(section):
            key = "CLIENTCONFIG_%s__%s" % (section, item)
            tr.hookargs[key] = value

@bundle2.parthandler('configexpress:clientformat', ())
def bundle2getformatdata(op, part):
    '''Retrieve a clientinfo part and store parameters as hook arguments'''
    tr = op.gettransaction()
    for line in  part.read().splitlines():
        key, value = line.split('=', 1)
        tr.hookargs["CLIENTFORMAT_%s" % key.replace(':', '__')] = value

@bundle2.parthandler('configexpress:clientextensions', ())
def bundle2getextensiondata(op, part):
    '''Retrieve a clientinfo part and store parameters as hook arguments'''
    tr = op.gettransaction()
    for line in  part.read().splitlines():
        key, value = line.split('=', 1)
        tr.hookargs["CLIENTEXTENSION_%s" % key] = value

@exchange.getbundle2partsgenerator('configexpress:proposedconfig')
def _getbundleproposedconfig(bundler, repo, source, **kwargs):
    '''Send an additional (optional) proposedconfig bundle to the client.'''
    if not repo.ui.has_section(SERVER2CLIENT_SECTION):
        return

    items = sorted(repo.ui.configitems(SERVER2CLIENT_SECTION, ignoresub=True))
    for (item, configfile) in items:
        if os.path.isabs(configfile):
            configpath = configfile
        else:
            source = repo.ui.configsource(SERVER2CLIENT_SECTION, item)
            sourcebase = repo.vfs.dirname(source)
            configpath = os.path.join(sourcebase, configfile)
        if not os.path.exists(configpath):
            repo.ui.warn("configexpress: proposedconfig not found: %s\n" % configpath)
            return
        (option, suboptions) = repo.ui.configsuboptions(SERVER2CLIENT_SECTION, item)

        data = util.readfile(configpath)

        part = bundler.newpart('configexpress:proposedconfig', mandatory=False, data=data)
        part.addparam('name', item, mandatory=False)
        type = suboptions.get('type')
        if type is not None:
            part.addparam('type', type)
        selection = suboptions.get('selection', 'all')
        if selection is not None:
            part.addparam('selection', selection)

_serverproposal = _("server suggests the following config changes:")
_outdatedconfig = _("this will overwrite these current user configurations:")

_hgrcdirname = 'hgrc-ext-config-express'
_hgrcdispatchname = 'hgrc-ext-config-express.rc'

_hgrccomment = ('# This "%include" enables config from the configexpress extension.'
                ' keep at end of file\n')
_hgrcinclude = '%%include ./%s\n' % _hgrcdispatchname


def _handleincludes(op, part):
    #TODO: change ui so we can just get configpaths from it directly
    global _configpaths
    _configpaths = []
    # not load for < hg-4.1
    lui = getattr(uimod.ui, 'load', uimod.ui)()
    lui.readconfig(op.repo.vfs.join('hgrc'))

    configpaths = '\n'.join(_configpaths)

    missingincludes = []
    #TODO: if we get configpaths from ui, we could choose to get absolute or relative paths.
    # the current solution looks for partial matches and is ugly...
    data = part.read()
    #Keep non-empty lines
    includes = [x for x in data.splitlines() if x]
    for include in includes:
        if not include in configpaths:
            missingincludes.append(include)

    if missingincludes:
        selection = part.params.get('selection', 'all')
        if selection == 'any':
            if len(missingincludes) == len(includes):
                op.ui.warn("you need at least one of the following includes in your configuration:\n")
                for missinginclude in missingincludes:
                    op.ui.warn("  %%include %s\n" % missinginclude)
                op.ui.warn("(add one of the above lines to your hgrc to fix your configuration)\n")
        elif selection == 'all':
            op.ui.warn("the following includes are missing in your configuration:\n")
            for missinginclude in missingincludes:
                op.ui.warn("  %%include %s\n" % missinginclude)
            op.ui.warn("(add the above lines to your hgrc to fix your configuration)\n")
        elif selection is None:
            raise error.Abort("no selection parameter was given for missing includes")
        else:
            raise error.Abort("unknown selection parameter given for missing includes: '%s'" % selection)

def _handlehgrc(op, part):
    serverdata = part.read()
    name = "%s.rc" % part.params.get('name', 'untitled-%s' % part.id)

    #TODO: just use StringIO (needs ui.readconfig support for fp)
    fd, path = tempfile.mkstemp()
    try:
        os.write(fd, serverdata)
        os.close(fd)
        serverui = uimod.ui()
        serverui.readconfig(path)
    finally:
        os.remove(path)
    # 1. Calculate the differences between client and server
    (add, diff1, diff2, remove) = calculateconfigdiff(serverui, op.ui, onlyfirst=False)
    if not add and not diff1:
        # no proposed changes to the configuration
        # XXX handle location
        op.records.add('configexpress.enabled-config',
                       {'file': name})
        return
    proposedconfig = getconfigstr(add + diff1)
    # 2. Propose applying differences to client
    op.ui.warn(_serverproposal + "\n")
    for line in proposedconfig.splitlines(True):
        op.ui.warn('  ' + line)
    if diff2:
        op.ui.warn(_outdatedconfig + "\n")
        for line in getconfigstr(diff2).splitlines(True):
            op.ui.warn('  ' + line)
    res = op.ui.promptchoice("apply these changes to your repository config file (yn)? $$ &Yes $$ &No")
    if res != 0:
        return

    # XXX move to a dedicated lock instead
    with op.repo.wlock():
        op.repo.vfs.makedirs(_hgrcdirname)
        # mercurial < hg-3.8 does not have context manager for vfs file
        path = op.repo.vfs.reljoin(_hgrcdirname, name)
        partrc = op.repo.vfs(path, 'w', atomictemp=True)
        try:
            _writeboilerplate(partrc)
            partrc.write(serverdata)
            partrc.close()
        except: # re-raises
            partrc.discard()
            raise

        op.records.add('configexpress.enabled-config', {'file': name})

def _writeboilerplate(f):
    f.write('# this file is managed by the configexpress extension\n')
    f.write('# /!\\ do not edit /!\\\n')

def _finalizeconfig(orig, *args, **kwargs):
    # XXX if not config changed, we should avoid rewriting everything
    op = orig(*args, **kwargs)
    entries = op.records['configexpress.enabled-config']
    if not entries:
        return op
    # XXX move to a dedicated lock instead
    with op.repo.wlock():
        # mercurial < hg-3.8 does not have context manager for vfs file
        sharedrc = op.repo.vfs(_hgrcdispatchname, 'w', atomictemp=True)
        try:
            _writeboilerplate(sharedrc)
            for entry in sorted(entries):
                sharedrc.write('%%include ./%s/%s\n' % (_hgrcdirname, entry['file']))
            sharedrc.close()
        except: # re-raises
            sharedrc.discard()
            raise

        commentidx = []
        includeidx = []
        rclines = op.repo.vfs.tryread('hgrc').splitlines(True)
        idx = 0
        for idx, line in enumerate(rclines):
            if line == _hgrccomment:
                commentidx.append(idx)
            elif line == _hgrcinclude:
                includeidx.append(idx)
        finalidx = idx

        if not commentidx + includeidx:
            # simple: no existing data
            with op.repo.vfs('hgrc', 'a') as mainrc:
                mainrc.write(_hgrccomment)
                mainrc.write(_hgrcinclude)
        elif commentidx != [finalidx -1] or includeidx != [finalidx]:
            # some data exist at the wrong spot, drop them
            dropped = set(commentidx + includeidx)
            with op.repo.vfs('hgrc', 'w', atomictemp=True) as mainrc:
                for idx, line in enumerate(rclines):
                    if idx not in dropped:
                        mainrc.write(line)
                mainrc.write(_hgrccomment)
                mainrc.write(_hgrcinclude)
    return op

_capability = 'ext-configexpress'
_enforcemsgwarn = _("this server recommends using the 'configexpress'"
                    " extension\n")
_enforcemsgabort = _("this server requires the 'configexpress' extension")
@bundle2.parthandler('configexpress:proposedconfig', ('type', 'selection'))
def bundle2getproposedconfig(op, part):
    '''Retrieve a proposed configuration, calculate the difference
       to our own configuration and apply the difference.'''

    name = part.params.get('name')
    option, suboptions = op.ui.configsuboptions(SERVER2CLIENT_SECTION, name)
    if 'ignore' in suboptions and util.parsebool(suboptions['ignore']):
        op.ui.debug("skipping proposed configs '%s'\n" % part.params.get('name', 'unnamed'))
        return

    type = part.params.get('type')
    if type == 'includes':
        _handleincludes(op, part)
    elif type:
        op.ui.warn("configexpress: ignoring proposed configuration: unknown type %s\n" % (type, ))
    else:
        _handlehgrc(op, part)



def checkreplycaps(orig, op, inpart):
    orig(op, inpart)
    if op.reply is not None:
        _enforceext(op.ui, op.reply)

_maxabortlength = 80

def _enforceext(ui, bundler):
    if _capability not in bundler.capabilities:
        # client does not have the extension enabled
        policy = ui.config('configexpress', 'enforce', 'warning')
        if policy == 'ignore':
            pass
        elif policy == 'warning':
            msgwarn = ui.config('configexpress', 'enforcewarningmsg', _enforcemsgwarn)
            ui.warn(msgwarn)
        elif policy == 'abort':
            msgabort = ui.config('configexpress', 'enforceabortmsg', _enforcemsgabort)
            if len(msgabort) > _maxabortlength:
                ui.warn(msgabort)
                ui.warn('\n')
                ui.warn('    - - -\n')
                msgabort = msgabort[:_maxabortlength] + "..."
            raise error.Abort(msgabort)
        else:
            msg = _("unknown value for 'configexpress.enforce': %s" % policy)
            ui.warn(msg)

_configpaths = []

#TODO: replace with a proper function in config.config

def _configread(orig, cls, path, fp=None, sections=None, remap=None):
    _configpaths.append(path)
    return orig(cls, path, fp, sections, remap)

@exchange.getbundle2partsgenerator('enforceconfigexpress', idx=0)
def _getbundlechangegrouppart(bundler, repo, source, bundlecaps=None,
                              b2caps=None, heads=None, common=None, **kwargs):
    _enforceext(repo.ui, bundler)

def uisetup(ui):
    replycapshandler = bundle2.parthandlermapping['replycaps']
    def wrapper(op, inpart):
        return checkreplycaps(replycapshandler, op, inpart)
    wrapper.params = replycapshandler.params
    bundle2.parthandlermapping['replycaps'] = wrapper
    bundle2.capabilities[_capability] = ()
    extensions.wrapfunction(bundle2, 'processbundle', _finalizeconfig)
    extensions.wrapfunction(config.config, 'read', _configread)
