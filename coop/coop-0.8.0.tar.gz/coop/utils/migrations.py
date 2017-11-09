from wagtail.wagtailcore.blocks.stream_block import StreamValue


def streamfield_mapper(model_name, field_name, mapper):
    def migration_function(apps, schema):
        SomeModel = apps.get_model(model_name)
        for instance in SomeModel.objects.all():
            data = getattr(instance, field_name).stream_data
            new_data = list(mapper(instance, data))
            if data != new_data:
                stream_block = getattr(instance, field_name).stream_block
                setattr(instance, field_name, StreamValue(stream_block, new_data, is_lazy=True))
                instance.save()

    return migration_function
