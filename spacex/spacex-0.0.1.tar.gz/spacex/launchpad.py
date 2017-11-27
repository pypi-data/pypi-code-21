from .http import request
from .errors import *


def get_all_launchpads():
    """Retrieves information for all launchpads.
    
    Returns
    -------
    List[:class:`Launchpad`]
        A list of all launchpads.
    """
    data = request('v2', 'launchpads', '')
    return [Launchpad(l) for l in data]


def get_launchpad_by_id(id: str):
    """Returns information for a specific Launchpad based on ID.

    Parameters
    ----------
    id: str
        The ID of the lauchpad.

    Returns
    -------
    :class:`Launchpad`
        The found vehicle.

    Raises
    ------
    LaunchpadNotFound
        The ID passed could not be found.
    """
    data = request('v2', 'launchpads', id)
    if data is None:
        raise LaunchpadNotFound('{} was not found.'.format(id))

    return Launchpad(data)


class Launchpad:
    """Represents a launchpad.
    
    Attributes
    ----------
    id: str
        The ID of the launchpad.
    full_name: str
        The full name of the launchpad.
    vehicles_launched: str
        The vehicles launched at this launchpad.
    details: str
        This launchpad's extra details.
    location: :class:`Location`
        The launchpad's location details.
    """
    def __init__(self, data):
        self._from_data(data)

    def _from_data(self, data):
        self.location = Location(data.pop('location', {}))
        self.__dict__.update(data)

    def __repr__(self):
        return '<Launchpad id={}>'.format(self.id)


class Location:
    """Represents a launchpad location.
    
    Attributes
    ----------
    name: str
        The location's name.
    region: str
        The location's region.
    latitude: float
        The location's latitude.
    longitude: float
        The location's longitude.
    """
    def __init__(self, data):
        self._from_data(data)

    def _from_data(self, data):
        self.__dict__.update(data)

    def __repr__(self):
        return '<Location name={}>'.format(self.name)
