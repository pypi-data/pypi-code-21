from setuptools import setup


setup(name='cookietransfer',
      version='0.1.0',
      py_modules=['cookietransfer'],
      author='Terry Lim',
      url='https://github.com/terry-lim/cookietransfer',
      description="helps cookie transfer between requests "
                  "session and selenium browser instance with ease",
      install_requires=[
          'requests>=2.18.1',
          'selenium>=3.7.0',
      ],
      license='MIT',
      keywords=['cookie', 'session', 'selenium',
                'requests', 'chrome', 'firefox']
      )
