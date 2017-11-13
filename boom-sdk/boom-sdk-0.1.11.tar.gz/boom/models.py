from declaration import fields, models


class Code(models.DeclarativeBase):
    scope = fields.StringField()
    code = fields.StringField()


class Account(models.DeclarativeBase):
    id = fields.UUIDField()
    email = fields.StringField()
    first_name = fields.StringField()
    last_name = fields.StringField()
    code = fields.NestedField(Code)
    created_date = fields.DateTimeField()
    updated_date = fields.DateTimeField()


class Platform(models.DeclarativeBase):
    id = fields.UUIDField()
    identifier = fields.StringField()


class Conversation(models.DeclarativeBase):
    id = fields.UUIDField()
    platform = fields.NestedField(Platform)
    account = fields.NestedField(Account)
    created_date = fields.DateTimeField()
    updated_date = fields.DateTimeField()


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
