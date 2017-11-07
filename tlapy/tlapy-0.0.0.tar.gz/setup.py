from setuptools import setup


description = (
    'Python tools for working with TLA+ specifications.')
# README = 'README.md'
VERSION_FILE = 'tlapy/_version.py'
MAJOR = 0
MINOR = 0
MICRO = 0
version = '{major}.{minor}.{micro}'.format(
    major=MAJOR, minor=MINOR, micro=MICRO)
s = (
    '# This file was generated from setup.py\n'
    "version = '{version}'\n").format(version=version)
install_requires = [
    'networkx >= 2.0',
    ]


if __name__ == '__main__':
    with open(VERSION_FILE, 'w') as f:
        f.write(s)
    setup(
        name='tlapy',
        version=version,
        description=description,
        # long_description=open(README).read(),
        author='Ioannis Filippidis',
        author_email='jfilippidis@gmail.com',
        url='https://github.com/johnyf/tlapy',
        license='BSD',
        install_requires=install_requires,
        tests_require=['nose'],
        packages=['tlapy'],
        package_dir={'tlapy': 'tlapy'})
