from django.shortcuts import render


def render_asset(request, path, prefix='assets'):
    import mimetypes
    context = {}
    response = render(request, '%s/%s' % (prefix, path), context, mimetypes.guess_type(path)[0])
    return response
