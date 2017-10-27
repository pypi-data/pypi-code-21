from distutils.core import setup
from hbr_client.__version__ import version
setup(
    name = 'hbr_client',
    packages = ['hbr_client'], # this must be the same as the name above
    version = version,
    description = 'Python Library to consume HBR Cloud API',
    author = 'HotBlack Robotics',
    author_email = 'info@hotblackrobotics.com',
    url = 'https://github.com/HotBlackRobotics/hbr_client_python', # use the URL to the github repo
    download_url = 'https://github.com/HotBlackRobotics/hbr_client_python/archive/{}.tar.gz'.format(version), # I'll explain this in a second
    keywords = ['HBR', 'logging'], # arbitrary keywords
    classifiers = [],
    install_requires=['requests']
)
