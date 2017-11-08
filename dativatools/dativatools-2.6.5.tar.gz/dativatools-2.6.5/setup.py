from setuptools import setup

setup(name='dativatools',
      version='2.6.5',
      description='A client library for integrating client data from source into client database',
      url='https://github.com/dativa4data/dativatools',
      author='Dativa Limited',
      author_email='tools@dativa.com',
      license='MIT',
      zip_safe=False,
      install_requires=[
          'boto<=2.48.0',
          'boto3<=1.4.4',
          'botocore<=1.5.80',
          'chardet<=3.0.4',
          'pandas<=0.18.0',
          'paramiko<=2.2.1',
          'patool<=1.12',
          'psycopg2<=2.7.3.1',
          'pexpect<=4.2.1'
      ],
      classifiers=['Development Status :: 4 - Beta',  # 5 - Production/Stable
                   'Intended Audience :: Developers',
                   'Topic :: Scientific/Engineering',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.2',
                   'Programming Language :: Python :: 3.3',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6'],
      keywords='dativa',)
