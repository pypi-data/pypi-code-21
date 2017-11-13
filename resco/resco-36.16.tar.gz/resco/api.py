from fabric.api import local, put, run, cd, get, env, settings

from .rvenv import RemoteVirtualEnv

__all__ = ['RemoteVirtualEnv', 'run_unit_tests', 'run_script', 'start_script']


def run_unit_tests():
    local("python -m unittest discover -s unittests/ -p '*tests.py'")


def run_script(script_name):
    run_command('{cmd}',
                create_command(script_name),
                env.venv,
                env.module_name,
                env.working_dir)


def start_script(script_name):
    run_command('tmux new-session -d -s {module} "{cmd}"',
                create_command(script_name),
                env.venv,
                env.module_name,
                env.working_dir)


def copy_data():
    put('data', env.working_dir)


def update_venv():
    put('requirements', env.working_dir)
    with cd(env.working_dir):
        env.venv.install()


def create_wd():
    with settings(warn_only=True):
        for name in ['theory', 'analysis', 'behaviour', 'figures']:
            run('mkdir -p {}'
                .format(env.working_dir + '/target/results/' + name))


def initialize_remote():
    create_wd()
    copy_data()
    update_venv()


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


def ls(glob_pattern='*'):
    with cd(env.working_dir):
        run('ls target/{}'.format(glob_pattern))


def fetch(glob_pattern='*'):
    with cd(env.working_dir):
        get(remote_path='target/' + glob_pattern,
            local_path='%(path)s')
