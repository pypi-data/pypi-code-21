# coding=utf-8
import os
import errno
import six

from contextlib import closing
import click
from mali_commands.legit.dulwich.errors import NotGitRepository

from mali_commands.data_volume_config import DataVolumeConfig
from .repo import MlRepo
from mali_commands.config import Config


def default_data_volume_path(volume_id):
    return os.path.join(os.path.expanduser('~'), '.MissingLinkAI', 'data_volumes', str(volume_id))


def create_data_volume(volume_id, data_path, linked, display_name, description):
    path = default_data_volume_path(volume_id)

    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    config = DataVolumeConfig(path)
    config.update_and_save(
        {
            'general': {
                'id': volume_id,
                'embedded': not linked,
                'datapath': data_path,
                'display_name': display_name,
                'description': description
            }
        }
    )

    return config


def with_repo(config, volume_id, read_only=False):
    repo_root = default_data_volume_path(volume_id)

    try:
        return closing(MlRepo(config, repo_root, read_only=read_only))
    except NotGitRepository:
        msg = 'Data volume {0} was not mapped on this machine, you should call "mali data map {0} --dataPath [root path of data]" in order to work with the volume locally'.format(volume_id)
        click.echo(msg, err=True)
        exit(1)


def validate_repo_data_path(repo, volume_id):
    if not repo.data_path:
        msg = "Data Volume {volume_id} is not mapped to a local folder,\n" \
              "the data root is needed in order to add data to the data volume.\n" \
              "You can run:\n" \
              "mali data get {volume_id} --dataPath <data root folder>".format(volume_id=volume_id)
        click.echo(msg.strip(), err=True)
        exit(1)
