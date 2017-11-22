from setuptools import setup

setup(name='lawrence',
      version='1.0.0',
      description='Website Mockup Utility',
      url='http://jmroper.com/',
      author='John Roper',
      author_email='john@jmroper.com',
      license='GPL3.0',
      packages=['lawrence'],
      include_package_data=True,
      install_requires=[
          'click',
          'Jinja2',
      ],
      entry_points={
          'console_scripts': [
              'lawrence=lawrence.__init__:cli',
          ],
      },
      python_requires='>=3',
      zip_safe=False)
