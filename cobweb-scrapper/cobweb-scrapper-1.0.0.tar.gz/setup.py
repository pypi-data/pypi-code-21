from setuptools import setup

setup(
    name='cobweb-scrapper',
    version='1.0.0',
    packages=['cobweb', 'cobweb.spiders', 'cobweb.bbs', 'cobweb.helpers',
              'cobweb.adapters', 'cobweb.link_extractor'],
    url='',
    license='',
    author='Alexander Svito',
    author_email='alexandervirk@gmail.com',
    entry_points={
        'console_scripts': ['cobweb=cobweb.scripts:main'],
    },
    data_files=[('cobweb/bbs', ['cobweb/bbs/user_agents.txt'])],
    description='A package for easy scrapping', requires=['requests', 'PyYAML', 'pygtrie', 'bs4', 'urllib3', 'Pillow',
                                                          'selenium']
)
