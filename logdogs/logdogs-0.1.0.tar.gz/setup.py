from setuptools import setup
try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

setup(
    name="logdogs",
    version="0.1.0",
    author="Xurui Yan",
    author_email="yxr1993@gmail.com",
    description='A daemon to monitor keywords in any log files specified by glob pattern',
    long_description=long_description,
    license="MIT License",
    keywords="log monitor",
    url="https://github.com/yanxurui/logdog",
    package_dir = {'': 'src'},
    py_modules=['logdogs', 'pyconfig'],
    platforms=['Linux'],
    install_requires=[
        'glob2>=0.6',
        'python-daemon>=2.1.2'
    ],
    entry_points={
        'console_scripts': [
            'logdogs=logdogs:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Environment :: Console',
        'Topic :: Utilities'
    ]
)
