from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='IChemphy',
      version='0.42',
      description='Physics and Chemistry Functions for GSU',
      long_description= readme(),
      classifiers=[
         'Development Status :: 3 - Alpha',
         'Programming Language :: Python :: 3.6',
         'Topic :: Education',
      ],
      keywords='physics chemistry dynamics simulation python projectile pendulum electromagentic trajectory',
      url='https://github.com/Lokesh523s/gsu_package',
      author='Lokesh Sannuthi',
      author_email='lokesh523s@gmail.com',
      license='MIT',
      packages=['IChemPhy'],
      install_requires=[
          'markdown','matplotlib','scipy','numpy','IPython', ],
      include_package_data=True,
      zip_safe=False,	
	test_suite='nose.collector',
    tests_require=['nose'],)

