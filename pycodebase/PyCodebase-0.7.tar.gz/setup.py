from setuptools import setup


try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst').decode('utf-8')
except (ImportError, OSError):
    long_description = open('README.md', 'rb').read().decode('utf-8')


setup(
    name='PyCodebase',
    version='0.7',
    description='A client for the Codebase API.',
    long_description=long_description,
    author='David Buxton',
    author_email='david@gasmark6.com',
    url='https://github.com/davidwtbuxton/pycodebase',
    license='MIT',
    package_dir={'': 'src'},
    packages=['codebase'],
    install_requires=['notrequests'],
)
