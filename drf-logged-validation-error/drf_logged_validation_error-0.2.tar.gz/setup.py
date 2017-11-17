from setuptools import setup

setup(name='drf_logged_validation_error',
      version='0.2',
      description='Raise validation with log in Django REST Framework API',
      keywords='django rest framework log validation error',
      url='https://gitlab.com/taelimoh/drf_logged_validation_error',
      author='Tae-lim Oh',
      author_email='taelimoh@gmail.com',
      license='MIT',
      packages=['drf_logged_validation_error'],
      install_requires=[
          'django==1.9.8',
          'djangorestframework==3.6.4',
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)