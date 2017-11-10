from six import iteritems

from schematics import Model as SchematicsModel
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy_utils.functions import get_columns

from dmu_utils.schematics.models import get_schematics_model_fields
from .types import schematics_field_to_sqlalchemy_column


class CustomBase(object):

    def update_from_schematics_instance(self, schematics_instance, include=None, exclude=None):

        if include is None:
            include = getattr(self, '__schematics_model_include_fields__', None)

        if exclude is None:
            exclude = getattr(self, '__schematics_model_exclude_fields__', ())

        for key, value in iteritems(schematics_instance.to_native()):
            if key in exclude or include and key not in include:
                continue

            raw_value = getattr(schematics_instance, key)
            if isinstance(raw_value, SchematicsModel):
                # TODO(dmu) HIGH: This should be optimized, because we are throwing away serialized
                #                 with to_native() value for `key`
                value = raw_value.to_primitive()
            setattr(self, key, value)

    @classmethod
    def from_schematics_instance(cls, schematics_instance, include=None, exclude=None):
        instance = cls()
        instance.update_from_schematics_instance(schematics_instance, include=include,
                                                 exclude=exclude)
        return instance

    def to_schematics_instance(self, schematics_model=None):
        schematics_model = schematics_model or getattr(self, '__schematics_model__', None)
        if not schematics_model:
            raise ValueError('Nor schematics_model method attribute neither __schematics_model__ '
                             'class attribute provided')
        return schematics_model({column.name: getattr(self, column.name) for column
                                 in get_columns(self)}, strict=False)


class CustomDeclarativeMeta(DeclarativeMeta):

    def __new__(mcs, class_name, bases, class_dict):
        schematics_model = class_dict.get('__schematics_model__')
        if schematics_model:
            include = class_dict.get('__schematics_model_include_fields__')
            exclude = class_dict.get('__schematics_model_exclude_fields__')
            class_dict = class_dict.copy()

            for field_name, field in iteritems(get_schematics_model_fields(
                    schematics_model, include=include, exclude=exclude)):
                if field_name not in class_dict:
                    class_dict[field_name] = schematics_field_to_sqlalchemy_column(field)

        return super(CustomDeclarativeMeta, mcs).__new__(mcs, class_name, bases, class_dict)


ModelBase = declarative_base(cls=CustomBase, metaclass=CustomDeclarativeMeta)
