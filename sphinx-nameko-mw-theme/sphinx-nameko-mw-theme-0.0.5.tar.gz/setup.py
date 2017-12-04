from setuptools import setup

setup(
    name='sphinx-nameko-mw-theme',
    version='0.0.5',
    author='penseleit',
    author_email='penseleit@mediaware.com.au',
    description='Sphinx Nameko MW Theme',
    url='https://github.com/penseleit/sphinx-nameko-mw-theme',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Software Development :: Documentation',
    ],
    packages=['sphinx_nameko_mw_theme'],
    install_requires=['sphinx'],
    entry_points = {
        'sphinx_themes': [
            'path = sphinx_nameko_mw_theme:get_html_theme_path',
        ]
    },
    include_package_data=True,
    zip_safe=False
)
