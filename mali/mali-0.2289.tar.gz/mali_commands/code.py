# -*- coding: utf8 -*-
import click
from pip.exceptions import BadCommand
from six.moves.urllib import parse

from .utilities import source_tracking


@click.group('code', help='Repository tracking allows you to quickly see, compare and clone snapshots, including'
                          'unpushed, uncommited and unstaged files of your source code for every experiment.'
                          'In order to use this feature, you must first create setup tracking repository - empty git repository'
                          'in the same organization as your tracked (source) repository, and then call "track"'
                          'This feature relays on the same git authentication mechanism as your source repository'
                          'So please make sure that the ssh key used for fetching your git code has fetch/push permissions'
                          'on the tracking repository')
def code_commands():
    pass


@code_commands.command('track', help='Sets up tracking for given source repository. When setting up tracking from mali, both source and target repositories must sit under the same organization. For more information please refer to our documentation.')
@click.option('--org', required=True, help="Organization/Workspace. Repository tracking is available to all users that have permission to access the Organization/Workspace")
@click.option('--source-repository', required=False is None, default=None, help='Source repository url. Defaults to the first remote of the repository of the current path')
@click.option('--tracking-repository', required=True,
              help='Target repository. When setting up tracking using mali, this repository must be under the same organization as teh source repository (i.e. if the source repo is https://github.com/my_org/my_repo, the tracking repository must be in the https://github.com/my_org organization')
@click.pass_context
def track_add(ctx, org, source, target):
    if source is None:
        source = source_tracking.get_remote_url()

    def validate_params():
        if source is None:
            raise BadCommand("Couldn't determinate the remote origin of the current directory, please provide --source-repository url")
        if source_tracking.remote_url_obj(source) is None:
            raise BadCommand("Source repository: {} is invalid")
        if source_tracking.remote_url_obj(target) is None:
            raise BadCommand("Target repository: {} is invalid")
        if not source_tracking.validate_remote_urls_org(source, target):
            raise BadCommand(" The tracking repository must belong to the same organization as the source ({})".format(source_tracking.get_org_from_remote_url(source)))

    validate_params()

    normalized_src = parse.quote(source_tracking.__remote_to_template(source), safe='')
    data = {
        'target': target
    }
    target_url = '{org}/code/track/{src_repo}'.format(org=org, src_repo=normalized_src)
    # result = ctx.obj.handle_api(ctx.obj, requests.post, target_url , data)
    from pprint import pprint
    pprint(target_url)
    pprint(data)
    # output_result(ctx, result, ['ok'])
