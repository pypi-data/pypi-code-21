from marshmallow import Schema, fields, post_load
from pytz import utc

from russell.constants import LOCAL_TIMEZONE
from russell.date_utils import pretty_date
from russell.model.base import BaseModel


class ExperimentSchema(Schema):
    id = fields.Str()
    name = fields.Str()
    description = fields.Str()
    created = fields.DateTime()
    state = fields.Str(allow_none=True)
    duration = fields.Number(allow_none=True)
    version = fields.Integer()
    log_id = fields.Str(load_from="logId")
    canvas = fields.Dict(load_only=True)
    task_instances = fields.List(fields.Str(), dump_only=True)
    instance_type = fields.Str(load_from="instanceType", allow_none=True)
    outputs = fields.List(fields.Dict(), allow_none=True)
    inputs = fields.List(fields.Dict(), allow_none=True)
    command = fields.Str()
    mode = fields.Str(allow_none=True)
    @post_load
    def make_experiment(self, data):
        return Experiment(**data)


class Experiment(BaseModel):
    schema = ExperimentSchema(strict=True)
    default_outputs = [{'name': 'output', 'type': 'dir'}]
    default_inputs = [{'name': 'input', 'type': 'dir'}]
    def __init__(self,
                 id,
                 name,
                 description,
                 created,
                 state,
                 duration,
                 log_id,
                 command,
                 mode="cli",
                 canvas=None,
                 instance_type=None,
                 outputs=None,
                 inputs=None):
        self.id = id
        self.name = name
        self.description = description
        self.created = self.localize_date(created)
        self.state = state
        self.duration = duration
        self.log_id = log_id
        self.command = command
        self.mode = mode
        if canvas:
            nodes = canvas.get('nodes', {})
            self.task_instances = {}
            for key in nodes:
                self.task_instances[nodes[key].get("taskInstanceId")] = nodes[key].get("type")
        self.instance_type = instance_type
        self.outputs = outputs or self.default_outputs
        self.inputs = inputs or self.default_inputs

    def localize_date(self, date):
        if not date.tzinfo:
            date = utc.localize(date)
        return date.astimezone(LOCAL_TIMEZONE)

    @property
    def created_pretty(self):
        return pretty_date(self.created)

    @property
    def duration_rounded(self):
        return int(self.duration or 0)

    @property
    def instance_type_trimmed(self):
        if self.instance_type:
            return self.instance_type.split('_')[0]
        return self.instance_type

    @property
    def is_finished(self):
        return self.state in ["shutdown", "failed", "success"]


class ExperimentRequestSchema(Schema):
    name = fields.Str()
    description = fields.Str()
    module_id = fields.Str()
    data_id = fields.Str()
    family_id = fields.Str(allow_none=True)
    version = fields.Integer(allow_none=True)
    predecessor = fields.Str(allow_none=True)
    instance_type = fields.Str(allow_none=True)
    command = fields.Str()
    mode = fields.Str(allow_none=True)
    environment = fields.Str(allow_none=True)
    @post_load
    def make_experiment_request(self, data):
        return ExperimentRequest(**data)


class ExperimentRequest(BaseModel):
    schema = ExperimentRequestSchema(strict=True)

    def __init__(self,
                 name,
                 description,
                 module_id,
                 data_id=None,
                 predecessor=None,
                 command=None,
                 mode=None,
                 family_id=None,
                 project_id=None,
                 version=None,
                 instance_type=None,
                 environment=None):
        self.name = name
        self.description = description
        self.module_id = module_id
        self.data_id = data_id
        self.family_id = family_id
        self.project_id = project_id
        self.version = version
        self.instance_type = instance_type
        self.command = command
        self.mode = mode
        self.predecessor = predecessor
        self.environment = environment
