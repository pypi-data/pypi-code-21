from fabric.api import local, put, run, cd

from .rvenv import RemoteVirtualEnv

__all__ = ['RemoteVirtualEnv', 'run_unit_tests', 'run_script', 'start_script']


def run_unit_tests():
    local("python -m unittest discover -s unittests/ -p '*tests.py'")


def run_script(script_name, venv, module, working_dir):
    run_command('{cmd}',
                create_command(script_name),
                venv,
                module,
                working_dir)


def start_script(script_name, venv, module, working_dir):
    run_command('tmux new-session -d -s {module} "{cmd}"',
                create_command(script_name),
                venv,
                module,
                working_dir)


def run_command(template, cmd, venv, module, working_dir):
    prepare(module, working_dir)

    with cd(working_dir), venv.activate():
        run(template.format(module=module, cmd=cmd))


def create_command(script_name):
    if not script_name.startswith('scripts/'):
        script_name = 'scripts/{}'.format(script_name)
    return 'PYTHONPATH=. python {}'.format(script_name)


def prepare(module, working_dir):
    run_unit_tests()
    put(module, working_dir)
    put('scripts', working_dir)
