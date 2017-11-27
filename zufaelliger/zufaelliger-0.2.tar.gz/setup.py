from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='zufaelliger',
      version='0.2',
      description='Der komischsten Witz im Welt',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing :: Linguistic',
      ],
      keywords='komisch Witz Comedy Zirkus',
      url='https://github.com/alexbmp/zufaelliger',
      author='Fliegender Kirkus',
      author_email='sm.alex.choi@gmail.com',
      license='MIT',
      packages=['zufaelliger'],
      install_requires=[
        'bitarray', 'markdown',
      ],
      include_package_data=True, # files to be copied to site-packages
      scripts=['bin/zufaelliger-joke', 'scripts/zufaelliger-bash'],
      test_suite='nose.collector',
      tests_require=['nose'],
      entry_points = {
          'console_scripts': ['funniest-joke=zufaelliger.command_line:main'],
      },
      zip_safe=False)
 
