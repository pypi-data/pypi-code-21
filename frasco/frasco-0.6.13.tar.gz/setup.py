from setuptools import setup, find_packages


setup(
    name='frasco',
    version='0.6.13',
    url='http://github.com/frascoweb/frasco',
    license='MIT',
    author='Maxime Bouroumeau-Fuseau',
    author_email='maxime.bouroumeau@gmail.com',
    description='Build web applications without coding',
    packages=find_packages(),
    package_data={
        'frasco': ['templating/*.html'],
    },
    zip_safe=False,
    platforms='any',
    install_requires=[
        'flask>=0.11',
        'honcho>=0.6',
        'PyYAML>=3.11',
        'blinker>=1.3',
        'jinja-macro-tags',
        'jinja-layout',
        'python-slugify',
        'ago',
        'simplejson',
        'speaklater',
        'requests>=2.3.0'
    ],
    entry_points='''
        [console_scripts]
        frasco=frasco.cli:main
    '''
)
