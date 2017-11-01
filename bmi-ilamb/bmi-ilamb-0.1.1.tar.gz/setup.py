from setuptools import setup, find_packages


execfile('./bmi_ilamb/version.py')
setup(name='bmi-ilamb',
      version=__version__,
      description='BMI for ILAMB',
      long_description=open('README.md').read(),
      url='https://github.com/permamodel/bmi-ilamb',
      license='MIT',
      author='Mark Piper',
      author_email='mark.piper@colorado.edu',
      packages=find_packages(exclude=['*.tests']),
      package_data={'': ['data/*']},
      install_requires=['pyyaml', 'basic-modeling-interface'],
      keywords='CSDMS BMI ILAMB model benchmark',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
      ],
)
