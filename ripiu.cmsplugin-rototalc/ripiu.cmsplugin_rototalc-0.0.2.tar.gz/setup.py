from setuptools import setup

from ripiu.cmsplugin_rototalc import __version__

setup(
    name='ripiu.cmsplugin_rototalc',
    version=__version__,
    url='https://github.com/ripiu/ripiu.cmsplugin_rototalc',
    license='BSD-new',
    description='A plugin for Django-CMS to display galleries, '
                'based on Slick carousel',
    long_description=open('README.rst').read(),
    author='matteo vezzola',
    author_email='matteo@studioripiu.it',
    # find_packages doesn't like implicit namespace packages:
    # https://stackoverflow.com/questions/27047443/
    # packages=find_packages(),
    packages=['ripiu.cmsplugin_rototalc'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    # TODO: check requirements
    install_requires=[
        "Django >= 1.8",

        "django-cms >= 3.1",
        "django-sekizai >= 0.4.2",
        "django-appconf",
    ],
    python_requires='>=3.3',
    include_package_data=True,
    zip_safe=False,
)
