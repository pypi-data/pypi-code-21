from setuptools import setup

name = 'pywow'
lib_filename = 'wow'
version = '1.0'

desc = 'Python WoW API Wrapper'
long_desc = open('README.md', 'r', encoding='utf-8').read()
github = 'https://github.com/mostm/pywow'
author = 'mostm'
author_email = 'mostm@endcape.ru'
license_type = 'MIT'
classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
]
keywords = 'wow world of warcraft world_of_warcraft python api wrapper lib'
install_requires = ['requests>=2.15,<3','Pillow>=4,<5']


setup(
    name=name,
    version=version,
    description=desc,
    long_description=long_desc,
    url=github,
    license=license_type,
    author=author,
    author_email=author_email,
    classifiers=classifiers,
    keywords=keywords,
    install_requires=install_requires,
    packages=[lib_filename]
)
