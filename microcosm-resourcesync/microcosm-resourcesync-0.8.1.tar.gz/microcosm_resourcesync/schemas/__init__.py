"""
Schema modeling.

"""
from enum import Enum, unique

from microcosm_resourcesync.schemas.hal_schema import HALSchema
from microcosm_resourcesync.schemas.simple_schema import SimpleSchema


@unique
class Schemas(Enum):
    HAL = HALSchema
    SIMPLE = SimpleSchema
