from distutils.core import setup
setup(
    name='strupy',
    version='0.5.5',
    description='structural engineering design python package',
    long_description = open("README.txt").read(),
    author='Lukasz Laba',
    author_email='lukaszlab@o2.pl',
    url='https://bitbucket.org/struthonteam/strupy/wiki/Home',
    packages=['strupy', 'strupy.concrete', 'strupy.steel', 'strupy.x_graphic', 'strupy.steel.database_sections'],
    package_data = {'': ['*.xml']},
    license = 'GNU General Public License (GPL)',
    keywords = 'civil engineering ,structural engineering, concrete structures, steel structures',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        ],    
    )
