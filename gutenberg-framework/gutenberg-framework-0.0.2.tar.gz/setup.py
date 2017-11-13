from setuptools import setup

setup(name='gutenberg-framework',
      version='0.0.2',
      description='Simple end-to-end REST API testing framework',
      url='http://github.com/KEOTL/gutenberg',
      author='Kento Lauzon',
      license='GNU GPLv3',
      packages=['gutenberg'],
      install_requires=['simplejson', 'python-dateutil'],
      zip_safe=False)
