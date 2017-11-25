import json
import datetime

from django.db.models import QuerySet, Model
from django.utils.deprecation import CallableBool


class DanteEncoder(json.JSONEncoder):
    def _from_fields(self, obj, fields):
        result = {key: getattr(obj, key) for key in fields}
        return result

    def _standard(self, obj):
        result = {field.name: getattr(obj, field.name) for field in obj.__class__._meta.fields}
        return result

    def default(self, obj):
        if isinstance(obj, QuerySet):
            result = [o for o in obj]
            return result
        elif isinstance(obj, Model):
            try:
                return obj.__to_json_dict__()
            except AttributeError:
                # Проверяем есть ли там __to_json_fields__
                try:
                    fields = obj.__to_json_fields__
                except AttributeError:
                    return self._standard(obj)
                else:
                    return self._from_fields(obj, fields)
        elif isinstance(obj, datetime.date):
            return str(obj)
        elif isinstance(obj, datetime.time):
            return str(obj)
        elif isinstance(obj, CallableBool):
            return True if obj else False
        else:
            return super().default(obj)
