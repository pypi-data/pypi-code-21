import datetime

from .vehicle import get_vehicle_by_id
from .http import request


def get_latest_launch():
    """Returns the latest :class:`Launch`.
    
    Returns
    -------
    :class:`Launch`
        The latest launch.
    """
    data = request('v2', 'launches', 'latest')
    return Launch(data)


def get_all_launches(upcoming=False):
    """Returns all launches.
    
    The list is in the order of oldest to newest.
    
    Parameters
    ----------
    upcoming: bool, optional(default=False)
        Retrieve upcoming launches.
    
    Returns
    -------
    List[:class:`Launch`]
        All retrieved launches.
    """
    data = request('v2', 'launches', '')
    return [Launch(l) for l in data]


def get_filtered_launches(upcoming=False, **filters):
    """Returns a list of filtered launches using the given kwargs.
    
    +---------------------+------------------------------------------+
    | Query Strings       | Description                              |
    +=====================+==========================================+
    | start & final       | Filter by a data range                   |
    +---------------------+------------------------------------------+
    | flight_number       | Filter by flight number                  |
    +---------------------+------------------------------------------+
    | launch_year         | Filter by year                           |
    +---------------------+------------------------------------------+
    | launch_date_utc     | Filter by UTC timestamp                  |
    +---------------------+------------------------------------------+
    | launch_date_local   | Filter by local ISO timestamp            |
    +---------------------+------------------------------------------+
    | rocket_id           | Filter by rocket id                      |
    +---------------------+------------------------------------------+
    | rocket_name         | Filter by rocket name                    |
    +---------------------+------------------------------------------+
    | rocket_type         | Filter by rocket type                    |
    +---------------------+------------------------------------------+
    | core_serial         | Filter by core serial                    |
    +---------------------+------------------------------------------+
    | cap_serial          | Filter by dragon capsule serial          |
    +---------------------+------------------------------------------+
    | core_reuse          | Filter by core reusability               |
    +---------------------+------------------------------------------+
    | side_core1_reuse    | Filter by Falcon Heavy side core 1 reuse |
    +---------------------+------------------------------------------+
    | side_core2_reuse    | Filter by Falcon Heavy side core 2 reuse |
    +---------------------+------------------------------------------+
    | fairings_reuse      | Filter by fairing reuse                  |
    +---------------------+------------------------------------------+
    | capsule_reuse       | Filter by dragon capsule reuse           |
    +---------------------+------------------------------------------+
    | site_id             | Filter by launch site id                 |
    +---------------------+------------------------------------------+
    | site_name           | Filter by launch site name               |
    +---------------------+------------------------------------------+
    | site_name_long      | Filter by long launch site name          |
    +---------------------+------------------------------------------+
    | payload_id          | Filter by payload id                     |
    +---------------------+------------------------------------------+
    | customer            | Filter by launch customer                |
    +---------------------+------------------------------------------+
    | payload_type        | Filter by payload type                   |
    +---------------------+------------------------------------------+
    | orbit               | Filter by payload orbit                  |
    +---------------------+------------------------------------------+
    | launch_success      | Filter by successful launches            |
    +---------------------+------------------------------------------+
    | reused              | Filter by launches with reused cores     |
    +---------------------+------------------------------------------+
    | land_success        | Filter by successful core landings       |
    +---------------------+------------------------------------------+
    | landing_type        | Filter by landing method                 |
    +---------------------+------------------------------------------+
    | landing_vehicle     | Filter by landing vehicle                |
    +---------------------+------------------------------------------+
    
    Parameters
    ----------
    upcoming: bool, optional(default=False)
        Retrieve upcoming launches.
    **filters
        Optional filters to pass.
    
    Returns
    -------
    List[:class:`Launch`]
        A list of the launches found matching the criteria.
    """
    if upcoming:
        data = request('v2', 'launches', 'upcoming', **filters)
    else:
        data = request('v2', 'launches', '', **filters)

    return [Launch(l) for l in data]


class Launch:
    """Represents a launch.

    Attributes
    ----------
    flight_number: int
        The flight number of the launch.
    launch_year: str
        The year the launch took place.
    launch_date: datetime.datetime
        The UTC datetime the launch took place.
    launch_date_utc: str
        Launch date UTC timestamp string.
    launch_date_local: str
        Launch date local timestamp string.
    rocket: :class:`Vehicle`
        The rocket used in the launch.
    reuse: dict
        The reusability of different parts of the launch.
    telemetry: dict
        Launch telemetry data.
    success: bool
        Whether or not the launch was successful.
    launch_site: :class:`LaunchSite`
        The launch site information.
    details: str
        Extra launch details.
    links: dict
        Links relating to the launch.
    """
    def __init__(self, data):
        self._from_data(data)

    def _from_data(self, data):
        self.launch_date = datetime.datetime.utcfromtimestamp(data.pop('launch_date_unix', None))
        self.rocket = get_vehicle_by_id(data.pop('rocket', {}).get('rocket_id'))
        self.success = data.pop('launch_success', False)
        self.launch_site = LaunchSite(data.pop('launch_site', {}))
        self.__dict__.update(data)

    def __repr__(self):
        return '<Launch flight_number={}>'.format(self.flight_number)


class LaunchSite:
    """Represents a launch site.
    
    Attributes
    ----------
    id: str
        The launch site's ID.
    name: str
        The launch site's shortened name.
    full_name: str
        The launch site's full name.
    """
    def __init__(self, data):
        self._from_data(data)

    def _from_data(self, data):
        self.id = data.pop('site_id', None)
        self.name = data.pop('site_name', None)
        self.full_name = data.pop('site_name_long', None)

    def __repr__(self):
        return '<LaunchSite id={}>'.format(self.id)
