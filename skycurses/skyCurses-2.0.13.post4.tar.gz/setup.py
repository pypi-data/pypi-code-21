from setuptools import setup

setup(
        name='skyCurses',
        version='2.0.13-4',
        description='Unofficial curses client for the SkyChat',
        url='http://git.beerstorm.info/Beerstorm/SkyCurses',
        author='Beerstorm',
        author_email='beerstorm.emberbeard@gmail.com',
        license='GPLv3',
        packages=['skyCurses'],
        install_requires=[
            'pafy',
            'redskyAPI>=1.0.9',
            'winCurses>=0.2.0-4',
            'simpleaudio',
            ],
        entry_points = {
            'console_scripts' : [
                'skyCurses = skyCurses.skyCurses:main',
                ],
            },
        package_data = {
            'skyCurses' : [
                'sounds/*.wav',
                'alias.json',
                ],
            },
        zip_safe=False,
        )
