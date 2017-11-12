from distutils.core import setup

setup(
    name='cobweb_scrapper',
    version='0.1.0',
    packages=['cobweb', 'cobweb.spiders',
              'cobweb.adapters', 'cobweb.link_extractor'],
    url='https://bitbucket.org/pollux_cast0r/cobweb/overview',
    license='',
    author='Alexander Svito',
    author_email='alexandervirk@gmail.com',
    description='A package for easy scrapping', requires=['requests', 'PyYAML', 'pygtrie', 'bs4', 'urllib3']
)
