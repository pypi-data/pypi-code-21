from django.db.models import IntegerField
from solo.models import SingletonModel


PAGE_SIZE_DEFAULT = 10


# TODO css url
class Config(SingletonModel):
    page_size = IntegerField(default=PAGE_SIZE_DEFAULT)
