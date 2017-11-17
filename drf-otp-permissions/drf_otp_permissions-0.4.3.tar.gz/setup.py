from setuptools import setup

setup(name='drf_otp_permissions',
      version='0.4.3',
      description='OTP permissions for Django REST Framework',
      keywords='django rest framework drf otp permission',
      url='https://gitlab.com/taelimoh/drf-otp-permissions',
      author='Tae-lim Oh',
      author_email='taelimoh@gmail.com',
      license='MIT',
      packages=['drf_otp_permissions'],
      install_requires=[
          'django==1.9.8',
          'djangorestframework==3.6.4',
          'python-keyczar==0.716',
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)