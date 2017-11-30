from distutils.core import setup
setup(
    name = "valection",
    packages = ["valection"],
    version = "1.0.1",
    description = "Sampler for verification",
    author = "Chris Cooper",
    author_email = "paul.boutros@oicr.on.ca",
    url = "http://oicr.on.ca/",
    # download_url = "http://chardet.feedparser.org/download/python3-chardet-1.0.1.tgz",
    keywords = ["verification", "selection", "sampling"],
    classifiers = [
         "Programming Language :: Python",
         "Programming Language :: Python :: 3",
         "Intended Audience :: Science/Research",
         "License :: OSI Approved :: GNU General Public License (GPL)",
         ],
    long_description = """\
Valection - Sampler for verification (version 1.0.1)
--------------------------------------------------

This is a binding for the valection C library and supports C version 1.0.0.

Valection can be used in various ways to sample the outputs of competing algorithims or
parameterizations, and fairly assess their performance against each other.

This software requires the valection library (http://labs.oicr.on.ca/boutros-lab/software/valection).

"""
)
