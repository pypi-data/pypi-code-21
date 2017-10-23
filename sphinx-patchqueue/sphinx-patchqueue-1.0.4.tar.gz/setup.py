from distutils.core import setup

setup(
    name='sphinx-patchqueue',
    version='1.0.4',
    packages = ['patchqueue'],
    package_data = {'patchqueue': ['static/*']},
    url='https://bitbucket.org/masklinn/sphinx-patchqueue',
    license='BSD',
    author='Xavier Morel',
    author_email='xavier.morel@masklinn.net',
    install_requires=['sphinx', 'unidiff'],
    description="Sphinx extension for embedding sequences of file alterations",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Sphinx :: Extension',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Documentation',
    ],
)
