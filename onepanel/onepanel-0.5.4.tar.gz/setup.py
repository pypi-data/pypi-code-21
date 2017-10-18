from setuptools import setup

setup(
    name="onepanel",
    version='0.5.4',
    packages = ['onepanel', 'onepanel.commands'],
    install_requires=[
        'requests',
        'click',
        'PTable',
        'configobj'
    ],
    entry_points='''
        [console_scripts]
        onepanel=onepanel.cli:cli
    ''',
)
