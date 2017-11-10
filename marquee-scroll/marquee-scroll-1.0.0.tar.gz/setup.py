from setuptools import setup, find_packages

def main():
    setup(name='marquee-scroll',
          description='Text scroller',
          use_scm_version={'write_to': 'src/marquee/_version.py'},
          license='GPLv3+',
          author='Michał Góral',
          author_email='dev@mgoral.org',
          url='https://git.mgoral.org/mgoral/marquee',
          platforms=['linux'],
          setup_requires=['setuptools_scm'],

          # https://pypi.python.org/pypi?%3Aaction=list_classifiers
          classifiers=['Development Status :: 5 - Production/Stable',
                       'Environment :: Console',
                       'Intended Audience :: End Users/Desktop',
                       'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
                       'Natural Language :: English',
                       'Operating System :: POSIX',
                       'Programming Language :: Python :: 3 :: Only',
                       'Programming Language :: Python :: 3.5',
                       'Programming Language :: Python :: 3.6',
                       'Topic :: Text Processing',
                       'Topic :: Text Processing :: Filters',
                       'Topic :: Utilities',
                       ],

          packages=find_packages('src'),
          package_dir={'': 'src'},
          entry_points={
              'console_scripts': ['marquee=marquee.app:main'],
          },
    )

if __name__ == '__main__':
    main()
