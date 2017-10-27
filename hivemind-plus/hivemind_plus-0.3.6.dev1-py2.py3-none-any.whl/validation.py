from hivemindplus.exceptions import ConfigValidationException


def validate(obj, field_groups):
    errors = []
    for group in field_groups:
        valid = False

        for field in group:
            if getattr(obj, field) is not None:
                valid = True
                break

        if not valid:
            errors.append([field.replace('_', ' ').strip() for field in group])

    if len(errors) != 0:
        message = 'No {} was supplied'.format(', '.join([' or '.join(group) for group in errors]))
        raise ConfigValidationException(message)
