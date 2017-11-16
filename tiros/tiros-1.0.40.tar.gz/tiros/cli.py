from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import json
import textwrap
import sys
from sys import stderr
import tiros.fetch_ as fetch_
import tiros.server as server
import tiros.util as util
import tiros.version as cliversion
from tiros.tiros_viz import app as tiros_viz_app

from tiros.util import eprint, pretty, vprint


def format_response(response, json_errors):
    try:
        j = json.loads(response.text)
    # The exception thrown on json parse failure in python3 is
    # json.decoder.JSONDecodeError, which does not exist in python2.
    # Fortunately, what python2 throws in that case is ValueError,
    # which is a superclass of json.decoder.JSONDecodeError.
    except ValueError:
        j = {'error': response.text}
    warnings = j.get('warnings', [])
    pp_warnings = '\n '.join('- {}'.format(x) for x in warnings)
    if 'error' in j and not json_errors:
        if response.status_code == 504:
            msg = j['error']
        else:
            error = j.get('error')
            try:
                # It reached Tiros Service (tiros error)
                msg = error.get('message')
            except AttributeError:
                # It didn't reach Tiros Service (boto error)
                msg = error
        return msg, pp_warnings
    else:
        return pretty(j.get('results', j)), pp_warnings


def snapshot_session(name):
    if '/' not in name:
        session = util.new_session(profile_name=name)
    else:
        [name, region] = name.split('/')
        session = util.new_session(profile_name=name, region_name=region)
    return session


# XXX: Remove this.  The code that calls Tiros on a Palisade snapshot
# should be the one doing the json surgery here.
def autodetect_raw_snapshot(s):
    # For Palisade snapshots, the raw snapshot holds the actual snapshot
    # in the db field
    if 'db' in s:
        return s.get('db')
    else:
        return s


def get_throttle(args):
    throttle = {}
    if args.max_calls_per_second_ec2:
        throttle['ec2'] = args.max_calls_per_second_ec2
    if args.max_calls_per_second_elb:
        throttle['elb'] = args.max_calls_per_second_elb
    if args.max_calls_per_second_elb2:
        throttle['elb2'] = args.max_calls_per_second_elb2
    return throttle


def is_localhost(host):
    ipv4 = '127.0.0.1'
    ipv6 = '::1'
    ipv6_with_port = '[::1]'
    localhost = 'localhost'
    return any(host.startswith(s)
               for s in [ipv4, ipv6, ipv6_with_port, localhost])


general_args = argparse.ArgumentParser(add_help=False)

general_args.add_argument(
    '--profile',
    help='The AWS profile to use for signing requests'
)

general_args.add_argument(
    '--region',
    help='The AWS region to use for signing requests'
)

general_args.add_argument(
    '--verbose',
    '-v',
    action='store_true',
    help='Be chatty'
)

general_args.add_argument(
    '--quiet',
    '-q',
    action='store_true',
    help='Do not show warning messages'
)

server_args = argparse.ArgumentParser(add_help=False)

server_args.add_argument(
    '--dev',
    action='store_true',
    help='Use the dev server'
)

server_args.add_argument(
    '--host',
    help='''
    Tiros host.  If the port is nonstandard, include it here,
    e.g. localhost:9000
    '''
)

server_args.add_argument(
    '--json',
    action='store_true',
    help='Force json output, even for errors'
)

server_args.add_argument(
    '--max-calls-per-second-ec2',
    help='Throttle the EC2 endpoints'
)

server_args.add_argument(
    '--max-calls-per-second-elb',
    help='Throttle the elasticloadbalancing endpoints'
)

server_args.add_argument(
    '--max-calls-per-second-elb2',
    help='Throttle the elasticloadbalancingv2 endpoints'
)

server_args.add_argument(
    '--no-ssl',
    action='store_true',
    help="Don't use SSL.  This argument is implied by --host localhost:*"
)

server_args.add_argument(
    '--paranoid',
    action='store_true',
    help="Don't log any data on the server side."
)

server_args.add_argument(
    '--raw-snapshot-file',
    '-r',
    default=[],
    action='append',
    help='File containing the raw JSON snapshot'
)

server_args.add_argument(
    '--snapshot-file',
    '-s',
    default=[],
    action='append',
    help='File containing the raw JSON snapshot'
)

server_args.add_argument(
    '--snapshot-profile',
    '-n',
    action='append',
    help="""
    An AWS profile name or profile/region pair.
    (e.g. dev, dev/us-east-1, prod/us-west-2).
    Multiple profiles are supported.  If no profile is
    provided the default is used. If no region
    is specified for a profile, the default region for the
    profile is used.
    """
)

server_args.add_argument(
    '--unsafe-ignore-classic',
    action='store_true',
    help="""
    Silently drop any VPC Classic resources we discover.  You can not
    trust Tiros results when this flag is set!  If ClassicLink is used
    in a VPC, Tiros has no information about the linked Classic instances.
    """
)

parser = argparse.ArgumentParser(
    description='Tiros, version ' + util.TIROS_VERSION)

subparsers = parser.add_subparsers(title='subcommands', dest='cmd')


def main():
    args = parser.parse_args()
    if not args.cmd:
        print("No subcommand specified")
        parser.print_help()
        sys.exit(1)
    if args.verbose:
        util.VERBOSE = True
    args.func(args)


# ---------- fetch -----------


def fetch(args):
    session = util.new_session(profile_name=args.profile,
                               region_name=args.region)
    if args.region:
        session = util.change_session_region(session, args.region)
    print(util.pretty(fetch_.fetch(session)))


fetch_parser = subparsers.add_parser(
    'fetch',
    parents=[general_args],
    help='Fetch a tiros snapshot using local credentials'
)

fetch_parser.set_defaults(func=fetch)


# ---------- query ----------


query_parser = subparsers.add_parser(
    'query',
    parents=[general_args, server_args],
    help='Query a network using TQL'
)


def query(args):
    session = util.new_session(profile_name=args.profile,
                               region_name=args.region)
    host = args.host or (server.DEV_HOST if args.dev else server.PROD_HOST)
    ssl = not args.no_ssl and not is_localhost(host)
    snapshot_sessions = [snapshot_session(p)
                         for p in (args.snapshot_profile or [])]
    snapshots = [json.loads(util.file_contents(f))
                 for f in (args.snapshot_file or [])]
    raw_snapshots = [autodetect_raw_snapshot(json.loads(util.file_contents(f)))
                     for f in (args.raw_snapshot_file or [])]
    if args.inline and args.queries_file:
        eprint("Can't specify both --inline and --queries_file")
    queries = None
    if args.inline:
        queries = args.inline
    elif args.queries_file:
        queries = util.file_contents(args.queries_file)
    else:
        eprint('You must specify --inline or --queries_file')
    if args.relations_file:
        user_relations = util.file_contents(args.relations_file)
    else:
        user_relations = None
    response = server.query(
        signing_session=session,
        queries=queries,
        backend=args.backend,
        host=host,
        raw_snapshots=raw_snapshots,
        snapshot_sessions=snapshot_sessions,
        snapshots=snapshots,
        ssl=ssl,
        throttle=get_throttle(args),
        transforms=args.transform,
        unsafe_ignore_classic=args.unsafe_ignore_classic,
        user_relations=user_relations)
    vprint('Status code: ' + str(response.status_code))
    query_result, warnings = format_response(response, args.json)
    print(query_result)
    if not args.quiet:
        stderr.write(warnings+"\n")
    if response.status_code != 200:
        sys.exit(1)
    sys.exit(0)


query_parser.set_defaults(func=query)

query_parser.add_argument(
    '--backend',
    '-b',
    help='Datalog backend'
)

query_parser.add_argument(
    '--inline',
    '-i',
    help='Inline query'
)

query_parser.add_argument(
    '--queries-file',
    '-f',
    default=None,
    help='File containing the JSON Tiros queries'
)

query_parser.add_argument(
    '--relations-file',
    '-l',
    default=None,
    help='User relations file'
)

query_parser.add_argument(
    '--transform',
    '-x',
    action='append',
    default=[],
    help='''
    Apply source transforms. Available: magic-sets.
    By default Tiros uses a heuristic to select which transforms to apply.
    Use -x no-TRANSFORM to disable the transform in the heuristic.
    '''
)


# ---------- snapshot ----------


def snapshot(args):
    session = util.new_session(profile_name=args.profile,
                               region_name=args.region)
    host = args.host or (server.DEV_HOST if args.dev else server.PROD_HOST)
    ssl = not args.no_ssl and not is_localhost(host)
    snapshot_sessions = [snapshot_session(p)
                         for p in (args.snapshot_profile or [])]
    snapshots = [json.loads(util.file_contents(f))
                 for f in (args.snapshot_file or [])]
    raw_snapshots = [autodetect_raw_snapshot(json.loads(util.file_contents(f)))
                     for f in (args.raw_snapshot_file or [])]
    response = server.snapshot(
        host=host,
        raw_snapshots=raw_snapshots,
        paranoid=args.paranoid,
        signing_session=session,
        snapshot_sessions=snapshot_sessions,
        snapshots=snapshots,
        ssl=ssl,
        throttle=get_throttle(args),
        unsafe_ignore_classic=args.unsafe_ignore_classic,
    )
    vprint('Status code: ' + str(response.status_code))
    snap, warnings = format_response(response, args.json)
    print(snap)
    if not args.quiet:
        stderr.write(warnings+"\n")
    if response.status_code != 200:
        sys.exit(1)
    sys.exit(0)


snapshot_parser = subparsers.add_parser(
    'snapshot',
    parents=[general_args, server_args],
    help="Get a network snapshot using the Tiros service's credentials"
)

snapshot_parser.set_defaults(func=snapshot)

# ---------- viz -----------
viz_parser = subparsers.add_parser(
    'viz',
    parents=[general_args, server_args],
    help='Tiros Snapshot Visualization.'
)


def viz(args):
    snapshot_sessions = [snapshot_session(p)
                         for p in (args.snapshot_profile or [])]
    throttle = get_throttle(args)
    tiros_viz_app.main(args, snapshot_sessions, throttle)


viz_parser.set_defaults(func=viz)

viz_parser.add_argument(
    '--viz_port',
    '-vp',
    default=5000,
    type=int,
    help='Port number for Tiros visualization'
)

# ---------- version ----------


version_parser = subparsers.add_parser(
    'version',
    parents=[general_args],
    help='Print Tiros version information and exit'
)


def version(args):
    print('Tiros version: {}'.format(util.TIROS_VERSION))
    print('Tiros cli version: {}'.format(cliversion.__version__))


version_parser.set_defaults(func=version)

if __name__ == '__main__':
    main()
