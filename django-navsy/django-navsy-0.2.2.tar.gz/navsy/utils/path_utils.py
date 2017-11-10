
# -*- coding: utf-8 -*-

from django.conf import settings


def fix_path(path=None, *args):

    append_slash = settings.APPEND_SLASH

    path = path or ''
    path = join_path_slugs(*[path] + list(args))
    path_slugs = split_path_slugs(path)
    path = join_path_slugs(*path_slugs)

    if len(path_slugs):

        path_last_slug = path_slugs[-1]
        filepath_extensions = [
            '.<file_ext>', '.{file_ext}',
            '.css', '.csv', '.gif', '.gz', '.html',
            '.jpg', '.js', '.json', '.less', '.pdf',
            '.png', '.psd', '.py', '.rar', '.rss',
            '.scss', '.tar', '.txt', '.xml', '.yml',
            '.zip']

        for extension in filepath_extensions:
            if path_last_slug.endswith(extension):
                append_slash = False
                break

    if not path.startswith('/'):
        path = '/' + path

    if not path.endswith('/'):
        path += '/'

    if not append_slash and len(path) > 1:
        path = path[0:-1]

    return path


def join_path_slugs(*slugs):
    path = '/'.join(slugs)
    return path


def split_path_slugs(path):
    slugs = path.split('/')
    slugs = list(filter(len, slugs))
    return slugs
