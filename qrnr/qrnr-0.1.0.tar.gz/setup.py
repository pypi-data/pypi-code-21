from distutils.core import setup
setup(
    name='qrnr',
    version='0.1.0',
    packages=['qrnr'],
    author='Sho Mizoe',
    author_email='sho.mizoe@gmail.com',
    url='https://github.com/smizoe/qrnr',
    python_requires='>=3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Database :: Database Engines/Servers',
    ],
    entry_points={
        'console_scripts': [
            'qrnr = qrnr.__main__:main'
        ]
    },
    install_requires=[
        'sqlalchemy'
    ],
    license='MIT License',
    description="""a tool to issue queries to databases in CLI using sqlalchemy."""
)
