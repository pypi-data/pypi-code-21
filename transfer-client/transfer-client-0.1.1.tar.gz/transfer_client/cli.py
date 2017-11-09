from __future__ import unicode_literals

from os.path import basename
import StringIO
import argparse
import datetime
import getpass
import hashlib
import json
import os
import socket
import sys

from jsonschema.exceptions import ValidationError
import jsonschema
import yaml

from . import doc_split, usage, version
from .local import Cache, Config, rel_abs, abs_arc, flat_list
from .stream import StreamMeta, Pipe, tgz_stream
from .transfer_client import TransferClient


def _write(output_handle, data, output_format):
    """Format `data` and write it to the output handle."""
    if output_format == 'yaml':
        output_handle.write(yaml.safe_dump(
            data, width=76, default_flow_style=False,
            allow_unicode=True).decode('utf-8'))
    else:
        output_handle.write('{}\n'.format(json.dumps(data, indent=4)))


# Configuration.
def set_default(log_handle, config, name, value):
    set_value = config.set_default(name, value)
    log_handle.write('{} set to {}\n'.format(name, set_value))


def defaults(log_handle, config, output_format):
    _write(log_handle, config.defaults(), output_format)


def add_project(log_handle, config, name, cert_path, key_path):
    config.add_project(name, cert_path, key_path)
    log_handle.write('Added project {}\n'.format(name))


def del_project(log_handle, config, name):
    config.del_project(name)
    log_handle.write('Removed project {}\n'.format(name))


def projects(log_handle, config, output_format):
    _write(log_handle, config.projects(), output_format)


# Cache.
# NOTE: cache interfaces here.

# API.
def about(output_handle, server_name, ssl_check, ca_bundle, output_format):
    client = TransferClient(server_name, ssl_check, ca_bundle)
    _write(output_handle, client.about(), output_format)


def consumer(
        output_handle, server_name, project_name, ssl_check, ca_bundle,
        cert_path, key_path, output_format):
    client = TransferClient(server_name, ssl_check, ca_bundle,
            (cert_path, key_path))
    _write(output_handle, client.consumer(project_name), output_format)


def consumer_transfers(
        output_handle, server_name, project_name, ssl_check, ca_bundle,
        cert_path, key_path, output_format):
    client = TransferClient(server_name, ssl_check, ca_bundle,
            (cert_path, key_path))
    _write(
        output_handle, client.consumer_transfers(project_name), output_format)


def consumer_transfer(
        output_handle, server_name, project_name, transfer_id, ssl_check,
        ca_bundle, cert_path, key_path, output_format):
    client = TransferClient(server_name, ssl_check, ca_bundle,
            (cert_path, key_path))
    _write(
        output_handle, client.consumer_transfer(project_name, transfer_id),
        output_format)


def producer(
        output_handle, server_name, project_name, ssl_check, ca_bundle,
        cert_path, key_path, output_format):
    client = TransferClient(server_name, ssl_check, ca_bundle,
            (cert_path, key_path))
    _write(output_handle, client.producer(project_name), output_format)


def producer_transfers(
        output_handle, server_name, project_name, ssl_check, ca_bundle,
        cert_path, key_path, output_format):
    client = TransferClient(server_name, ssl_check, ca_bundle,
            (cert_path, key_path))
    _write(
        output_handle, client.producer_transfers(project_name), output_format)


def producer_transfer_start(
        output_handle, metadata_handle, server_name, project_name, ssl_check,
        ca_bundle, cert_path, key_path, output_format):
    client = TransferClient(server_name, ssl_check, ca_bundle,
            (cert_path, key_path))
    _write(output_handle, client.producer_transfer_start(
        project_name, json.loads(metadata_handle.read())), output_format)


def producer_transfer(
        output_handle, server_name, project_name, transfer_id, ssl_check,
        ca_bundle, cert_path, key_path, output_format):
    client = TransferClient(server_name, ssl_check, ca_bundle,
            (cert_path, key_path))
    _write(
        output_handle, client.producer_transfer(project_name, transfer_id),
        output_format)


def producer_transfer_cancel(
        output_handle, server_name, project_name, transfer_id, ssl_check,
        ca_bundle, cert_path, key_path, output_format):
    client = TransferClient(server_name, ssl_check, ca_bundle,
            (cert_path, key_path))
    _write(
        output_handle,
        client.producer_transfer_cancel(project_name, transfer_id),
        output_format)


def producer_upload(
        output_handle, server_name, project_name, transfer_id, file_handle,
        ssl_check, ca_bundle, cert_path, key_path, output_format):
    client = TransferClient(server_name, ssl_check, ca_bundle,
            (cert_path, key_path))
    _write(
        output_handle,
        client.producer_upload(project_name, transfer_id, file_handle),
        output_format)


# Local.
def _minimal_metadata(title, additional=None):
    """Make an empty metadata object."""
    metadata = {'transfer': {'title': title, 'files': []}}

    if additional:
        metadata.update(additional)

    return metadata


def _make_metadata(log_handle, paths, title, additional):
    """Make transfer metadata for a list of files."""
    metadata = _minimal_metadata(title, additional)

    for name in paths:
        log_handle.write(
            'Calculating checksum for file: {}\n'.format(name))
        hash_sum = hashlib.md5()
        with open(name) as handle:
            for chunk in iter(lambda: handle.read(4096), b''):
                hash_sum.update(chunk)

        metadata['transfer']['files'].append({
            'name': basename(name),
            'md5sum': hash_sum.hexdigest()})

    return metadata


def _make_stream_metadata(log_handle, paths, title, additional):
    """Make transfer metadata for a directory."""
    readme = open(os.path.join(os.path.dirname(__file__), 'unpack.md')).read()
    metadata = _minimal_metadata(title, additional)
    metadata['transfer']['files'].append({
        'name': 'README.md',
        'md5sum': hashlib.md5(readme).hexdigest()})
    metadata['transfer']['tags'] = {
        'chunked': True,
        'note': 'Unpack with: `cat chunk_* | tar -xzv`'}

    stream_metadata = StreamMeta(log_handle)
    tgz_stream(stream_metadata, paths)
    stream_metadata.flush()

    metadata['transfer']['files'] += map(
        lambda x: dict(zip(('name', 'md5sum'), x)), stream_metadata.info)

    return metadata, stream_metadata.sizes


def _get_additional_metadata(handle):
    return json.loads(handle.read()) if handle else {}


def make_metadata(
        output_handle, log_handle, file_handles, title, additional_handle):
    """Make transfer metadata for a list of files."""
    # FIXME: This needs to be revised like transfer/resume.
    _write(
        output_handle, _make_metadata(
            log_handle, file_handles, title,
            _get_additional_metadata(additional_handle)), 'json')


def check_metadata(
        metadata_handle, server_name, project_name, ssl_check, ca_bundle,
        cert_path, key_path):
    """Check a metadata file against the JSON schema."""
    client = TransferClient(server_name, ssl_check, ca_bundle,
            (cert_path, key_path))
    jsonschema.validate(
        json.loads(metadata_handle.read()), client.producer(project_name))


# Convenience.
def _sanity_check(transfer_client, project_name, additional):
    """Sanity checking.

    This function tests whether:
    - The server is reachable.
    - The certificate is valid (or checking is disabled).
    - A metadata sample conforms to the schema.
    - There is no active transfer.
    """
    test_metadata = _minimal_metadata('title', additional)
    test_metadata['transfer']['files'].append(
        {'name': 'file', 'md5sum': '00000000000000000000000000000000'})
    jsonschema.validate(test_metadata, transfer_client.producer(project_name))

    transfers = transfer_client.producer_transfers(project_name)
    if transfers and transfers[-1]['status'] == 'initiated':
        raise ValueError('active transfer found')


def _resume(
        log_handle, client, transfer_id, transfer, project_name, entry):
    """Resume an interrupted transfer."""
    abs_paths = entry['paths']

    for file_object, path in zip(transfer['files'], abs_paths):
        if file_object['status'] == 'pending':
            log_handle.write(
                'Uploading file: {}\n'.format(file_object['name']))
            with open(path, 'rb') as file_handle:
                client.producer_upload(project_name, transfer_id, file_handle)


def _transfer(log_handle, client, additional, paths, project_name, title):
    """Transfer a list of files."""
    cache = Cache()
    abs_paths = rel_abs(paths)

    metadata = _make_metadata(log_handle, abs_paths, title, additional)
    cache.set_entry(
        project_name, {
            'paths': abs_paths, 'metadata': metadata, 'chunked': False})
    try:
        transfer_id = client.producer_transfer_start(
            project_name, metadata)['id']
    except (ValueError, OSError, IOError) as error:
        # FIXME: Add message about saving data from cache.
        return
    log_handle.write('Transfer ID: {}\n'.format(transfer_id))

    # NOTE: _resume at this point?
    for name in abs_paths:
        log_handle.write('Uploading file: {}\n'.format(name))
        with open(name) as handle:
            client.producer_upload(project_name, transfer_id, handle)

    cache.del_entry(project_name)


def _resume_chunked(
        log_handle, client, transfer_id, transfer, project_name, entry):
    """Resume an interrupted transfer."""
    # FIXME: This does not upload the README, possible deadlock.
    pt_list = entry['paths']

    pipe = Pipe()

    processid = os.fork()
    if not processid:
        tgz_stream(pipe, pt_list)
        pipe.flush()
        exit()

    sizes = entry['sizes']

    for file_object, size in zip(transfer['files'][1:], sizes):
        if file_object['status'] != 'uploaded':
            log_handle.write(
                'Uploading chunk: {}\n'.format(file_object['name']))
            pipe.set_file(file_object['name'], size)
            client.producer_upload(project_name, transfer_id, pipe)
        else:
            log_handle.write(
                'Skipping chunk: {}\n'.format(file_object['name']))
            pipe.skip(size)


def _transfer_chunked(
        log_handle, client, additional, paths, project_name, title):
    """Transfer a directory."""
    cache = Cache()
    abs_paths = rel_abs(paths)
    pt_list = zip(abs_paths, abs_arc(abs_paths))

    metadata, sizes = _make_stream_metadata(
        log_handle, pt_list, title, additional)
    cache.set_entry(
        project_name, {
            'paths': pt_list, 'metadata': metadata, 'sizes': sizes,
            'chunked': True})
    try:
        transfer_id = client.producer_transfer_start(
            project_name, metadata)['id']
    except (ValueError, OSError, IOError) as error:
        # FIXME: Add message about saving data from cache.
        return
    log_handle.write('Transfer ID: {}\n'.format(transfer_id))

    # NOTE: _resume at this point?
    pipe = Pipe()

    processid = os.fork()
    if not processid:
        tgz_stream(pipe, pt_list)
        pipe.flush()
        exit()

    readme = StringIO.StringIO(open(os.path.join(
        os.path.dirname(__file__), 'unpack.md')).read())
    readme.name = 'README.md'
    client.producer_upload(project_name, transfer_id, readme)

    for item, size in zip(metadata['transfer']['files'][1:], sizes):
        log_handle.write('Uploading chunk: {}\n'.format(item['name']))
        pipe.set_file(item['name'], size)
        client.producer_upload(project_name, transfer_id, pipe)

    cache.del_entry(project_name)


def transfer(
        log_handle, paths, server_name, project_name, title,
        additional_handle, ssl_check, ca_bundle, cert_path, key_path):
    """Transfer a list of paths."""
    client = TransferClient(server_name, ssl_check, ca_bundle,
            (cert_path, key_path))
    additional = _get_additional_metadata(additional_handle)
    _sanity_check(client, project_name, additional)

    if flat_list(paths): # NOTE: Switch to `as_list` at some time.
        _transfer(
            log_handle, client, additional, paths, project_name, title)
    else:
        _transfer_chunked(
            log_handle, client, additional, paths, project_name, title)


def _interrupted_transfer(log_handle, client, project_name):
    """Find an interrupted transfer."""
    transfers = client.producer_transfers(project_name)

    if not (transfers and transfers[-1]['status'] == 'initiated'):
        raise ValueError('no interrupted transfers found')

    transfer = transfers[-1]
    log_handle.write('Transfer ID: {}\n'.format(transfer['id']))

    return transfer


def resume(
        log_handle, server_name, project_name, ssl_check, ca_bundle,
        cert_path, key_path):
    """Resume an interrupted transfer."""
    cache = Cache()
    client = TransferClient(server_name, ssl_check, ca_bundle,
            (cert_path, key_path))

    transfer_id = _interrupted_transfer(log_handle, client, project_name)['id']
    transfer = client.producer_transfer(project_name, transfer_id)
    entry = cache.get_entry(project_name)

    if entry['chunked']:
        _resume_chunked(
            log_handle, client, transfer_id, transfer, project_name, entry)
    else:
        _resume(log_handle, client, transfer_id, transfer, project_name, entry)

    cache.del_entry(project_name)


def cancel(log_handle, server_name, project_name, ssl_check, ca_bundle,
        cert_path, key_path):
    """Cancel an interrupted transfer."""
    client = TransferClient(server_name, ssl_check, ca_bundle,
            (cert_path, key_path))

    transfer = _interrupted_transfer(log_handle, client, project_name)
    client.producer_transfer_cancel(project_name, transfer['id'])


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=usage[0], epilog=usage[1])
    parser.add_argument('-v', action='version', version=version(parser.prog))
    top_subparsers = parser.add_subparsers()

    config = Config()

    # Parent parsers.
    ## Files.
    output_parser = argparse.ArgumentParser(add_help=False)
    output_parser.add_argument(
        '-o', dest='output_handle', metavar='OUTPUT',
        type=argparse.FileType('w'), default=sys.stdout, help='output file')

    log_parser = argparse.ArgumentParser(add_help=False)
    log_parser.add_argument(
        '-l', dest='log_handle', metavar='LOG',
        type=argparse.FileType('w'), default=sys.stderr, help='log file')

    metadata_parser = argparse.ArgumentParser(add_help=False)
    metadata_parser.add_argument(
        'metadata_handle', metavar='METADATA', type=argparse.FileType('r'),
        help='metadata file')

    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        'file_handle', metavar='FILE', type=argparse.FileType('rb'),
        help='file to be transferred')

    files_parser = argparse.ArgumentParser(add_help=False)
    files_parser.add_argument(
        'file_handles', metavar='FILE', type=argparse.FileType('rb'),
        nargs='+', help='files to be transferred')

    additional_parser = argparse.ArgumentParser(add_help=False)
    additional_parser.add_argument(
        '-t', dest='title', type=str,
        default='Transfer from {} by {} using {}'.format(
            socket.gethostname(), getpass.getuser(), parser.prog),
        help='transfer title (default="%(default)s")')
    additional_parser.add_argument(
        '-a', dest='additional_handle', metavar='ADDITINOAL',
        type=argparse.FileType('r'), help='additional metadata')

    ## Configuration.
    name_parser = argparse.ArgumentParser(add_help=False)
    name_parser.add_argument(
        'name', metavar='NAME', type=str, help='name')

    ## API.
    server_parser = argparse.ArgumentParser(add_help=False)
    server_parser.add_argument(
        '-s', dest='server_name', metavar='SERVER', type=str,
        default=config.get_default('server'),
        help='server name (%(type)s default="%(default)s")')

    project_parser = argparse.ArgumentParser(add_help=False)
    project_parser.add_argument(
        '-p', dest='project_name', metavar='PROJECT', type=str,
        default=config.get_default('project'),
        help='project name (%(type)s default="%(default)s")')

    transfer_id_parser = argparse.ArgumentParser(add_help=False)
    transfer_id_parser.add_argument(
        'transfer_id', metavar='TRANSFER', type=str, help='transfer id')

    ssl_parser = argparse.ArgumentParser(add_help=False)
    ssl_parser.add_argument(
        '-n', dest='ssl_check', default=config.get_default('ssl_check'),
        action='store_false', help='disable SSL certificate check')

    ssl_parser.add_argument(
        '-b', dest='ca_bundle', metavar='CA_BUNDLE_PATH', type=str,
        default=config.get_default('ca_bundle'),
        help='alternative SSL ca bundle')

    # FIXME: cert and key do not follow project.
    cert_parser = argparse.ArgumentParser(add_help=False)
    cert_parser.add_argument(
        '-c', dest='cert_path', metavar='CERT', type=str,
        help='path to client certificate (%(type)s default follows project)')
    cert_parser.add_argument(
        '-k', dest='key_path', metavar='KEY', type=str,
        help='path to client key (%(type)s default follows project)')

    format_parser = argparse.ArgumentParser(add_help=False)
    format_parser.add_argument(
        '-f', dest='output_format',
        default=config.get_default('output_format'),
        choices=('json', 'yaml'), help='output format (default=%(default)s)')

    ## Convenience.
    paths_parser = argparse.ArgumentParser(add_help=False)
    paths_parser.add_argument(
        'paths', metavar='PATH', type=str, nargs='+',
        help='paths to be transferred')

    # Subparsers.
    ## Configuration.
    top_subparser = top_subparsers.add_parser('config')
    subparsers = top_subparser.add_subparsers()

    subparser = subparsers.add_parser(
        'set', parents=[log_parser, name_parser],
        description=doc_split(Config.set_default))
    subparser.add_argument('value', metavar='VALUE', type=str, help='value')
    subparser.set_defaults(func=set_default, config=config)

    subparser = subparsers.add_parser(
        'defaults', parents=[log_parser, format_parser],
        description=doc_split(Config.defaults))
    subparser.set_defaults(func=defaults, config=config)

    subparser = subparsers.add_parser(
        'add', parents=[log_parser, name_parser],
        description=doc_split(Config.add_project))
    subparser.add_argument(
        'cert_path', metavar='CERT', type=str,
        help='path to client certificate')
    subparser.add_argument(
        'key_path', metavar='KEY', type=str, help='path to client key')

    subparser.set_defaults(func=add_project, config=config)

    subparser = subparsers.add_parser(
        'del', parents=[log_parser, name_parser],
        description=doc_split(Config.del_project))
    subparser.set_defaults(func=del_project, config=config)

    subparser = subparsers.add_parser(
        'projects', parents=[log_parser, format_parser],
        description=doc_split(Config.projects))
    subparser.set_defaults(func=projects, config=config)

    ## API.
    top_subparser = top_subparsers.add_parser('api')
    subparsers = top_subparser.add_subparsers()

    subparser = subparsers.add_parser(
        'about', parents=[
            output_parser, server_parser, ssl_parser, format_parser],
        description=doc_split(TransferClient.about))
    subparser.set_defaults(func=about)

    subparser = subparsers.add_parser(
        'consumer',
        parents=[
            output_parser, server_parser, project_parser, ssl_parser,
            cert_parser, format_parser],
        description=doc_split(TransferClient.consumer))
    subparser.set_defaults(func=consumer)

    subparser = subparsers.add_parser(
        'consumer_transfers',
        parents=[
            output_parser, server_parser, project_parser, ssl_parser,
            cert_parser, format_parser],
        description=doc_split(TransferClient.consumer_transfers))
    subparser.set_defaults(func=consumer_transfers)

    subparser = subparsers.add_parser(
        'consumer_transfer', parents=[
            output_parser, server_parser, project_parser, transfer_id_parser,
            ssl_parser, cert_parser, format_parser],
        description=doc_split(TransferClient.consumer_transfer))
    subparser.set_defaults(func=consumer_transfer)

    subparser = subparsers.add_parser(
        'producer',
        parents=[
            output_parser, server_parser, project_parser, ssl_parser,
            cert_parser, format_parser],
        description=doc_split(TransferClient.producer))
    subparser.set_defaults(func=producer)

    subparser = subparsers.add_parser(
        'producer_transfers',
        parents=[
            output_parser, server_parser, project_parser, ssl_parser,
            cert_parser, format_parser],
        description=doc_split(TransferClient.producer_transfers))
    subparser.set_defaults(func=producer_transfers)

    subparser = subparsers.add_parser(
        'producer_transfer_start', parents=[
            output_parser, metadata_parser, server_parser, project_parser,
            ssl_parser, cert_parser, format_parser],
        description=doc_split(TransferClient.producer_transfer_start))
    subparser.set_defaults(func=producer_transfer_start)

    subparser = subparsers.add_parser(
        'producer_transfer', parents=[
            output_parser, server_parser, project_parser, transfer_id_parser,
            ssl_parser, cert_parser, format_parser],
        description=doc_split(TransferClient.producer_transfer))
    subparser.set_defaults(func=producer_transfer)

    subparser = subparsers.add_parser(
        'producer_transfer_cancel', parents=[
            output_parser, server_parser, project_parser, transfer_id_parser,
            ssl_parser, cert_parser, format_parser],
        description=doc_split(TransferClient.producer_transfer_cancel))
    subparser.set_defaults(func=producer_transfer_cancel)

    subparser = subparsers.add_parser(
        'producer_upload', parents=[
            output_parser, server_parser, project_parser, transfer_id_parser,
            file_parser, ssl_parser, cert_parser, format_parser],
        description=doc_split(TransferClient.producer_upload))
    subparser.set_defaults(func=producer_upload)

    ## Local.
    top_subparser = top_subparsers.add_parser('local')
    subparsers = top_subparser.add_subparsers()

    subparser = subparsers.add_parser(
        'make_metadata',
        parents=[output_parser, log_parser, files_parser, additional_parser],
        description=doc_split(make_metadata))
    subparser.set_defaults(func=make_metadata)

    subparser = subparsers.add_parser(
        'check_metadata', parents=[
            server_parser, project_parser, ssl_parser, metadata_parser],
        description=doc_split(check_metadata))
    subparser.set_defaults(func=check_metadata)

    ## Convenience.
    subparser = top_subparsers.add_parser(
        'transfer', parents=[
            log_parser, paths_parser, server_parser, project_parser,
            additional_parser, ssl_parser, cert_parser],
        description=doc_split(transfer))
    subparser.set_defaults(func=transfer)

    subparser = top_subparsers.add_parser(
        'resume', parents=[
            log_parser, server_parser, project_parser, ssl_parser,
            cert_parser],
        description=doc_split(resume))
    subparser.set_defaults(func=resume)

    subparser = top_subparsers.add_parser(
        'cancel', parents=[
            log_parser, server_parser, project_parser, ssl_parser,
            cert_parser],
        description=doc_split(cancel))
    subparser.set_defaults(func=cancel)

    try:
        args = parser.parse_args()
    except IOError, error:
        parser.error(error)

    if 'cert_path' in args and args.cert_path == None:
        args.cert_path = config.get_project(args.project_name)['cert']
    if 'key_path' in args and args.key_path == None:
        args.key_path = config.get_project(args.project_name)['key']

    try:
        args.func(**{k: v for k, v in vars(args).items() if k not in ('func')})
    except (ValueError, IOError, OSError, ValidationError) as error:
        parser.error(error)


if __name__ == '__main__':
    main()
