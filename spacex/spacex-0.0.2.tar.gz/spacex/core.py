from .http import request


def get_all_cores():
    """Retrieves all cores.
    
    Returns
    -------
    List[:class:`Core`]
        All retrieved cores.
    """
    data = request('v2', 'parts', 'cores')

    return [Core(c) for c in data]


def get_filtered_cores(**filters):
    """Returns a list of filtered cores using the given kwargs.
    
    +------------------+-----------------------------------------+
    | Query Strings    | Description                             |
    +==================+=========================================+
    | core_serial      | Filter by core serial number            |
    +------------------+-----------------------------------------+
    | status           | Filter by flight status                 |
    +------------------+-----------------------------------------+
    | original_launch  | Filter by original launch date          |
    +------------------+-----------------------------------------+
    | missions         | Filter by flight missions               |
    +------------------+-----------------------------------------+
    | rtls_attempt     | Filter by RTLS attempt                  |
    +------------------+-----------------------------------------+
    | rtls_landings    | Filter by total number of RTLS landings |
    +------------------+-----------------------------------------+
    | asds_attempt     | Filter by ASDS attempt                  |
    +------------------+-----------------------------------------+
    | asds_landings    | Filter by total number of ASDS landings |
    +------------------+-----------------------------------------+
    | water_landing    | Filter by water landing                 |
    +------------------+-----------------------------------------+
    
    Parameters
    ----------
    **filters
        Optional filters to pass.
        
    Returns
    -------
    List[:class:`Core`]
        A list of filtered cores.
    """
    data = request('v2', 'parts', 'cores', **filters)

    return [Core(c) for c in data]


class Core:
    """Represents a core.
    
    Attributes
    ----------
    core_serial: str
        The core's serial number.
    status: str
        The core's status.
    original_launch: str
        The original launch date and time.
    missions: List[str]
        The list of missions the core was used on.
    rtls_attempt: bool
        Whether RTLS was attempted or not.
    rtls_landings: int
        The amount of RTLS landings performed.
    asds_attempt: bool
        Whether ASDS was attempted or not.
    asds_landings: int
        The amount of ASDS landings performed.
    water_landing: bool
        Whether the core landed in water or not.
    details: str
        Extra details about the core.
    """
    def __init__(self, data):
        self._from_data(data)

    def _from_data(self, data):
        self.__dict__.update(data)

    def __repr__(self):
        return '<Core core_serial={}>'.format(self.core_serial)
