import os
import shutil
import pkg_resources
import subprocess

import click


@click.command()
def cli():
    """Install configuration files, IPython extensions, Jupyter extensions,
    and JavaScript/CSS assets for using a Docker image with Civis Platform
    Jupyter notebooks.
    """

    # make home areas and dirs
    for dr in [('~', 'work'),
               ('~', '.jupyter', 'custom'),
               ('~', '.ipython', 'profile_default')]:
        try:
            os.makedirs(os.path.expanduser(os.path.join(*dr)))
        except OSError:
            pass

    # enable civisjupyter extension
    for cmd in ['jupyter nbextension install --py civis_jupyter_ext',
                'jupyter nbextension enable --py civis_jupyter_ext']:
        subprocess.check_call(cmd, shell=True)

    # copy code
    def _copy(src, dst):
        src = pkg_resources.resource_filename(__name__, os.path.join(*src))
        dst = os.path.expanduser(os.path.join(*dst))
        shutil.copy(src, dst)
    _copy(('assets', 'jupyter_notebook_config.py'), ('~', '.jupyter'))
    _copy(('assets', 'custom.css'), ('~', '.jupyter', 'custom'))
    _copy(('assets', 'custom.js'), ('~', '.jupyter', 'custom'))
    _copy(('assets', 'ipython_config.py'), ('~', '.ipython', 'profile_default'))
    _copy(('assets', 'civis_client_config.py'), ('~', '.ipython'))
