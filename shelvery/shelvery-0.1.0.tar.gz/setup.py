from setuptools import setup

setup(name='shelvery', version='0.1.0', author='Base2Services R&D',
      author_email='itsupport@base2services.com',
      url='http://base2services.com',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 3.6',
          'Intended Audience :: System Administrators',
          'Intended Audience :: Information Technology',
          'License :: OSI Approved :: MIT License',
          'Topic :: System :: Archiving :: Backup',
      ],
      keywords='aws backup lambda ebs rds ami',
      packages=['shelvery', 'shelvery_cli', 'shelvery_lambda'],
      install_requires=['boto3', 'python-dateutil'],
      python_requires='>=3.6',
      entry_points={
          'console_scripts': ['shelvery = shelvery_cli.__main__:main'],
      })
