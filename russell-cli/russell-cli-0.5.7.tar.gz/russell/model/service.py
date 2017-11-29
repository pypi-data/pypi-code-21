from marshmallow import Schema, fields, post_load

from russell.model.base import BaseModel


class ServiceSchema(Schema):
    """
    Russell cloud service schema
    """
    service_status = fields.Int()

    @post_load
    def make_credentials(self, data):
        return Service(**data)


class Service(BaseModel):
    """
    Service status for russell cloud
    """
    schema = ServiceSchema(strict=True)

    def __init__(self, service_status):
        self.service_status = service_status
