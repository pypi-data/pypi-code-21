# -*- coding:utf-8 -*-

from setuptools import setup, find_packages


def long_description():

    def read_markdown(file):
        try:
            from pypandoc import convert
            return convert(file, 'rst')
        except (ImportError, OSError):
            with open(file) as readme:
                return readme.read()

    readme = read_markdown('README.md')
    with open('HISTORY.rst') as history_file:
        history = history_file.read()
        return '\n\n'.join((readme, history))


setup(name='logxstract',
      version='0.0.1',
      description='Library for extracting xml from logs to output file.',
      long_description=long_description(),
      author="Nuncjo",
      author_email='zoreander@gmail.com',
      url='https://github.com/nuncjo/logxstract',
      packages=find_packages(include=['logxstract']),
      install_requires=['lxml'],
      license="MIT license",
      zip_safe=False,
      keywords='xml extractor, xml logs, extract from logs, logs filtering, log',
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 2.7',
      ],
      entry_points={
          'console_scripts': [
              'logxstract = logxstract.__main__:main'
          ]
      })
