from setuptools import setup

setup(name='drf_otp_requests',
      version='0.3.1',
      description='requests for API with OTP permission',
      keywords='django rest framework drf otp permission requests',
      url='https://gitlab.com/taelimoh/drf-otp-requests',
      author='Tae-lim Oh',
      author_email='taelimoh@gmail.com',
      license='MIT',
      packages=['drf_otp_requests'],
      install_requires=[
            'requests==2.18.4',
            'requests-toolbelt==0.8.0',
            'drf-otp-permissions==0.4.2',
            'drf-logged-validation-error==0.1'
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)