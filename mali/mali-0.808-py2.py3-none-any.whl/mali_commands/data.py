# coding=utf-8
import json
import os
import click
import requests
from mali_commands.legit.dulwich import porcelain
from mali_commands.legit.dulwich.index import _fs_to_tree_path, index_entry_from_stat
from mali_commands.legit.dulwich.objects import Blob
from mali_commands.commons import add_to_data_if_not_none, output_result
from mali_commands.data_volume import create_data_volume, with_repo, validate_repo_data_path
import time


@click.group('data')
def data_commands():
    pass


ignore_files = ['.DS_Store']


def get_total_files_in_path(paths):
    total_files = 0

    for path in paths:
        path = __expend_and_validate_path(path)

        if os.path.isdir(path):
            for root, dirs, files in os.walk(path, followlinks=True):
                for file_ in files:
                    if file_ in ignore_files:
                        continue

                    total_files += 1
        elif path not in ignore_files:
            total_files += 1

    return total_files


def __expend_and_validate_path(path):
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)

    if not os.path.exists(path):
        click.echo('not found %s' % path, err=True)
        exit(1)
        return

    return path


def enumerate_path(paths):
    for path in paths:
        path = __expend_and_validate_path(path)
        if os.path.isfile(path):
            yield path

        for root, dirs, files in os.walk(path, followlinks=True):
            for file_ in files:
                if file_ in ignore_files:
                    continue

                yield os.path.join(root, file_)


@data_commands.command('get')
@click.argument('volumeId')
@click.option('--dataPath', 'data_path', required=True)
@click.pass_context
def _cmd_add_dataPath(ctx, volumeid, data_path):
    result = ctx.obj.handle_api(ctx.obj, requests.get, "data_volumes/{volume_id}".format(volume_id=volumeid))

    create_data_volume(
        result['id'],
        data_path,
        not result['embedded'],
        result.get('display_name'),
        result.get('description'))

    display_name = result.get('display_name', 'No display name provided')
    click.echo('Initialized data volume %s (%s)' % (result['id'], display_name))


@data_commands.command('create')
@click.option('--displayName', required=True)
@click.option('--description', required=False)
@click.option('--org', required=True)
@click.option('--dataPath', required=True)
@click.option('--linked/--embedded', is_flag=True, required=True)
@click.pass_context
def _cmd_create_data_volume(ctx, displayname, description, org, datapath, linked):
    data = {}

    if org == 'me':
        org = None

    add_to_data_if_not_none(data, displayname, "display_name")
    add_to_data_if_not_none(data, org, "org")
    add_to_data_if_not_none(data, description, "description")
    add_to_data_if_not_none(data, not linked, "embedded")

    result = ctx.obj.handle_api(ctx.obj, requests.post, "data_volumes", data)

    data_volume_id = result['id']

    create_data_volume(data_volume_id, datapath, linked, displayname, description)

    click.echo('Initialized data volume %s' % data_volume_id)


@data_commands.command('commit')
@click.argument('volumeId')
@click.option('--message', '-m', required=False)
@click.pass_context
def commit_data_volume(ctx, volumeid, message):
    with with_repo(ctx, volumeid) as repo:
        result = repo.commit(message)

        if 'commit_id' not in result:
            click.echo('no changeset detected', err=True)
            exit(1)

        output_result(ctx, result)


@data_commands.command('log')
@click.option('--path', '-p', required=False)
@click.pass_context
def log_data_volume(ctx, path):
    with with_repo(ctx, path) as r:
        for entry in r.get_walker():
            commit = entry.commit
            click.echo("%s %s" % (commit.id.decode('utf8')[:7], commit.message.decode('utf8')))


@data_commands.command('add')
@click.argument('volumeId')
@click.option('--files', '-f', multiple=True)
@click.option('--commit', is_flag=True, required=False)
@click.option('--message', '-m', required=False)
@click.pass_context
def add_to_data_volume(ctx, volumeid, files, commit, message):
    if commit and not message:
        raise click.UsageError('missing --message when using --commit')

    total_files = get_total_files_in_path(files)
    batch_size = min(total_files // 100, 2000)  # FIXME: hardcoded

    def add_batch(current_batch):
        porcelain.add(repo, current_batch, repo.data_volume_config.embedded)
        bar.update(len(current_batch))

    with with_repo(ctx, volumeid) as repo:
        with click.progressbar(length=total_files) as bar:
            batch = []

            for file_or_path in enumerate_path(files):
                batch.append(file_or_path)
                if len(batch) == batch_size:
                    add_batch(batch)
                    batch = []

            if len(batch) > 0:
                add_batch(batch)

        if commit:
            repo.commit(message)


@data_commands.command('serve')
@click.option('--path', '-p', required=False)
@click.option('--host', '-h', default='127.0.0.1', required=False)
@click.option('--port', default=3030, required=False)
@click.pass_context
def serve_data(ctx, path, host, port):
    from .server import app
    click.echo('Starting server on http://{host}:{port}'.format(host=host, port=port))

    with with_repo(ctx, path) as repo:
        repo.close()
        app.config.update(dict(data_path=repo.data_path, repo_root=repo.repo_root, config_prefix=ctx.obj.config_prefix))
        app.run(host=host, port=port, debug=True)


@data_commands.command('copy')
@click.option('--path', '-p', required=False)
@click.option('--dest', '-d', required=True)
@click.option('--query', '-q', required=False)
@click.pass_context
def copy_data(ctx, path, dest, query):
    from mali_commands import rsync

    dest = dest or os.getcwd()
    dest = os.path.abspath(dest)

    with with_repo(ctx, path, read_only=True) as repo:
        src_files = [os.path.join(repo.data_path, item['@sha']) for item in repo.metadata.query(query)]
        explict_query = repo.metadata.explict_query(query)

    rsync.copy_from_to(repo.data_path, src_files, dest)
    config = create_data_volume(dest, data_path=None, linked=False)
    config.update_and_save({'general': {'query': explict_query, 'total_files': len(src_files)}})


@data_commands.group('metadata')
def metadata_commands():
    pass


def stats_from_json(now, json):
    return os.stat_result((
        0,  # mode
        0,  # inode
        0,  # device
        0,  # hard links
        0,  # owner uid
        0,  # gid
        len(json),  # size
        0,  # atime
        now,
        now,
    ))


@metadata_commands.command('query')
@click.argument('query', nargs=1)
@click.option('--path', '-p', required=False)
@click.pass_context
def query_metadata(ctx, query, path):
    with with_repo(ctx, path, read_only=True) as repo:
        for item in repo.metadata.query(query):
            print(os.path.join(repo.data_path, item['@sha']))


def chunks(l, n):
    result = []
    for item in l:
        result.append(item)

        if len(result) == n:
            yield result
            result = []

    if result:
        yield result


@metadata_commands.command('add')
@click.argument('volumeId')
@click.option('--files', '-f', multiple=True)
@click.option('--data', '-d', required=False)
@click.option('--update/--replace', is_flag=True, default=True, required=False)
@click.pass_context
def add_to_metadata(ctx, volumeid, files, data, update):
    if data is not None:
        if not isinstance(data, bytes):
            data = data.encode('utf8')

    now = time.time()

    data = data.decode('utf8')
    current_data = json.loads(data)

    def filter_internal_data(full_current_data):
        return {key: val for key, val in full_current_data.items() if not key.startswith('@')}

    def compare_data(prev_data):
        prev_data_without_internal = filter_internal_data(prev_data) if prev_data else None

        return prev_data_without_internal == current_data

    def update_data(prev_data=None):
        prev_data = prev_data or {}

        prev_data.update(current_data)

        json_data_text = json.dumps(prev_data, sort_keys=True)

        data_blob = Blob()
        data_blob.data = json_data_text.encode('utf8')

        data_st = stats_from_json(now, json_data_text)

        return data_blob, prev_data, data_st

    def update_enumerate_function(current_batch):
        results = {sha: {} for sha in current_batch}
        for result in repo.metadata.get_head_data(current_batch):
            results[result['@sha']] = result

        for sha in current_batch:
            yield results[sha]

    def override_enumerate_function(current_batch):
        return [{}] * len(current_batch)

    enumerate_function = update_enumerate_function if update else override_enumerate_function

    with with_repo(ctx, volumeid) as repo:
        validate_repo_data_path(repo, volumeid)

        total_files = get_total_files_in_path(files)

        insert_batch_size = max(min(total_files // 20, 2000), 100)  # FIXME: hardcoded

        with click.progressbar(length=total_files) as bar:
            index = repo.open_index()

            for file_path_chunks in chunks(enumerate_path(files), insert_batch_size):
                file_rel_path_chunk = [os.path.relpath(file_path, repo.data_path) for file_path in file_path_chunks]

                data_batch = []

                entries = {}

                for i, prev_json in enumerate(enumerate_function(file_rel_path_chunk)):
                    if compare_data(prev_json):
                        continue

                    blob, json_data, st = update_data(prev_json)
                    data_batch.append((file_rel_path_chunk[i], json_data))

                    file_path = file_path_chunks[i]
                    metadata_path = file_path + '.metadata'

                    metadata_rel_path = os.path.relpath(metadata_path, repo.data_path)
                    metadata_tree_path = _fs_to_tree_path(metadata_rel_path)

                    entries[metadata_tree_path] = index_entry_from_stat(st, blob.id, 0)

                metadata = repo.metadata
                metadata.add_data(data=data_batch)
                index.set_entries(entries)

                bar.update(len(file_path_chunks))
