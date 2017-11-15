from setuptools import setup

setup(
    name = 'rtctools',
    version = '0.0.1.dev2',
    author = 'Jack Vreeken',
    description = "Toolbox for control and optimization of water systems",
    long_description = '''Use `rtc-tools <https://pypi.python.org/pypi/rtc-tools/>`_ instead''',
    url = 'https://pypi.python.org/pypi/rtc-tools/',
    license = 'GPL',
    platforms = ['all'],
    install_requires = ["rtc-tools"],
    zip_safe=False
)
