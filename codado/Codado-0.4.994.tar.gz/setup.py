from setuptools import setup

from codado import _version


reqs = []
with open('requirements.txt') as f:
    for line in f:
        if line.startswith('#'):
            continue
        reqs.append(line.strip())


setup(
    name = 'Codado',
    packages = ['codado', 'codado.kleinish'],
    version = _version.__version__,
    description = 'A collection of system development utilities',
    author = 'Cory Dodt',
    author_email = 'corydodt@gmail.com',
    url = 'https://github.com/corydodt/Codado',
    keywords = ['twisted', 'utility'],
    classifiers = [],
    scripts = ['bin/urltool', 'bin/jentemplate'],
    install_requires=reqs
)
