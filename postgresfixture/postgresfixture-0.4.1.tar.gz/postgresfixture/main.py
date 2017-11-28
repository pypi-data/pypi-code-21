# Copyright 2012-2014 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Manage a PostgreSQL cluster."""

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
    )

__metaclass__ = type
__all__ = [
    "main",
    ]

import argparse
from os import (
    environ,
    fdopen,
    )
import pipes
import signal
from subprocess import CalledProcessError
import sys
from time import sleep

from postgresfixture.cluster import (
    PG_VERSION_MAX,
    PG_VERSIONS,
    )
from postgresfixture.clusterfixture import ClusterFixture


try:
    from itertools import imap
except ImportError:
    imap = map  # Python 3.


def setup():
    # Ensure stdout and stderr are line-bufferred.
    sys.stdout = fdopen(sys.stdout.fileno(), "w", 1)
    sys.stderr = fdopen(sys.stderr.fileno(), "w", 1)
    # Run the SIGINT handler on SIGTERM; `svc -d` sends SIGTERM.
    signal.signal(signal.SIGTERM, signal.default_int_handler)


def repr_pid(pid):
    try:
        pid = int(pid)
    except ValueError:
        return pipes.quote(pid)
    else:
        try:
            with open("/proc/%d/cmdline" % pid, "rb") as fd:
                cmdline = fd.read().rstrip(b"\0").split(b"\0")
        except IOError:
            return "%d (*unknown*)" % pid
        else:
            cmdline = (arg.decode("ascii", "replace") for arg in cmdline)
            return "%d (%s)" % (pid, " ".join(imap(pipes.quote, cmdline)))


def locked_by_description(lock):
    pids = sorted(lock.locked_by)
    return "locked by:\n* %s" % (
        "\n* ".join(imap(repr_pid, pids)))


def error(*args, **kwargs):
    kwargs.setdefault("file", sys.stderr)
    return print(*args, **kwargs)


def action_destroy(cluster, arguments):
    """Destroy the cluster."""
    action_stop(cluster, arguments)
    cluster.destroy()
    if cluster.exists:
        if cluster.shares.locked:
            message = "%s: cluster is %s" % (
                cluster.datadir, locked_by_description(cluster.shares))
        else:
            message = "%s: cluster could not be removed." % cluster.datadir
        error(message)
        raise SystemExit(2)


def action_run(cluster, arguments):
    """Create and run the cluster."""
    database_name = arguments.dbname
    command = arguments.command
    with cluster:
        if database_name is not None:
            cluster.createdb(database_name)
        if command is None or len(command) == 0:
            while cluster.running:
                sleep(5.0)
        else:
            cluster.execute(*command)


def action_shell(cluster, arguments):
    """Spawn a `psql` shell for a database in the cluster."""
    database_name = arguments.dbname
    with cluster:
        cluster.createdb(database_name)
        cluster.shell(database_name)


def action_status(cluster, arguments):
    """Display a message about the state of the cluster.

    The return code is also set: 0 indicates that the cluster is running; 1
    indicates that it exists, but is not running; 2 indicates that it does not
    exist.
    """
    if cluster.exists:
        if cluster.running:
            print("%s: running" % cluster.datadir)
            raise SystemExit(0)
        else:
            print("%s: not running" % cluster.datadir)
            raise SystemExit(1)
    else:
        print("%s: not created" % cluster.datadir)
        raise SystemExit(2)


def action_stop(cluster, arguments):
    """Stop the cluster."""
    cluster.stop()
    if cluster.running:
        if cluster.shares.locked:
            message = "%s: cluster is %s" % (
                cluster.datadir, locked_by_description(cluster.shares))
        else:
            message = "%s: cluster is still running." % cluster.datadir
        error(message)
        raise SystemExit(2)


argument_parser = argparse.ArgumentParser(description=__doc__)
argument_parser.add_argument(
    "-D", "--datadir", dest="datadir", action="store",
    metavar="PGDATA", default="db", help=(
        "the directory in which to place, or find, the cluster "
        "(default: %(default)s)"))
argument_parser.add_argument(
    "--preserve", dest="preserve", action="store_true",
    default=False, help=(
        "preserve the cluster and its databases when exiting, "
        "even if it was necessary to create and start it "
        "(default: %(default)s)"))
argument_parser.add_argument(
    "--version", dest="version", choices=PG_VERSIONS,
    default=PG_VERSION_MAX, help=(
        "The version of PostgreSQL to use (default: %(default)s)"))
argument_subparsers = argument_parser.add_subparsers(
    title="actions")


def add_action(name, handler, *args, **kwargs):
    """Configure a subparser for the given name and function."""
    parser = argument_subparsers.add_parser(
        name, *args, help=handler.__doc__, **kwargs)
    parser.set_defaults(handler=handler)
    return parser


def get_action(name):
    """Retrieve the named subparser."""
    return argument_subparsers.choices[name]


# Register actions.
add_action("destroy", action_destroy)
add_action("run", action_run)
add_action("shell", action_shell)
add_action("status", action_status)
add_action("stop", action_stop)


# Customise argument lists for individual actions.
get_action("run").add_argument(
    "-d", "--dbname", dest="dbname", action="store", metavar="PGDATABASE",
    default=environ.get("PGDATABASE", None), help=(
        "if specified, the database to create. The default is taken from "
        "the PGDATABASE environment variable (current default: "
        "%(default)s)."))
get_action("run").add_argument(
    "command", nargs="*", default=None, help=(
        "the command to execute (default: %(default)s)"))
get_action("shell").add_argument(
    "-d", "--dbname", dest="dbname", action="store", metavar="PGDATABASE",
    default=environ.get("PGDATABASE", "data"), help=(
        "the database to create and connect to. The default is taken from "
        "the PGDATABASE environment variable, otherwise 'data' (current "
        "default: %(default)s)."))


def main(args=None):
    args = argument_parser.parse_args(args)
    try:
        setup()
        cluster = ClusterFixture(
            datadir=args.datadir,
            preserve=args.preserve, version=args.version)
        args.handler(cluster, args)
    except CalledProcessError as error:
        raise SystemExit(error.returncode)
    except KeyboardInterrupt:
        pass
