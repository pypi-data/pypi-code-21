import enum


class _Categories(enum.Enum):
    OTHER = '1'
    BRIDGE = '2'
    FAN = '3'
    GARAGE_DOOR_OPENER = '4'
    LIGHTBULB = '5'
    DOOR_LOCK = '6'
    OUTLET = '7'
    SWITCH = '8'
    THERMOSTAT = '9'
    SENSOR = '10'
    ALARM_SYSTEM = '11'
    DOOR = '12'
    WINDOW = '13'
    WINDOW_COVERING = '14'
    PROGRAMMABLE_SWITCH = '15'
    RANGE_EXTENDER = '16'
    CAMERA = '17'


class _States(enum.Enum):
    """ We don't actually understand the utility of the state parameter, this is just a guess """
    ON = '1'
    OFF = '1'


class _Discoverable(enum.Enum):
    TRUE = '1'
    FALSE = '0'
