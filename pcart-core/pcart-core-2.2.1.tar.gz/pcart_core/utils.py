
SLUG_SAVE_AS_DASH = '.,/'
SLUG_ALLOWED_CHARS = r'^[a-zA-Z0-9\-]$'


def get_settings_upload_path(site_id, filename):
    import os
    path = os.path.join(
        'theme-config',
        'site-%s' % site_id,
    )
    if filename is not None:
        path = os.path.join(path, filename)
    return path


def get_settings_upload_url(site_id, filename):
    from django.core.files.storage import default_storage
    path = get_settings_upload_path(site_id, filename)
    return default_storage.url(path)


def slugify_unicode(value, save_as_dash=SLUG_SAVE_AS_DASH, dash='-'):
    import re
    import slugify
    for k in save_as_dash:
        value = value.replace(k, dash)
    result = slugify.slugify(value, only_ascii=True)

    pattern = re.compile(SLUG_ALLOWED_CHARS)
    result = ''.join(filter(lambda x: pattern.match(x) is not None, result))
    return result


def get_unique_slug(value, model_class, slug_attr='slug', slug_func=slugify_unicode, ignore_slugs=[]):
    """ Generate unique slug for a model."""
    import itertools
    _slug = _orig = slug_func(value)
    for x in itertools.count(1):
        if not model_class.objects.exclude(
                **{'%s__in' % slug_attr: ignore_slugs}).filter(**{slug_attr: _slug}).exists():
            break
        _slug = '%s-%d' % (_orig, x)
    return _slug


def markdown_to_html(source):
    import markdown
    html = markdown.markdown(
        source,
        extensions=[
            'markdown.extensions.nl2br',
            'urlize',
        ])
    return html
