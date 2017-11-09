# BOTLIB Framework to program bots
#
# botlib/options.py
#
# Copyright 2017 B.H.J Thate
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice don't have to be included.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Bart Thate
# Heerhugowaard
# The Netherlands

""" defines of command line options. """

import os

opts_defs = [
    ('-a', '--all', 'store_true', False, 'all', "load all plugins."),
    ('-b', '--banner', 'store_true', False, 'banner', "show banner"),
    ("-c", "--channel", "string", "", "channel", "channel to join"),
    ('-d', '--workdir', 'string', "", 'workdir', "working directory."),
    ('-e', '--onerror', 'store_true', False, 'onerror', "raise on error."),
    ('-f', '--filelog', "string", "", "filelog", "enable logging to file."),
    ('-g', '--global', "string", "", "global", "use global scope."),
    ('-i', '--init', 'string', "", 'init', "whether to initialize plugins."),
    ('-j', '--jid', 'string', "", 'jid', "set jid to use"),
    ('-k', '--kill', 'store_true', False, 'kill', 'disable user checks.'),
    ('-l', '--loglevel', 'string', "", 'loglevel', "loglevel."),
    ('-m', '--mods', 'string', "", 'mods', "modules to load."),
    ('-n', '--nick', 'string', "", 'nick', "nick to use in channels."),
    ('-o', '--owner', 'string', "root@shell", 'owner', "userhost/JID of the bot owner."),
    ('-p', '--port', 'string', 10102, 'port', "port to run HTTP server on."),
    ('-r', '--resume', 'store_true', False, 'resume', "resume on restart."),
    ('-s', '--server', 'string', '', 'server', "server to connect to."),
    ('-t', '--test', 'store_true', False, 'test', "switch to test mode"),
    ("-u", "--user", "store_true", False, "user", "run in user mode"),
    ('-v', '--verbose', 'store_true', False, 'verbose', 'use verbose mode.'),
    ('-w', '--write', 'store_true', False, 'write', 'save kernel state after boot.'),
    ('-x', '--exclude', 'string', "test", 'exclude', "modules to exclude."),
    ('-y', '--yes', 'store_true', False, 'yes', "enable all boot options."),
    ('-z', '--reboot', 'store_true', False, 'reboot', "enable rebooting."),
    ('-6', '--use_ipv6', 'store_true', False, 'use_ipv6', 'enable ipv6'),
    ('', '--eggs', 'store_true', False, 'eggs', "load eggs located in the current working directory."),
    ('', '--homedir', 'string', os.path.abspath(os.path.expanduser("~")), "homedir", "homedir to use."),
    ('', '--license', 'store_true', '', 'license', 'show licensen or not.'),
    ('', '--no_certs', 'store_true', False, 'no_certs', "disables XMPP certificates."),
    ('', '--room', 'string', "", 'room', "XMPP conference room to join."),
    ('', '--shell', 'store_true', False, 'shell', "start console shell.")
]

opts_defs_event = [
    ('-d', '--dump', 'store_true', False, 'dump', "enable dump mode."),
    ("-u", "--uniq", "string", "", "uniq", "enable uniq filtering on provided key.")
]

opts_defs_sed = [
    ('-d', '--dir', 'string', "", 'dir_sed', "directory to work with."),
    ('-l', '--loglevel', 'string', "error", 'loglevel', "loglevel"),
]

opts_defs_udp = [
    ('-p', '--port', 'string', "10102", 'port', "port to run API server on"),
    ('-l', '--loglevel', 'string', "error", 'loglevel', "loglevel"),
]

opts_defs_doctest = [
    ('-e', '--onerror', 'store_true', False, 'onerror', "raise on error"),
    ('-v', '--verbose', 'store_true', False, 'verbose', "use verbose"),
    ('-l', '--loglevel', 'string', "error", 'loglevel', "loglevel"),
]
