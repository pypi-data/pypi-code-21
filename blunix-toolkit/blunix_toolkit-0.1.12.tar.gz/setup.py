from distutils.core import setup

setup(
    name='blunix_toolkit',
    version='0.1.12',
    author='Brian Wiborg',
    author_email='b.wiborg@blunix.org',
    packages=[
        'blunix_toolkit',
        'blunix_toolkit.config',
    ],
    url='http://github.com/blunix/blunix-toolkit',
    license='LICENCE.txt',
    description="Helpers and wrappers for the Blunix engineering team.",
    long_description=open('README.md').read(),
    keywords='tool development',
    python_requires='>=2.7, <=3.0',
    install_requires=[
        'PyGithub >= 1.35',
        'GitPython==2.1.7',
    ],
    scripts=[
        'bin/blunix-config-bash',
        'bin/blunix-config-cat',
        'bin/blunix-config-edit',
        'bin/blunix-gh-repos',
        'bin/blunix-gh-roles',
        'bin/blunix-gh-playbooks',
        'bin/blunix-role-glance',
    ],
)
