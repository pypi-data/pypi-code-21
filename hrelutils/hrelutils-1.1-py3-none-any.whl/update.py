import typing


def get_or_create(model, identifiers: dict, *, extra_attrs: dict):
    """
    Either get a record by `identifiers`, or if `extra_attrs` is provided,
    either create a new record or update an old one
    """
    match = model.objects.filter(**identifiers).first()

    if not extra_attrs:
        return match

    else:
        if not match:
            match = model(**identifiers)

        for attr in extra_attrs:
            setattr(match, attr, extra_attrs[attr])

        match.save()
        return match
