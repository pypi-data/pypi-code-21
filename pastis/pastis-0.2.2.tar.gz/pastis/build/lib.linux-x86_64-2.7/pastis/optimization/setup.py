from os.path import join
import os
import numpy as np


def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration

    config = Configuration('optimization', parent_package, top_path)

    # Counts module
    # XXX is this useful ?
    counts_sources = ['counts_.cpp',
                      join("counts.cpp"),
                      ]
    counts_depends = [join(".", 'counts.hpp')]

    config.add_extension('counts_',
                         sources=counts_sources,
                         include_dirs=[np.get_include(),
                                       os.path.expanduser("~/include/coin"),
                                       ],
                         depends=counts_depends,
                         libraries=["blas", "lapack", "gfortran",
                                    "pthread", "gfortranbegin", 'm', "gcc_s",
                                    "dl",
                                    ],
                         library_dirs=[os.path.expanduser('~/.local/lib')],
                         language='c++'
                         )
    optimization_sources = ['counts_.cpp',
                            join("counts.cpp"),
                            "optimization.cpp", "optimization_.cpp",
                            "poisson_model.cpp",
                            "model.cpp",
                            "mds.cpp",
                            "negative_binomial_model.cpp",
                            ]
    optimization_depends = [join(".", 'counts.hpp'),
                            "model.hpp",
                            "mds.hpp",
                            join(".", "optimization.hpp"),
                            join(".", "poisson_model.hpp"),
                            join(".", "negative_binomial_model.hpp"),]

    config.add_extension('optimization_',
                         sources=optimization_sources,
                         include_dirs=[np.get_include(),
                                       os.path.expanduser(
                                       "~/.local/include/coin"),
                                       ],
                         depends=optimization_depends,
                         libraries=["ipopt",
                                    "blas", "lapack", "gfortran",
                                    "pthread", "gfortranbegin", 'm', "gcc_s",
                                    "dl",
                                    "coinhsl"
                                    ],
                         library_dirs=[os.path.expanduser('~/.local/lib')],
                         language='c++'
                         )

    return config


if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())
