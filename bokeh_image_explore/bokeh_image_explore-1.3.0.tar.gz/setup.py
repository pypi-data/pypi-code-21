# (C) Michael Wilber, 2013-2015, UCSD and Cornell Tech.
# All rights reserved. Please see the 'LICENSE.txt' file for details.

from distutils.core import setup

setup(name = 'bokeh_image_explore',
      version = '1.3.0',
      packages = ['bokeh_image_explore'],
      description="Quickly explore large image embeddings with Bokeh",
      author='Michael Wilber',
      author_email='mwilber@mjwilber.org',
      url='http://vision.cornell.edu/se3/projects/concept-embeddings/',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: BSD License',
          'License :: OSI Approved :: zlib/libpng License',
          'Operating System :: MacOS',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Cython',
          'Programming Language :: Python :: 2.7',
          'Topic :: Scientific/Engineering :: Visualization',
      ],
      keywords='bokeh embedding visualization image big-data',

)
