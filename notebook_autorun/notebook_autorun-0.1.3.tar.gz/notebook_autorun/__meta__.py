
__name__ = 'notebook_autorun'
name_url = __name__.replace('_', '-')

__packages__ = [__name__]
__version__ = '0.1.3'
__description__ = 'Auto run certain cells upon notebook start - if trusted'
__author__ = 'oscar6echo'
__author_email__ = 'olivier.borderies@gmail.com'
__url__ = 'https://github.com/oscar6echo/{}'.format(name_url)
__download_url__ = 'https://github.com/oscar6echo/{}/tarball/{}'.format(name_url,
                                                                        __version__)
__keywords__ = ['python', 'display', 'javascript']
__license__ = 'MIT'
__classifiers__ = ['Development Status :: 4 - Beta',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6'
                   ]
__include_package_data__ = True
__package_data__ = {
    'templates':
    ['templates/getCellsFromComment.js',
     'templates/getCellsFromMetadata.js',
     'templates/getCellsFromString.js',
     'templates/notice_short.md',
     'templates/notice_long.md',
     'templates/notice_safe.txt'
     ]
}
