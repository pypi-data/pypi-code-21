import jinja2

from . import templates
from . import utils


def start_project(name):
    utils.create_tree({
        '.': ['README.md', 'fabfile.py'],
        name: '__init__.py',
        'unittests': {},
        'scripts': {
            'behaviour': {},
            'analysis': {},
            'theory': {},
            'figures': {},
            'tools': {},
        },
        'target': {
            'results': {
                'behaviour': {},
                'analysis': {},
                'theory': {},
                'figures': {},
            },
        },
        'requirements': ['all.txt', 'remote.txt', 'local.txt'],
    })
    with open('README.md', 'w') as f:
        f.write(jinja2.Template(templates.readme).render(module=name))

    with open('fabfile.py', 'w') as f:
        f.write(jinja2.Template(templates.fabfile).render())

    with open('requirements/all.txt', 'w') as f:
        f.write('resco')
