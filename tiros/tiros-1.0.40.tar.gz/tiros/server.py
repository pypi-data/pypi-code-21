from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import requests
import semantic_version

import tiros.util as util
from tiros.auth import AuthSession
from tiros.util import pretty, eprint, vprint
from tiros.version import __version__

# Use new-style classes in Python 2
__metaclass__ = type


API_VERSION = 1
DEV_HOST = 'dev.tiros.amazonaws.com'
PROD_HOST = 'prod.tiros.amazonaws.com'


def get_cli_version():
    v = semantic_version.Version(__version__)
    return {'major': v.major, 'minor': v.minor, 'patch': v.patch}


def get_route(command):
    return ''.join(['/v', str(API_VERSION), '/', command])


def get_endpoint(ssl, host, route):
    if host in [DEV_HOST, PROD_HOST] and not ssl:
        eprint("You must use SSL with the dev and prod hosts")
    proto = 'https' if ssl else 'http'
    return ''.join([proto, '://', host, route])


def get_headers(amz_date, auth_header, signing_session):
    headers = {
        'Authorization': auth_header,
        'Content-Type': util.CONTENT_TYPE,
        'X-Amz-Date': amz_date
    }
    token = signing_session.token()
    if token:
        headers['X-Amz-Security-Token'] = token
    return headers


def get_default_snapshot_sessions(signing_session, snapshot_sessions,
                                  snapshots, raw_snapshots):
    """
    If no snapshots are provided, use the signing session as a snapshot 
    session.
    """
    if not snapshot_sessions and not snapshots and not raw_snapshots:
        if not signing_session.region_name:
            eprint('No snapshots given and the signing session has no region')
        return [signing_session]
    return snapshot_sessions


def snapshot(signing_session,
             host=PROD_HOST,
             throttle=None,
             raw_snapshots=None,
             paranoid=False,
             snapshot_sessions=None,
             snapshots=None,
             source=None,
             ssl=True,
             unsafe_ignore_classic=False):
    """
    Create a JSON snapshot containing the combined networks.
    """
    assert signing_session.region_name
    # noinspection PyUnresolvedReferences
    now = datetime.datetime.utcnow()
    amz_date = now.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = now.strftime('%Y%m%d')
    route = get_route('snapshot')
    endpoint = get_endpoint(ssl, host, route)
    snapshot_sessions = get_default_snapshot_sessions(
        signing_session=signing_session,
        snapshot_sessions=snapshot_sessions,
        snapshots=snapshots,
        raw_snapshots=raw_snapshots)
    auth_sessions = [AuthSession(p) for p in (snapshot_sessions or [])]
    dbs = (
        [{'credentials': s.snapshot_key(amz_date, date_stamp, host)} for s in auth_sessions] +
        [{'snapshot': s} for s in (snapshots or [])] +
        [{'raw_snapshot': s} for s in (raw_snapshots or [])]
    )
    obj_body = {
        'cliVersion': get_cli_version(),
        'dbs': dbs,
        'ignore-classic': unsafe_ignore_classic,
        'paranoid': paranoid,
        'source': source,
        'throttle': throttle
    }
    if source:
        obj_body['source'] = source
    body = util.canonical(obj_body)
    vprint('Body: ' + body)
    auth_session = AuthSession(signing_session)
    auth_header = auth_session.auth_header(
        amz_date, body, date_stamp, host, util.METHOD, route)
    headers = get_headers(amz_date, auth_header, auth_session)
    vprint('Headers: ' + pretty(headers))
    return requests.request(util.METHOD, endpoint, headers=headers, data=body)


def query(signing_session,
          queries,
          backend=None,
          host=PROD_HOST,
          raw_snapshots=None,
          snapshot_sessions=None,
          snapshots=None,
          source=None,
          ssl=True,
          throttle=None,
          transforms=None,
          unsafe_ignore_classic=False,
          user_relations=None):
    """Query."""
    # noinspection PyUnresolvedReferences
    now = datetime.datetime.utcnow()
    amz_date = now.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = now.strftime('%Y%m%d')
    route = get_route('query')
    endpoint = get_endpoint(ssl, host, route)
    snapshot_sessions = get_default_snapshot_sessions(
        signing_session=signing_session,
        snapshot_sessions=snapshot_sessions,
        snapshots=snapshots,
        raw_snapshots=raw_snapshots)
    auth_sessions = [AuthSession(p) for p in (snapshot_sessions or [])]
    dbs = (
        [{'credentials': s.snapshot_key(amz_date, date_stamp, host)}
         for s in auth_sessions] +
        [{'snapshot': s} for s in (snapshots or [])] +
        [{'raw_snapshot': s} for s in (raw_snapshots or [])]
    )
    obj_body = {
        'cliVersion': get_cli_version(),
        'dbs': dbs,
        'ignore-classic': unsafe_ignore_classic,
        'queries': queries,
        'source': source,
        'throttle': throttle,
    }
    if backend:
        obj_body['backend'] = backend
    if source:
        obj_body['source'] = source
    if transforms:
        obj_body['transforms'] = transforms
    if user_relations:
        obj_body['userRelations'] = user_relations
    body = util.canonical(obj_body)
    vprint('Body: ' + body)
    auth_session = AuthSession(signing_session)
    auth_header = auth_session.auth_header(
        amz_date, body, date_stamp, host, util.METHOD, route)
    headers = get_headers(amz_date, auth_header, auth_session)
    vprint('Headers: ' + pretty(headers))
    return requests.request(util.METHOD, endpoint, headers=headers, data=body)
