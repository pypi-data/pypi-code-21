from distutils.core import setup
setup(
  name = 'talentcircles',
  packages = ['talentcircles'],
  version = '0.4.1',
  description = 'A module for accessing the TalentCircles REST API',
  author = 'Tom Clowers',
  author_email = 'tom@talentcircles.com',
  url = 'https://github.com/talentcircles/python_sdk',
  download_url = 'https://github.com/talentcircles/python_sdk/archive/0.4.1.tar.gz',
  keywords = ['hr', 'talent', 'jobs'],
  license='MIT',
  classifiers = [
    'Development Status :: 5 - Production/Stable',

    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',

    'License :: OSI Approved :: MIT License',

    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7'
  ],
  install_requires=[
    'requests',
    'datetime',
    'urllib3'
  ],
  py_modules=["talentcircles"]
)