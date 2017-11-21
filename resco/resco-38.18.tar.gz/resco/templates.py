readme = """
# {{ module }}

This is an empty readme.
"""

fabfile = """
from fabric.api import local, cd, env
from resco import api

env.module_name = '{{ module }}'
env.working_dir = '{{ module }}-wd'
env.venv = api.RemoteVirtualEnv('{{ module }}-env',
                            dependencies=['requirements/remote.txt',
                                          'requirements/all.txt'])

run_unit_tests = api.run_unit_tests
run_script = api.run_script
update_venv = api.update_venv
ls = api.ls
fetch = api.fetch
copy_data = api.copy_data
initialize_remote = api.initialize_remote
update_venv = api.update_venv


def install_local():
    local('pip install -r requirements/all.txt -r requirements/local.txt')
"""
