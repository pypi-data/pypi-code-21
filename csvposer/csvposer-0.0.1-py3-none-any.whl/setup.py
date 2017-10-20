#-- csvposer.setup

from copy import deepcopy
#----------------------------------------------------------------------------------------------#

kwargs = dict(
    name            = 'csvposer',
    packages        = ['csvposer'],
    version         = '0.0.1',
    description     = __doc__,
    license         = "MIT License",

    url             = 'https://github.com/philipov/csvposer',
    author          = 'Philip Loguinov',
    author_email    = 'philipov@gmail.com',

    zip_safe                = True,
    include_package_data    = True,

    classifiers=[
        'Programming Language :: Python :: 3.6',
    ]
)

test_kwargs = deepcopy( kwargs )
dev_kwargs  = deepcopy( test_kwargs )

__version__ = kwargs['version']


#----------------------------------------------------------------------------------------------#
