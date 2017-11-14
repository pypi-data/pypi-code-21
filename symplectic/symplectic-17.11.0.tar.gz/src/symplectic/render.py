"""
Rendering
"""

import functools
import os
import shutil

import pkg_resources

import chameleon


def _process(template, inputs, output_file):
    rendered = template(**inputs)
    if rendered.count('<!DOCTYPE html>') > 1:
        rendered = rendered.replace('<!DOCTYPE html>', '', 1)
    with open(output_file, 'w') as filep:
        filep.write(rendered)


def _dict_sum(dict1, **dict2):
    ret = dict1.copy()
    ret.update(dict2)
    return ret


def render(blog, theme, output):
    """
    Render a blog

    Render a blog to the output directory.

    Args:
        blog (Blog): Blog to render
        theme (list of str): List of theme directories
        output (str): output directory
    """
    theme[0:0] = [pkg_resources.resource_filename('symplectic', 'basic')]
    if not os.path.exists(output):
        os.makedirs(output)
    loader = chameleon.PageTemplateLoader(theme)
    base_dict = dict(metadata=blog.metadata, pages=blog.pages,
                     pagination=None,
                     archives=[dict(name='All', link='list.html')])
    regular_and = functools.partial(_dict_sum, base_dict)
    _process(loader['river.html'],
             regular_and(posts=blog.posts),
             os.path.join(output, 'river.html'))
    _process(loader['list.html'],
             regular_and(posts=blog.posts),
             os.path.join(output, 'list.html'))
    for post in blog.posts:
        _process(loader['post.html'],
                 regular_and(post=post),
                 os.path.join(output, '{}.html'.format(post.slug)))
    for page in blog.pages:
        _process(loader['post.html'],
                 regular_and(post=page),
                 os.path.join(output, '{}.html'.format(page.slug)))
    dname = theme[-1]
    for asset in ['css', 'js']:
        if os.path.exists(os.path.join(output, asset)):
            shutil.rmtree(os.path.join(output, asset))
        shutil.copytree(os.path.join(dname, asset),
                        os.path.join(output, asset))
