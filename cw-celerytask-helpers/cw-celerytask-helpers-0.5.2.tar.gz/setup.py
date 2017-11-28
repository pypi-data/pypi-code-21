from setuptools import setup, find_packages

from cw_celerytask_helpers import __pkginfo__ as pkginfo

setup(
    name=pkginfo.distname,
    version=pkginfo.version,
    description=pkginfo.description,
    author=pkginfo.author,
    author_email=pkginfo.author_email,
    license=pkginfo.license,
    classifiers=pkginfo.classifiers,
    packages=find_packages('.'),
    install_requires=["{0} {1}".format(d, v and v or "").strip()
                      for d, v in pkginfo.__depends__.items()],
)
