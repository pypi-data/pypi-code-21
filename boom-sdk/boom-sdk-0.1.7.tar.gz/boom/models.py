from declaration import fields, models


class Account(models.DeclarativeBase):
    pass


class Conversation(models.DeclarativeBase):
    id = fields.UUIDField()


class Platform(models.DeclarativeBase):
    id = fields.UUIDField()
    identifier = fields.StringField()


class Message(models.DeclarativeBase):
    conversation = fields.NestedField(Conversation)
    platform = fields.NestedField(Platform)
    sender = fields.StringField()
    receiver = fields.StringField()
    identifier = fields.StringField()
    intent = fields.StringField()
    content = fields.StringField()
    raw = fields.StringField()
    extra = fields.JSONField()
    timestamp = fields.DateTimeField()
