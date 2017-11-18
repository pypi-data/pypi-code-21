try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='discuss',
    packages=['discuss'],
    version='0.0.0.dev1',
    license="GPL",
    description='',
    author='Biwin John',
    author_email='biwinjohn@gmail.com',
    url='https://github.com/biwin/discuss',
    download_url='https://github.com/biwin/discuss/',
    install_requires=[],
    keywords=['discuss', 'python'],
    classifiers=[
	    'Development Status :: 1 - Planning',
	    'Intended Audience :: Developers',
	    'License :: OSI Approved :: GNU General Public License (GPL)',
	    'Programming Language :: Python :: 2',
	    'Programming Language :: Python :: 2.6',
	    'Programming Language :: Python :: 2.7',
	    'Programming Language :: Python :: 3',
	    'Programming Language :: Python :: 3.2',
	    'Programming Language :: Python :: 3.3',
	    'Programming Language :: Python :: 3.4',
    ],
)
