from setuptools import setup, find_packages

setup(
    name="cfcli",
    description="Cloudflare CLI is a simple command-line interface for cloudflare",
    version='0.0.2',
    url='https://github.com/lucascaro/cloudflare-cli',
    author='Lucas Caro',
    author_email='lucascaro@gmail.com',
    license='MIT',
    classifiers =[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>=3',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    py_modules=['cfcli'],
    install_requires=[
        'Click', 'Cloudflare'
    ],
    entry_points='''
        [console_scripts]
        cfcli=cfcli.cli:cli
    ''',
)