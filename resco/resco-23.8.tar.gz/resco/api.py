from fabric.api import local, put, run, cd

from .rvenv import RemoteVirtualEnv


def run_unit_tests():
    local('python -m unittest discover unittests/')


def run_script(script_name, venv, module, working_dir):
    run_unit_tests()
    with cd(working_dir), venv.activate():
        put(module, '')
        put('scripts', '')
        if not script_name.startswith('scripts/'):
            script_name = 'scripts/{}'.format(script_name)
        run('python {}'.format(script_name))
