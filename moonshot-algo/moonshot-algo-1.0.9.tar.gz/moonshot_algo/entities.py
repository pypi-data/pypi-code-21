from enum import Enum
from mongoengine import Document, StringField, ReferenceField, ListField, IntField, EmbeddedDocumentField, \
    EmbeddedDocument, FloatField


class ScoreTypes(Enum):
    LOSS = 1
    AUC = 2


class Score(EmbeddedDocument):
    type = IntField()  # type: ScoreTypes
    value = FloatField()  # type: float

    def __repr__(self):
        return "type: {}, value: {}".format(self.type, self.value)


class DatasetConfig(EmbeddedDocument):
    pass


class ModelConfig(EmbeddedDocument):
    pass


class FitConfig(EmbeddedDocument):
    pass


class Space(Document):
    id = StringField(required=True)


class Config(Document):
    id = StringField(required=True)  # type: str
    datasetConfig = EmbeddedDocumentField(DatasetConfig)  # type: DatasetConfig
    modelConfig = EmbeddedDocumentField(ModelConfig)  # type: ModelConfig
    fitConfig = EmbeddedDocumentField(FitConfig)  # type: FitConfig


class HyperOptResult(Document):
    id = StringField(required=True)  # type: str
    space_id = ReferenceField(Space)  # type: str
    config = ReferenceField(Config)  # type: Config
    scores = ListField(EmbeddedDocumentField(Score))  # type: list[Score]
    iterations = IntField()  # type: int


class Pick(Document):
        id = StringField(required=True)  # type: str
        config_list = ListField(ReferenceField(Config))  # type: list[str]
