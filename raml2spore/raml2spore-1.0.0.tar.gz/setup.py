try:
    from setuptools import setup
except ImportError:
    # can't have the entry_points option here.
    from distutils.core import setup

setup(name='raml2spore',
      version='1.0.0',
      author="Ahmed T. Youssef",
      author_email="xmonader@gmail.com",
      description='convert RAML specs to SPORE specs.',
      long_description='Convert RAML specs to SPORE specs.',
      packages=['raml2spore'],
      scripts=['scripts/raml2spore'],
      url="http://github.com/xmonader/raml2spore",
      license='BSD 3-Clause License',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
      ],
      )
