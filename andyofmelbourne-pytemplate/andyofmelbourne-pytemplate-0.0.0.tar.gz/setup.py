from setuptools import setup
import io

import pytemplate

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.md')
license          = read('LICENSE')

setup(name='andyofmelbourne-pytemplate',
      version=pytemplate.__version__,
      description='a simple python template project',
      long_description=long_description,
      url='http://github.com/andyofmelbourne/pytemplate',
      author='Andrew Morgan',
      author_email='andyofmelbourne@gmail.com',
      license=license,
      packages=['pytemplate'],
      zip_safe=False)
