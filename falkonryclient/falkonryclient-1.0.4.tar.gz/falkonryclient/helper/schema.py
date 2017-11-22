"""
Falkonry Client

Client to access Condition Prediction APIs

:copyright: (c) 2016 by Falkonry Inc.
:license: MIT, see LICENSE for more details.

"""

from falkonryclient.helper.models import *

Models = {
    "Assessment": Assessment,
    "Datastream": Datastream,
    "Datasource": Datasource,
    "Field": Field,
    "Signal": Signal,
    "Input": Input,
    "Stats": Stats,
    "EntityMeta": EntityMeta,
    "Tracker": Tracker
}

__all__ = [
    'Models'
]
