

from setuptools import setup, find_packages


setup(name='SocialKit',
    version='0.5.5',
    description='a socialkit libs',
    url='http://github.com/',
    author='Froy',
    author_email='no_email@mail.web.com',
    license='MIT',
    zip_safe=False,
    packages=find_packages(),
    install_requires=['pyquery','mroylib-min','qtornado','selenium','termcolor'],

)
