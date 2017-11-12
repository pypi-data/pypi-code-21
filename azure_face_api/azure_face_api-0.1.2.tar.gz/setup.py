"""
API wrapper for azure face api
"""
from setuptools import setup

dependencies = ['requests']

setup(
    name='azure_face_api',
    version='0.1.2',
    url='https://github.com/PandaWhoCodes/azure_face_api',
    license='MIT',
    author='Thomas Ashish Cherian',
    author_email='ufoundashish@gmail.com',
    description='API wrapper for azure face api',
    long_description=__doc__,
    packages=['azure_face_api'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
