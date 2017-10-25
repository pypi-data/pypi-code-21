# coding=utf-8
import json
import os
import random
import click
import errno
import requests
from mali_commands.legit.dulwich import porcelain
from mali_commands.legit.dulwich.index import _fs_to_tree_path, index_entry_from_stat
from mali_commands.legit.dulwich.objects import Blob
from mali_commands.commons import add_to_data_if_not_none, output_result
from mali_commands.data_volume import create_data_volume, with_repo, validate_repo_data_path
import time
import shutil


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


def __expend_and_validate_path(path, expand_vars=True, validate_path=True):
    path = os.path.expanduser(path)
    if expand_vars:
        path = os.path.expandvars(path)

    if validate_path:
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


@data_commands.command('map')
@click.argument('volumeId', envvar='VOLUMEID', type=int)
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
@click.argument('volumeId', envvar='VOLUMEID', type=int)
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
@click.argument('volumeId', envvar='VOLUMEID', type=int)
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
@click.argument('volumeId', envvar='VOLUMEID', type=int)
@click.option('--host', '-h', default='127.0.0.1', required=False)
@click.option('--port', default=3030, required=False)
@click.pass_context
def serve_data(ctx, volumeid, host, port):
    from .server import app
    click.echo('Starting server on http://{host}:{port}'.format(host=host, port=port))

    with with_repo(ctx, volumeid) as repo:
        repo.close()
        app.config.update(dict(data_path=repo.data_path, repo_root=repo.repo_root, config_prefix=ctx.obj.config_prefix))
        app.run(host=host, port=port, debug=True)


def get_file_phase(split):
    rand = random.uniform(0, 1)

    phase = None
    for key, ranges in split.items():
        start_range, end_range = ranges

        if rand >= start_range < end_range:
            phase = key
            break

    return phase


def fill_in_vars(path, replace_vars):
    for var_name, var_value in replace_vars.items():
        path = path.replace('$' + var_name, str(var_value))

    return path


def safe_make_dirs(dir):
    try:
        os.makedirs(dir)
    except OSError as ex:
        if ex.errno != errno.EEXIST:
            raise


def path_elements(path):
    folders = []
    while 1:
        path, folder = os.path.split(path)

        if folder != "":
            folders.append(folder)
        else:
            if path != "":
                folders.append(path)

            break

    folders.reverse()

    return folders


def safe_rm_tree(path):
    try:
        shutil.rmtree(path)
    except OSError as ex:
        if ex.errno != errno.ENOENT:
            raise


@data_commands.command('clone')
@click.argument('volumeId', envvar='VOLUMEID', type=int)
@click.option('--dest', '-d', required=True)
@click.option('--query', '-q', required=False)
@click.option('--delete', is_flag=True, required=False)
@click.pass_context
def clone_data(ctx, volumeid, dest, query, delete):
    dest = __expend_and_validate_path(dest, expand_vars=False, validate_path=False)

    def find_dest_root():
        elements = path_elements(dest)

        root = []
        for element in elements:
            if element.startswith('$'):
                break

            root.append(element)

        return os.path.join(*root)

    if delete:
        root_dest = find_dest_root()
        safe_rm_tree(root_dest)

    if '$phase' not in dest and '$@' not in dest:
        dest = os.path.join(dest, '$@')

    if '$name' not in dest and '$path' not in dest:
        dest = os.path.join(dest, '$name')

    split = {
        'train': (0.0, 0.7),
        'test': (0.7, 0.8),
        'validation': (0.8, 1.0),
    }

    with with_repo(ctx, volumeid, read_only=True) as repo:
        results = list(repo.metadata.query(query))
        with click.progressbar(length=len(results)) as bar:
            for item in results:
                type, data = repo.object_store.get_raw(item['id'])

                phase = get_file_phase(split)

                if phase is None:
                    continue

                item['phase'] = phase
                item['@'] = phase
                item['name'] = os.path.basename(item['path'])
                item['dir'] = os.path.dirname(item['path'])
                item['path'] = item['path']
                dest_file = fill_in_vars(dest, item)

                safe_make_dirs(os.path.dirname(dest_file))

                with open(dest_file, 'w') as f:
                    f.write(data)

                bar.update(1)


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
@click.argument('volumeId', envvar='VOLUMEID', type=int)
@click.argument('query', nargs=1)
@click.pass_context
def query_metadata(ctx, query, path):
    with with_repo(ctx, path, read_only=True) as repo:
        for item in repo.query(query):
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
@click.argument('volumeId', envvar='VOLUMEID', type=int)
@click.option('--files', '-f', multiple=True)
@click.option('--data', '-d', required=False)
@click.option('--property', '-p', required=False, type=(str, str), multiple=True)
@click.option('--propertyInt', '-pi', required=False, type=(str, int), multiple=True)
@click.option('--propertyFloat', '-pf', required=False, type=(str, float), multiple=True)
@click.option('--update/--replace', is_flag=True, default=True, required=False)
@click.pass_context
def add_to_metadata(ctx, volumeid, files, data, property, propertyint, propertyfloat, update):
    if data is not None:
        if not isinstance(data, bytes):
            data = data.encode('utf8')

    now = time.time()

    current_data = {}

    if data:
        data = data.decode('utf8')
        current_data = json.loads(data)

    for props in (property, propertyint, propertyfloat):
        if not props:
            continue

        for prop_name, prop_val in props:
            current_data[prop_name] = prop_val

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
