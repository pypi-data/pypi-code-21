# coding=utf-8
import json
import os
from contextlib import closing
import click
import errno
import requests
from tqdm import tqdm

from mali_commands.config import Config
from mali_commands.legit.dulwich import porcelain
from mali_commands.legit.dulwich.index import index_entry_from_stat, _fs_to_tree_path
from mali_commands.legit.dulwich.objects import Blob
from mali_commands.commons import add_to_data_if_not_none, output_result
from mali_commands.data_volume import create_data_volume, with_repo, validate_repo_data_path
import time
import shutil

from mali_commands.legit.multi_process_control import MultiProcessControl, MultiProcessControlShim


@click.group('data')
def data_commands():
    pass


ignore_files = ['.DS_Store']


def enumerate_path(path):
    path = __expend_and_validate_path(path)
    if os.path.isfile(path):
        yield path
        return
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path, followlinks=True):
            for file_ in files:
                if file_ in ignore_files:
                    continue
                yield os.path.join(root, file_)
                # TODOx: ASK SHAY
                # elif path not in ignore_files:
                #     total_files += 1


def enumerate_paths(paths):
    for path in paths:
        for file_ in enumerate_path(path):
            yield file_


def get_total_files_in_path(paths):
    total_files = 0
    for _ in enumerate_paths(paths):
        total_files += 1
    return total_files


def __expend_and_validate_path(path, expand_vars=True, validate_path=True, abs_path=True):
    path = os.path.expanduser(path)
    if expand_vars:
        path = os.path.expandvars(path)

    if abs_path:
        path = os.path.abspath(path)

    if validate_path:
        if not os.path.exists(path):
            click.echo('not found %s' % path, err=True)
            exit(1)
            return

    return path


def get_batch_of_files_from_paths(paths, batch_size):
    batch = []
    for file_or_path in enumerate_paths(paths):
        batch.append(file_or_path)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if len(batch) > 0:
        yield batch


@data_commands.command('map')
@click.argument('volumeId', envvar='VOLUMEID', type=int)
@click.option('--dataPath', required=True)
@click.pass_context
def _cmd_add_dataPath(ctx, volumeid, datapath):
    result = ctx.obj.handle_api(ctx.obj, requests.get, "data_volumes/{volume_id}".format(volume_id=volumeid))

    datapath = __expend_and_validate_path(datapath)

    create_data_volume(
        result['id'],
        datapath,
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

    expiration = ctx.obj.config.readonly_items('data_volumes').get('expiration')
    if expiration:
        data['expiration'] = expiration

    result = ctx.obj.handle_api(ctx.obj, requests.post, "data_volumes", data)

    data_volume_id = result['id']

    datapath = __expend_and_validate_path(datapath)

    create_data_volume(data_volume_id, datapath, linked, displayname, description)

    output_result(ctx, result)


@data_commands.command('commit')
@click.argument('volumeId', envvar='VOLUMEID', type=int)
@click.option('--message', '-m', required=False)
@click.pass_context
def commit_data_volume(ctx, volumeid, message):
    with with_repo(ctx.obj.config, volumeid) as repo:
        result = repo.commit(message)

        if 'commit_id' not in result:
            click.echo('no changeset detected', err=True)
            exit(1)

        output_result(ctx, result)


@data_commands.command('log')
@click.option('--path', '-p', required=False)
@click.pass_context
def log_data_volume(ctx, path):
    with with_repo(ctx.obj.config, path) as r:
        for entry in r.get_walker():
            commit = entry.commit
            click.echo("%s %s" % (commit.id.decode('utf8')[:7], commit.message.decode('utf8')))


def _run_add_batches(paths, repo, no_progressbar=False):
    total_files = get_total_files_in_path(paths)
    batch_size = min(total_files // 100, 250)  # FIXME: hardcoded
    with tqdm(total=total_files, desc="Adding files", unit=' files', ncols=80, disable=no_progressbar) as bar:
        for current_batch in get_batch_of_files_from_paths(paths, batch_size):
            porcelain.add(repo, current_batch, repo.data_volume_config.embedded)
            bar.update(len(current_batch))


@data_commands.command('add')
@click.argument('volumeId', envvar='VOLUMEID', type=int)
@click.option('--files', '-f', multiple=True)
@click.option('--commit', is_flag=True, required=False)
@click.option('--message', '-m', required=False)
@click.option('--processes', default=-1, type=int, required=False)
@click.option('--no_progressbar/--enable_progressbar', default=False, is_flag=True, required=False)
@click.pass_context
def add_to_data_volume(ctx, volumeid, files, commit, message, processes, no_progressbar):
    def _validate_message_for_commit():
        if commit and not message:
            raise click.UsageError('missing --message when using --commit')

    _validate_message_for_commit()

    with with_repo(ctx.obj.config, volumeid) as repo:
        if processes != -1:
            repo.data_volume_config.object_store_config['processes'] = processes

        _run_add_batches(files, repo, no_progressbar)
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

    with with_repo(ctx.obj.config, volumeid) as repo:
        repo.close()
        app.config.update(dict(data_path=repo.data_path, repo_root=repo.repo_root, config_prefix=ctx.obj.config_prefix))
        app.run(host=host, port=port, debug=True)


def fill_in_vars(path, replace_vars):
    for var_name, var_value in replace_vars.items():
        path = path.replace('$' + var_name, str(var_value))

    for var_name, var_value in replace_vars.items():
        path = path.replace('#' + var_name, str(var_value))

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


def __download_entity(config_init_dict, volume_id, dest, item):
    import google.api_core.exceptions

    config = Config(**config_init_dict)

    with with_repo(config, volume_id, read_only=True) as repo:
        try:
            _, data = repo.object_store.get_raw(item['id'])
        except requests.exceptions.HTTPError as ex:
            if ex.response.status_code == 404:
                return

            raise
        except google.api_core.exceptions.NotFound:
            return

        phase = item.get('phase')

        if phase is None:
            return

        _, file_extension = os.path.splitext(item['path'])

        item['phase'] = phase
        item['@'] = phase
        item['name'] = os.path.basename(item['path'])
        item['dir'] = os.path.dirname(item['path'])
        item['path'] = item['path']
        item['ext'] = os.path.basename(file_extension)
        dest_file = fill_in_vars(dest, item)

        safe_make_dirs(os.path.dirname(dest_file))

        if os.path.exists(dest_file):
            click.echo('file %s already exists, overriding' % dest_file, err=True)

        with open(dest_file, 'w') as f:
            f.write(data)


@data_commands.command('clone')
@click.argument('volumeId', envvar='VOLUMEID', type=int)
@click.option('--dest', '-d', required=True)
@click.option('--query', '-q', required=False)
@click.option('--delete', is_flag=True, required=False)
@click.option('--batchSize', required=False, default=500)
@click.option('--processes', default=-1, type=int, required=False)
@click.option('--no_progressbar/--enable_progressbar', default=False, is_flag=True, required=False)
@click.pass_context
def clone_data(ctx, volumeid, dest, query, delete, batchsize, processes, no_progressbar):
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

    if '$name' not in dest and '$path' not in dest and '$id' not in dest:
        dest = os.path.join(dest, '$id$ext')

    start_index = 0

    def get_next_results():
        current_results, current_total_data_points = repo.metadata.query(query, max_results=batchsize, start_index=start_index)

        return list(current_results), current_total_data_points

    multi_process_control = MultiProcessControl(processes) if processes != 1 else MultiProcessControlShim()

    try:
        with with_repo(ctx.obj.config, volumeid, read_only=True) as repo:
            results, total_data_points = get_next_results()

            with tqdm(total=total_data_points, desc="Downloading", unit=' data point', ncols=80, disable=no_progressbar) as bar:
                with closing(multi_process_control):
                    while True:
                        for item in results:
                            config_init_dict = ctx.obj.config.init_dict

                            multi_process_control.execute(__download_entity, args=(config_init_dict, volumeid, dest, item), callback=lambda _: bar.update())

                        if len(results) != batchsize:
                            break

                        start_index += len(results)

                        results, total_data_points = get_next_results()
    except KeyboardInterrupt:
        multi_process_control.terminate()
        multi_process_control.close()


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


@data_commands.command('query')
@click.argument('volumeId', envvar='VOLUMEID', type=int)
@click.option('--query', '-q')
@click.option('--batchSize', required=False, default=500)
@click.pass_context
def query_metadata(ctx, volumeid, query, batchsize):
    def get_next_results():
        current_results, current_total_data_points = repo.metadata.query(query, max_results=batchsize, start_index=start_index)

        return list(current_results), current_total_data_points

    total_results = []
    start_index = 0
    with with_repo(ctx.obj.config, volumeid) as repo:
        results, total_data_points = get_next_results()
        while True:
            total_results.extend(results)

            if len(results) != batchsize:
                break

            start_index += len(results)

            results, total_data_points = get_next_results()

    output_result(ctx, total_results)


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
@click.option('--dataPoint', '-dp', multiple=True)
@click.option('--dataFile', '-df', required=False, type=click.File('rb'))
@click.option('--property', '-p', required=False, type=(str, str), multiple=True)
@click.option('--propertyInt', '-pi', required=False, type=(str, int), multiple=True)
@click.option('--propertyFloat', '-pf', required=False, type=(str, float), multiple=True)
@click.option('--update/--replace', is_flag=True, default=True, required=False)
@click.option('--no_progressbar/--enable_progressbar', default=False, is_flag=True, required=False)
@click.pass_context
def add_to_metadata(
        ctx, volumeid, files, data, datapoint, datafile, property, propertyint, propertyfloat, update, no_progressbar):
    now = time.time()

    def get_current_data(data_param):
        if datafile:
            current_data_from_params = json.load(datafile)
        else:
            current_data_from_params = {}

            if data_param:
                current_data_from_params = json.loads(data_param)

            for props in (property, propertyint, propertyfloat):
                if not props:
                    continue

                for prop_name, prop_val in props:
                    current_data_from_params[prop_name] = prop_val

        return current_data_from_params

    current_data = get_current_data(data)

    def filter_internal_data(full_current_data):
        return {key: val for key, val in full_current_data.items() if not key.startswith('@')}

    def compare_data(prev_data, key):
        prev_data_without_internal = filter_internal_data(prev_data) if prev_data else None

        item_current_data = current_data if not datafile else current_data[key]

        return prev_data_without_internal == item_current_data

    def update_data(prev_data, key):
        prev_data = prev_data or {}

        item_current_data = current_data if not datafile else current_data[key]

        prev_data.update(item_current_data)

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

    def rel_path(file_enum):
        def rel_path_if_needed(path):
            if os.path.isabs(path):
                return os.path.relpath(path, repo.data_path)

            return path

        for current_file_path_chunks in file_enum:
            yield [rel_path_if_needed(current_file_path) for current_file_path in current_file_path_chunks]

    def enumerate_json():
        for item_key in current_data.keys():
            yield item_key

    def get_totals():
        if datapoint:
            return len(datapoint)

        if datafile:
            return len(current_data)

        return get_total_files_in_path(files)

    def enumerate_data_points():
        if datapoint:
            return datapoint

        if datafile:
            return enumerate_json()

        return enumerate_paths(files)

    with with_repo(ctx.obj.config, volumeid) as repo:
        validate_repo_data_path(repo, volumeid)

        total_files = get_totals()

        insert_batch_size = max(min(total_files // 20, 2000), 100)  # FIXME: hardcoded

        with tqdm(total=total_files, desc="Adding Metadata", unit=' files', ncols=80, disable=no_progressbar) as bar:
            index = repo.open_index()

            data_enumerator = enumerate_data_points()

            for file_rel_path_chunk in rel_path(chunks(data_enumerator, insert_batch_size)):
                data_batch = []

                entries = {}

                for i, prev_json in enumerate(enumerate_function(file_rel_path_chunk)):
                    rel_file_path = file_rel_path_chunk[i]

                    if compare_data(prev_json, rel_file_path):
                        continue

                    blob, json_data, st = update_data(prev_json, rel_file_path)
                    data_batch.append((file_rel_path_chunk[i], json_data))

                    metadata_rel_path = rel_file_path + '.metadata'

                    metadata_tree_path = _fs_to_tree_path(metadata_rel_path)

                    entries[metadata_tree_path] = index_entry_from_stat(st, blob.id, 0)

                metadata = repo.metadata
                metadata.add_data(data=data_batch)
                index.set_entries(entries)

                bar.update(len(file_rel_path_chunk))
