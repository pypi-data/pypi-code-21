from django.db.models.manager import BaseManager
from .query import TwistedQuerySet

class TwistedManager(BaseManager.from_queryset(TwistedQuerySet)):
    pass

try:
    from .query import BulkTwistedQuerySet
    class BulkTwistedManager(BaseManager.from_queryset(BulkTwistedQuerySet)):
        pass

except ImportError:
    pass
