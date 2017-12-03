from distutils.core import setup

# note to self: see http://peterdowns.com/posts/first-time-with-pypi.html for setup
from setuptools import find_packages

setup(
    name='easingutilities',
    packages=['easingutilities', 'easingutilities/easing', 'easingutilities/easingcontroller',
              'easingutilities/exceptions'],  # this must be the same as the name above
    version='1.0',
    description='A controller for controlling Dynamixel motors with easing algorithms through pypot',
    author='Graunephar',
    author_email='daniel@graungaard.com',
    url='https://github.com/Robot-Boys/Easing-utilities',  # use the URL to the github repo
    download_url='https://github.com/Robot-Boys/Easing-utilities/archive/1.0.tar.gz',  # Link created via github tag
    keywords=['Dynamixel', 'Easing', 'Motor'],
    classifiers=[
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
        'Programming Language :: Python :: 3.4',
    ])
