from .http import request
from .errors import *


def get_all_vehicles():
    """Returns generic information for all Vehicles.
    
    Returns
    -------
    List[:class:`Vehicle`]
        A list of all generic vehicle information.
    """
    data = request('v2', 'vehicles', '')
    return [Vehicle(v) for v in data if v['type'] != 'capsule']


def get_all_capsules():
    """Returns information for all Capsules.
    
    Returns
    -------
    List[:class:`Capsule`]
        A list of all Capsule information.
    """
    data = request('v2' 'vehicles', '')
    return [Capsule(c) for c in data if c['type'] == 'capsule']


def get_vehicle_by_id(id: str):
    """Returns information for a specific Vehicle based on ID.
    
    This includes Capsules.
    
    Parameters
    ----------
    id: str
        The ID of the vehicle.
        
    Returns
    -------
    :class:`Vehicle`
        The found vehicle.
        
    Raises
    ------
    VehicleNotFound
        The ID passed could not be found.
    """
    data = request('v2', 'vehicles', id)
    if data is None:
        raise VehicleNotFound('{} was not found.'.format(id))

    return Vehicle(data)


class Capsule:
    """Represents a Capsule
    
    Attributes
    ----------
    id: str
        The capsule ID.
    name: str
        The capsule name.
    type: str
        The capsule type.
    active: bool
        The activity state of the capsule.
    sidewall_angle_deg: int
        The angle of the sidewall.
    orbit_duration_yr: int
        The orbit duration in years.
    variations: dict
        Variations of the capsule.
    heat_shield: dict
        Information of the capsule's heat shield.
    thrusters: dict
        Information on the capsule's thrusters.
    launch_payload_mass: dict
        Information on the capsule's launch payload mass.
    launch_payload_vol: dict
        Information on the capsule's launch payload volume.
    return_payload_mass: dict
        Information on the capsule's return payload mass.
    return_payload_vol: dict
        Information on the capsule's return payload volume.
    pressurized_capsule: dict
        Information about the capsule's payload when pressurized.
    trunk: dict
        Information on the capsule's trunk.
    height_w_trunk: dict
        Information on the height of the trunk.
    diameter: dict
        Information on the capsule's diameter.
    """
    def __init__(self, data):
        self._from_data(data)

    def _from_data(self, data):
        self.__dict__.update(data)


class Vehicle:
    """Represents a vehicle.
    
    Attributes
    ----------
    id: str
        The ID of the vehicle.
    name: str
        The name of the vehicle.
    type: str
        The type of the vehicle.
    active: bool
        The activity state of the vehicle.
    stages: int
        The amount of stages.
    engines: dict
        Contains specific information on the engines.
    cost_per_launch: int
        The USD amount it costs per launch.
    success_rate_pct: int
        The success rate percent.
    first_flight: str
        The date of the first flight in YYYY-MM-DD.
    launchpad: str
        The launchpad that was used.
    country: str
        The country it was in.
    company: str
        The company of the vehicle.
    height: dict
        The height in meters and feet.
    diameter: dict
        The diameter in meters and feet.
    mass: dict
        The mass in pounds and kilograms.
    payload_weights: List[PayloadWeights]
        A list of PayloadWeights.
    description: str
        A short description of the vehicle.
    stage_info: List[:class:`Stage`]
        Ordered additional information on each stage of the vehicle.
    """
    def __init__(self, data):
        self._from_data(data)

    def _from_data(self, data):
        payload_weights = data.pop('payload_weights', None)
        if payload_weights is not None:
            self.payload_weights = [PayloadWeights(p) for p in payload_weights]
        self.stage_info = []
        for k, v in dict(data).items():
            if k.endswith('_stage'):
                self.stage_info.append(Stage(data.pop(k)))
        self.engines = data.pop('engines', {})
        self.__dict__.update(data)


class Stage:
    """Represents a stage for a vehicle.
    
    Attributes
    ----------
    reusable: bool
        Whether or not the stage is reusable.
    engines: Union[int, dict]
        The amount of engines. May contain additional information.
    cores: Optional[int]
        The amount of cores.
    fuel_amount_tons: int
        The amount of fuel in tons.
    burn_time_sec: int
        The burn time in seconds.
    payloads: Optional[dict]
        A dictionary containing information on the stage's payloads.
    """
    def __init__(self, data):
        self._from_data(data)

    def _from_data(self, data):
        self.reusable = bool(data.pop('reusable', False))
        self.cores = data.pop('cores', 0)
        self.__dict__.update(data)


class PayloadWeights:
    """Represents a payload weight.
    
    Attributes
    ----------
    id: str
        The ID of the payload.
    name: str
        The name of the payload.
    kg: int
        The weight of the payload in kilograms.
    lb: int
        The weight of the payload in pounds.
    """
    def __init__(self, data):
        self._from_data(data)

    def _from_data(self, data):
        self.__dict__.update(data)
