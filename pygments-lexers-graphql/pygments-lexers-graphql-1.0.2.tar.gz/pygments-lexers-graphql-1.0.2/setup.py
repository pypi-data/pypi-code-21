import setuptools

def readme():
	'A GraphQL lexer for Pygments.'

setuptools.setup(
    name='pygments-lexers-graphql',
    license='MIT',
    author='Ryan Parman',
    author_email='ryan@ryanparman.com',
    url="https://github.com/skyzyx/pygments.lexers.graphql",
    install_requires=[
        'Pygments >=2.2.0',
    ],
    version='1.0.2',
    description='A GraphQL lexer for Pygments.',
    long_description=readme(),
    keywords='graphql pygments',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
    ],
    entry_points =
    """
    [pygments.lexers]
    graphqllexer=graphqllexer.lexer:GraphqlLexer
    """,
)
