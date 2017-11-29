from marshmallow import Schema, fields, post_load

from russell.cli.utils import sizeof_fmt
from russell.model.base import BaseModel
from pytz import utc
from russell.constants import LOCAL_TIMEZONE
from russell.date_utils import pretty_date

class DataDetailsSchema(Schema):
    state = fields.Str()
    size = fields.Str()
    uri = fields.Str()

    @post_load
    def make_data_details(self, data_details):
        return DataDetails(**data_details)


class DataDetails(BaseModel):
    schema = DataDetailsSchema(strict=True)

    def __init__(self,
                 state,
                 size,
                 uri):
        self.state = state
        self.size = size
        self.uri = uri

class ModuleSchema(Schema):
    name = fields.Str()
    id = fields.Str()
    description = fields.Str()

    module_type = fields.Str(allow_none=True)
    family_id = fields.Str(allow_none=True)
    entity_id = fields.Str(allow_none=True)
    version = fields.Int(allow_none=True)
    created = fields.DateTime(load_from="date_created")
    size = fields.Int(allow_none=True)
    state = fields.Str(allow_none=True)

    @post_load
    def make_module(self, data):
        return Module(**data)


class Module(BaseModel):
    schema = ModuleSchema(strict=True)

    def __init__(self,
                 name,
                 description=None,
                 id=None,
                 module_type="code",
                 family_id=None,
                 entity_id=None,
                 version=None,
                 created=None,
                 size=0,
                 uri=None,
                 state=None):
        self.id = id
        self.name = name
        self.description = description
        self.module_type = module_type
        self.family_id = family_id
        self.version = version
        self.entity_id = entity_id
        self.size = size
        self.state = state
        self.created = self.localize_date(created)
        self.uri = uri

    def localize_date(self, date):
        if not date:
            return None
        if not date.tzinfo:
            date = utc.localize(date)
        return date.astimezone(LOCAL_TIMEZONE)

    @property
    def created_pretty(self):
        return pretty_date(self.created)

    @property
    def size_pretty(self):
        if self.size < 1:
            return "less than 1 MB"
        #self.size is MB to B
        return sizeof_fmt(self.size * 1024 * 1024)


class ModuleRequestSchema(Schema):
    name = fields.Str()
    description = fields.Str()
    module_type = fields.Str()
    entity_id = fields.Str()
    data_type = fields.Str()
    version = fields.Integer(allow_none=True)
    size = fields.Int(allow_none=True)
    @post_load
    def make_data(self, data):
        return ModuleRequest(**data)

class ModuleRequest(BaseModel):
    schema = ModuleRequestSchema(strict=True)

    def __init__(self,
                 name,
                 entity_id=None,
                 description=None,
                 module_type="code",
                 version=None,
                 data_type=None,
                 size=None):
        self.name = name
        self.description = description
        self.module_type = module_type
        self.version = version
        self.entity_id = entity_id
        self.data_type = data_type
        self.size = size
