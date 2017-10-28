from distutils.core import setup

setup(
    name='page-block',
    version='0.0.1',
    packages=['page_block', 'page_block.migrations', 'page_block.templatetags'],
    url='https://bitbucket.org/olcms/page-block',
    license='Apache 2.0',
    author='Jacek Bzdak',
    author_email='jacek@askesis.pl',
    description='Translatable page blocks that can be edited through admin'
)
