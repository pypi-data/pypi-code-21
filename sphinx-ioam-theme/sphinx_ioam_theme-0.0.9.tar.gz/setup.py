from setuptools import setup

import versioneer

setup(
    name='sphinx_ioam_theme',
    version=versioneer.get_version(),    
    zip_safe=False,
    packages=['sphinx_ioam_theme'],
    package_data={'sphinx_ioam_theme': [
        'theme.conf',
        '*.html',
        'includes/*.html',
        'static/css/*.css',
        'static/js/*.js',
        'static/images/*.*'
    ]},
    include_package_data=True,
    entry_points = {
        'sphinx.html_themes': [
            'sphinx_ioam_theme = sphinx_ioam_theme',
        ]
    },
)
