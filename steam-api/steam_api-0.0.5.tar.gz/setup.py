from setuptools import setup, find_packages

setup(name='steam_api',
      version='0.0.5',
      description='simple python wrapper for Steam web API',
      packages=find_packages(exclude=['tests', 'docs']),
      keywords='steam api',
      install_requires=[
          'certifi==2017.7.27.1',
          'chardet==3.0.4',
          'future==0.16.0',
          'idna==2.6',
          'pluggy==0.5.2',
          'py==1.4.34',
          'requests==2.18.4',
          'six==1.11.0',
          'urllib3==1.22',
      ],
      classifiers=[
          'Development Status :: 3 - Alpha',

          'Intended Audience :: Developers',
          'Topic :: Software Development :: Build Tools',

          'License :: OSI Approved :: MIT License',

          # Specify the Python versions you support here. In particular, ensure
          # that you indicate whether you support Python 2, Python 3 or both.
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
      ],
      author='edmundluk',
      author_email='edmundluk3@gmail.com',
      license='MIT',
      zip_safe=False)
