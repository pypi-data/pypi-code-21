from distutils.core import setup

setup(
    name='sc2challenge',
    packages=['sc2challenge'],
    version='0.9.9108',
    description='Base Terminus7 Starcraft II agent for sending metrics',
    author='Luis Mesas',
    author_email='luismesas@gmail.com',
    url='https://terminus7.com',
    download_url='https://terminus7.com',
    keywords=['sc2','terminus7'],
    classifiers=[],
    install_requires=[
        'pysc2',
        'mixpanel'
    ]
)
