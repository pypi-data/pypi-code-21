import graham.utils
import marshmallow


class MixedList(marshmallow.fields.Field):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields')
        super().__init__(*args, **kwargs)

        self.instances = []

        for cls_or_instance in fields:
            if isinstance(cls_or_instance, type):
                if not issubclass(cls_or_instance,
                                  marshmallow.fields.FieldABC):
                    raise ValueError('The type of the list elements '
                                     'must be a subclass of '
                                     'marshmallow.base.FieldABC')
                self.instances.append(cls_or_instance())
            else:
                if not isinstance(cls_or_instance,
                                  marshmallow.fields.FieldABC):
                    raise ValueError('The instances of the list '
                                     'elements must be of type '
                                     'marshmallow.base.FieldABC')
                self.instances.append(cls_or_instance)

    def get_cls_or_instance(self, cls_or_instance):
        if not isinstance(self.instances, dict):
            instances = {}
            for instance in self.instances:
                if isinstance(instance, marshmallow.fields.Nested):
                    nested = instance.nested
                    if isinstance(nested, str):
                        if nested == marshmallow.fields._RECURSIVE_NESTED:
                            instances[self.parent.__graham_graham__.type] = (
                                self.parent
                            )
                        else:
                            cls = marshmallow.class_registry.get_class(
                                nested)
                            instances[cls._type.constant] = cls
                    else:
                        instances[nested._type.constant] = nested
                else:
                    instances[instance._type.constant] = instance

            self.instances = instances

        # TODO: handle self referential schema definition
        # self.cls_or_instance['group'] = Group.schema

        return self.instances[cls_or_instance]

    def _serialize(self, value, attr, obj):
        return [graham.core.dump(each).data for each in value]

    def _deserialize(self, value, attr, data):
        type_attribute_name = graham.core.type_attribute_name

        return [
            self.get_cls_or_instance(each[type_attribute_name]).load(
                graham.utils._dict_strip(each, (type_attribute_name,)),
            ).data
            for each in value
        ]
