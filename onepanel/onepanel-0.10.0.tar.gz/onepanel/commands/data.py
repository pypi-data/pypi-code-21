"""
Data commands
"""
import os
import subprocess
import sys

import click

from onepanel.commands.login import login_required
from onepanel.commands.projects import Project


# Path separator for remote resources. Alternative `PATH_SEP = os.path.sep' is discouraged.
PATH_SEP = '/'


@click.group(help='Data commands group')
@click.pass_context
def data(ctx):
    # Retrieve the project from the local storage and pass it over
    local_project = Project.from_directory(os.getcwd())
    if local_project is None:
        # All job commands require project_uid. Return error before reaching them:
        print('This project is not initialized, type "onepanel init" to initialize this project')
        sys.exit(1)
    else:
        ctx.obj['project'] = local_project


@data.command(
    'download',
    help='Download output for a job. RESOURCE for job output: '
         '"jobs/__JOB_ID__/output" OR "__ACCOUNT_ID__/__PROJECT_ID__/jobs/__JOB_ID__/output".'
)
@click.argument(
    'resource',
    type=click.Path(),
    required=True
)
@click.argument(
    'directory',
    type=click.Path(),
    required=False
)
@click.pass_context
@login_required
def data_download(ctx, resource, directory):

    project = ctx.obj['project']

    # These will be updated from `resource`
    account_uid = project.account_uid
    project_uid = project.project_uid
    job_uid = ''

    #
    # Resource
    #

    dirs = resource.split(PATH_SEP)

    # Dataset
    # onepanel/datasets/<dataset_uid>
    if (dirs[0] == 'onepanel') and (dirs[1] == 'datasets'):

        print('Not implemented')
        return False

    # Job output: Method 1
    # jobs/<job_uid>/output
    elif (dirs[0] == 'jobs') and (len(dirs) == 3):

        # Parse a resource path such as: onepanel/<job id>/output
        try:
            _, job_uid, output_dir = dirs
            assert output_dir == 'output'
        except:
            print('Incorrect RESOURCE')
            return None

    # Job output: Method 2
    # <account_uid>/<project_uid>/jobs/<job_uid>/output
    elif len(dirs) == 5:

        try:
            account_uid, project_uid, jobs_dir, job_uid, output_dir = dirs
            assert (jobs_dir == 'jobs') and (output_dir == 'output')
        except:
            print('Incorrect RESOURCE')
            return None

    else:

        print('Incorrect RESOURCE')
        return None

    #
    # Directory
    #

    if directory is None or directory == '.':
        home = os.getcwd()
    else:
        home = os.path.join(os.getcwd(), directory)

    #
    # Clone
    #

    cwd = os.getcwd()

    cmd = (
            'rm -rf .onepanel_output'   # Cleaning after previous errors to avoid "is not an empty directory" error
            ' && git clone --quiet --no-checkout https://{host}/{account_uid}/{project_uid}-output.git .onepanel_output'
            ' && cd .onepanel_output'
            ' && git config --local core.sparseCheckout true'
            ' && echo \'jobs/{job_uid}/output/*\'> .git/info/sparse-checkout'
            ' && git checkout --quiet  master'
            ' && cp -r jobs/{job_uid}/output/ {dir}'
            ' && cd {cwd}'
            ' && rm -rf .onepanel_output'
        ).format(
            host='git.onepanel.io',
            account_uid=account_uid,
            project_uid=project_uid,
            job_uid=job_uid,
            dir=home,
            cwd=cwd
        )
    p = subprocess.Popen(cmd, shell=True)
    p.wait()

    if p.returncode == 0:
        print('The resource downloaded to: {dir}'.format(dir=home))
        return True
    else:
        print('Unable to download')
        return False
