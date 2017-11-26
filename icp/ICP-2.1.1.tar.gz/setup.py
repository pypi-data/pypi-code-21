#!/usr/bin/env python

### setup.py

#from distutils.core import setup

from setuptools import setup, find_packages
import sys, os

setup(name='ICP',
      version='2.1.1',
      author='Avinash Kak',
      author_email='kak@purdue.edu',
      maintainer='Avinash Kak',
      maintainer_email='kak@purdue.edu',
      url='https://engineering.purdue.edu/kak/distICP/ICP-2.1.1.html',
      download_url='https://engineering.purdue.edu/kak/distICP/ICP-2.1.1.tar.gz',
      description='A Python module for registering a photo with a database image of the same scene',
      long_description='''

Consult the module API page at

    https://engineering.purdue.edu/kak/distICP/ICP-2.1.1.html

for all information related to this module, including information related to the
latest changes to the code.  The page at the URL shown above lists all of the module
functionality you can invoke in your own code. With regard to the new functionality
added in Version 2.1.0, that page also describes how you can use the ICP algorithm in
a scan mode when working with large images that are synthesized by collecting data
from sensors in motions (as is the case with earth-observing satellites that use
pushbroom cameras and, in some cases, with the images recorded by UAVs).

**Version 2.1.1** fixes a bug that made itself evident when using ICP in the scanning
mode with a non-square array of subimages. 

**Version 2.1.0** incorporates a new ICPImageScanner class that allows the ICP
algorithm to be invoked in a scanning mode for subimage-based ICP registration of
large model and data images.  This version also includes a bugfix needed to make the
module work with the more recent versions of the Pillow library for PIL.  This
version also includes a constructor option for specifying your own font file needed
for displaying the results.

**Version 2.0** is a Python 3.x compliant version of the ICP module.  This version should work with both Python 3.x and Python 2.7.

An application scenario would be the registration of an image recorded by a
UAV-mounted camera flying over a terrain with an image extracted from a GIS
(Geographical Information System) database.

Typical usage syntax for a color or grayscale image when using edge-based
ICP:

::

        import ICP
        icp = ICP.ICP(
                   binary_or_color = "color",
                   corners_or_edges = "edges",
                   auto_select_model_and_data = 1,
                   calculation_image_size = 200,
                   max_num_of_pixels_used_for_icp = 300,
                   pixel_correspondence_dist_threshold = 20,
                   iterations = 24,
                   model_image =  "SydneyOpera.jpg",
                   data_image = "SydneyOpera2.jpg",
                 )
        icp.extract_pixels_from_color_image("model")
        icp.extract_pixels_from_color_image("data")
        icp.icp()
        icp.display_images_used_for_edge_based_icp()
        icp.display_results_as_movie()
        icp.cleanup_directory()


Here is example syntax for using corner-pixels based ICP:

::

        import ICP
        icp = ICP.ICP(
                   binary_or_color = "color",
                   corners_or_edges = "corners",
                   calculation_image_size = 200,
                   image_polarity = -1,
                   smoothing_low_medium_or_high = "medium",
                   corner_detection_threshold = 0.2,
                   pixel_correspondence_dist_threshold = 40,
                   auto_select_model_and_data = 1,
                   max_num_of_pixels_used_for_icp = 100,
                   iterations = 16,
                   model_image =  "textured.jpg",
                   data_image = "textured2.jpg",
                )
        icp.extract_pixels_from_color_image("model")
        icp.extract_pixels_from_color_image("data")
        icp.icp()
        icp.display_images_used_for_corner_based_icp()
        icp.display_results_as_movie()
        icp.cleanup_directory()

Yet another mode for using the module is for registering binary images. The
Examples directory contains six canned scripts that illustrate the
different ways of using this module.

For the new functionality that was added in Version 2.1.0, see the ExamplesICPImageScanner
directory for how to invoke that functionality for first chopping large images
into subimages and then applying ICP separately to each corresponding pair of
subimages.

          ''',

      license='Python Software Foundation License',
      keywords='image processing, image registration, computer vision',
      platforms='All platforms',
      classifiers=['Topic :: Scientific/Engineering :: Image Recognition', 'Programming Language :: Python :: 2.7', 'Programming Language :: Python :: 3.5'],
      packages=['ICP','ICPImageScanner']
)
