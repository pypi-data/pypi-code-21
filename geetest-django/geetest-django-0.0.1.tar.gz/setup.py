from setuptools import setup


install_requires = (
    "geetest",
)


setup(
    name='geetest-django',
    version='0.0.1',
    packages=['geetest_django'],
    url='https://github.com/winkidney/geetest-django',
    license='MIT',
    author='winkidney',
    install_requires=install_requires,
    author_email='winkidney@gmail.com',
    description='A session-based geetest api implementation'
)
