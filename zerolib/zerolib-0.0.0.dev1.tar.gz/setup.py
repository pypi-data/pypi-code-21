from setuptools import setup

setup(name='zerolib',
      version='0.0.0.dev1',
      description='A minimalist ZeroNet protocol library',
      url='https://github.com/MuxZeroNet/zerolib',
      author='MuxZeroNet and zerolib contributors',
      author_email='muxzeronet@users.noreply.github.com',
      license='GPLv3+',
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',

          'Intended Audience :: Developers',
          'Topic :: Software Development :: Libraries',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

          'Programming Language :: Python :: 3 :: Only',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
      ],
      keywords='development bitcoin zeronet',
      packages=['zerolib'],
      python_requires='>=3',
)
