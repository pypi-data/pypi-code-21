from setuptools import setup, find_packages
setup(
    name = 'strpy',
    version = '0.6.4',
    packages = find_packages(),
    description = 'STR python tools for computer vision and machine learning',
    author = 'Jeffrey Byrne',
    author_email = 'jeffrey.byrne@stresearch.com',
    url = 'https://github.com/stresearch/strpy',
    download_url = 'https://github.com/stresearch/strpy/archive/0.6.4.tar.gz', 
    install_requires=[
        "opencv-python",
        "numpy",  
        "scipy",
        "scikit-learn",
        "matplotlib",    
        "dill",
        "ipython",
        "h5py", 
    ],
    keywords = ['STR', 'vision', 'learning', 'janus'], 
    classifiers = [],
)

# 0.6.4 DIRTY

# Creating a pypi package
# 
# git commit -am "message"
# git push
# git tag 0.6.3 -m "strpy-0.6.3"
# git push --tags origin master
# edit setup.py
#
# to delete a tag
#   git tag -d x.y
#   git push origin :refs/tags/x.y
#
# create ~/.pypirc following https://packaging.python.org/guides/migrating-to-pypi-org/#uploading
# python setup.py register -r testpypi
# python setup.py sdist upload -r testpypi
#
# python setup.py register -r pypi
# python setup.py sdist upload -r pypi

