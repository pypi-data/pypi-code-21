import os
import platform
from datetime import datetime

from envparse import env
import yaml
from pip import get_installed_distributions


def version(_name, _comment=True, **kwargs):
    label_list = [
        '{}="{}"'.format(str(label), str(value))
        for label, value in kwargs.items() if value]
    if not label_list:
        return None
    labels = '{' + ','.join(label_list) + '}'

    comments = []
    if _comment:
        comments = [
            '# HELP version_{} version info.'.format(_name),
            '# TYPE version_{} counter'.format(_name),
        ]
    return '\n'.join(comments + ['version_{}{} 1'.format(_name, labels)])


def os_package_list():
    versions = ''
    with open(os.environ.get('VERSIONS_OS_PACKAGE_PATH', '/var/local/os-package-versions.yaml'), 'r') as f:  # noqa
        versions = yaml.load(f)
    return versions


def get_distribution():
    try:
        distribution = platform.linux_distribution()
        if distribution == ('', '', ''):
            raise Exception
    except Exception:
        env.read_envfile('/etc/os-release')
        distribution = (env('NAME'), env('VERSION_ID'), env('ID'))

    distro_id = distribution[2] if distribution[2] else distribution[0]
    return {
        'distro_name': distribution[0].replace('_', ' ').capitalize(),
        'distro_version': distribution[1],
        'distro_id': str(distro_id).lower().replace(' ', '-'),
    }


def generate_versions(**application_labels):
    response = '\n'.join(filter(None, [
        version('application', **application_labels),
        version('platform', name=platform.system(), achitecture=platform.architecture()[0],type=platform.machine(), system=platform.release(), **get_distribution()),  # noqa
        version('python', version=platform.python_version(), date=datetime.strptime(platform.python_build()[1], '%b %d %Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S'), compiler=platform.python_compiler(), implementation=platform.python_implementation()),  # noqa
    ] + [version('package', group="os", name=package[0], version=package[1], _comment=key == 0) for key, package in enumerate(os_package_list().items())]  # noqa
      + [version('package', group="python", name=str(package.project_name).lower(), version=package._version, _comment=False) for package in get_installed_distributions(local_only=True)]  # noqa
    )) + '\n'
    return response.encode('utf-8')
