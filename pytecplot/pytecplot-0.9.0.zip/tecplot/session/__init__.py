"""|Tecplot Engine| and |Tecplot License| management.

The `session` module contains methods used to manipulate the |Tecplot Engine|
such as notification of a state-change that was done outside of PyTecplot.
It also contains methods for acquiring and releasing the |Tecplot License|.
"""

from .aux_data import AuxData
from .session import (acquire_license, connect, connected, disconnect,
                      license_expiration, release_license, start_roaming, stop,
                      stop_roaming)
from .state_changed import state_change, state_changed, zones_added
from .style import Style, get_style, set_style

import os
import platform
from ..tecutil import _tecutil_connector


def tecplot_install_directory():
    """|Tecplot 360| installation directory.

    Top-level installation directory for |Tecplot 360|. This will
    typically contain configuration files and the examples directory.

    This directory is platform-dependent and will contain configuration files
    and the examples directory:

    .. code-block:: python
        :emphasize-lines: 4

        import os
        import tecplot

        installdir = tecplot.session.tecplot_install_directory()
        infile = os.path.join(installdir,'examples','SimpleData','SpaceShip.lpk')
        outfile = 'spaceship.png'
        tecplot.load_layout(infile)
        tecplot.export.save_png(outfile, 600, supersample=3)

    .. figure:: /_static/images/spaceship.png
        :width: 300px
        :figwidth: 300px
    """
    d = _tecutil_connector.tecsdkhome
    if not d:
        _tecutil_connector.start()
    if platform.system() in ['Darwin', 'Mac']:
        d = os.path.normpath(os.path.join(d, '..', '..'))
    return d


def tecplot_examples_directory():
    """|Tecplot 360| examples directory.

    Examples directory that is typically installed with |Tecplot 360|.
    This may be overridden with the TECPLOT_EXAMPLES environment variable.

    This directory is platform-dependent and by default contains the various
    examples shipped with |Tecplot 360|:

    .. code-block:: python
        :emphasize-lines: 4

        import os
        import tecplot

        examples_dir = tecplot.session.tecplot_examples_directory()
        infile = os.path.join(examples_dir,'SimpleData','F18.lay')
        outfile = 'load_example.png'
        tecplot.load_layout(infile)
        tecplot.export.save_png(outfile, 600, supersample=3)

    .. figure:: /_static/images/load_example.png
        :width: 300px
        :figwidth: 300px
    """
    d = tecplot_install_directory()
    return os.environ.get('TECPLOT_EXAMPLES', os.path.join(d, 'examples'))
