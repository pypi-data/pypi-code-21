from setuptools import setup, find_packages
import requests

version = '0.1.5'


def readme():
    r = requests.post(url='http://c.docverter.com/convert',
                      data={'to': 'rst', 'from': 'markdown'},
                      files={'input_files[]': open('README.md', 'rb')})
    if r.ok:
        return r.content.encode()
    else:
        return 'error converting readme'


setup(name='py-piwik',
      version=version,
      description='Piwik API Client',
      # long_description=readme(),
      classifiers=[
          'Intended Audience :: Developers',
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Programming Language :: Python :: 3 :: Only'
      ],
      keywords='piwik api client',
      url='https://github.com/adminhead-tech/pypiwik',
      author='AdminHead',
      author_email='code@adminhead.tech',
      license='MIT',
      packages=find_packages(exclude=['contrib', 'docs', 'tests']),
      install_requires=[
          'requests'
      ],
      extras_require={
          'dev': ['pytest', 'responses']
      },
      python_requires='>=3',
      include_package_data=True,
      zip_safe=False)
