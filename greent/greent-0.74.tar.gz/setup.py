from distutils.core import setup
from pip.req import parse_requirements
install_reqs = parse_requirements("greent/requirements.txt", session="i")
requirements = [str(r.req) for r in install_reqs]
setup(
    name = 'greent',
    packages = [ 'greent' ], # this must be the same as the name above
    package_data={ 'greent' : [
        'greent.conf',
        'greent-stars.conf',
        'rosetta.yml',
        'identifiers.org.json',
        'requirements.txt',
        'jsonld/*',
        'query/*.sparql'
    ]},
    version = '0.74',
    description = 'Green Team BioMedical Data Translator',
    author = 'Steve Cox',
    author_email = 'scox@renci.org',
    install_requires = requirements,
    include_package_data=True,
    url = 'https://github.com/NCATS-Tangerine/greent.git',
    download_url = 'http://github.com/NCATS-Tangerine/greent/archive/0.1.tar.gz',
    keywords = [ 'biomedical', 'environmental', 'exposure', 'clinical' ],
    classifiers = [ ],
)
