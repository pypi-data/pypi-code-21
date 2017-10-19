from setuptools import setup

setup(name='stem_ladiespixiedust_twitterdemo',
      version='0.2',
      description='Pixiedust demo of the Twitter Sentiment Analysis tutorialsfor the STEM activity wall',
      url='https://github.com/lgellis/STEM-twitter-wall/tree/master/twitterdemo',
      install_requires=['pixiedust'],
      author='David Taieb the genius and slightly hacked by STEM Women',
      author_email='david_taieb@us.ibm.com',
      license='Apache 2.0',
      packages=['pixiedust_twitterdemo'],
      include_package_data=True,
      zip_safe=False)
