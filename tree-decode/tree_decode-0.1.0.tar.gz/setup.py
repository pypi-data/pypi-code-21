from setuptools import setup
from tree_decode import __version__ as decode_version

SHORT_DESCRIPTION = "Scikit-Learn Decision Tree Decoder"

LONG_DESCRIPTION = """
tree_decode is a library that helps to remove the black-box
surrounding decision trees from scikit-learn. Such functionality
makes it easier to understand how trees work and more importantly,
diagnose their issues when they produce unexpected results.
"""

GITHUB_URL = "https://github.com/gfyoung/tree-decode"
BUGTRACK_URL = GITHUB_URL + "/issues"

setup(
    name="tree_decode",
    version=decode_version,
    packages=["tree_decode",
              "tree_decode.tests"],
    package_data={"tree_decode.tests": ["models/*.pickle"]},
    include_package_data=True,
    license="MIT License",
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    download_url=GITHUB_URL,
    url=GITHUB_URL,
    author="G. Young",
    bugtrack_url=BUGTRACK_URL,
    keywords="python scikit-learn decision "
             "trees machine learning black box",
    install_requires=["scikit-learn >= 0.17"],
    setup_requires=["scikit-learn >= 0.17",
                    "numpy >= 1.6.1",
                    "scipy >= 0.9"],
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Natural Language :: English",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering :: Artificial Intelligence"
    ]
)
