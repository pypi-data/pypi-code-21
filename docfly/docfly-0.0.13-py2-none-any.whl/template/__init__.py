#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import jinja2
try:
    from ..pkg import textfile
except:  # pragma: no cover
    from docfly.pkg import textfile


data = dict()
dir_path = os.path.dirname(__file__)
for basename in os.listdir(dir_path):
    if basename.endswith(".tpl"):
        fname, ext = os.path.splitext(basename)
        abspath = os.path.join(dir_path, basename)
        data[fname] = textfile.read(abspath)


class TemplateCollection(object):
    toc = jinja2.Template(data["toc"])
    module = jinja2.Template(data["module"])
    package = jinja2.Template(data["package"])


TC = TemplateCollection


if __name__ == "__main__":
    from docfly.pkg.picage import Package, Module
    from docfly.doctree import Article
    from docfly.api_reference_doc import is_ignored

    pkg = Package("docfly")
    text = TC.package.render(
        package=pkg, ignored_packages=[], is_ignored=is_ignored)
    print(text)

    module = Module("docfly.zzz_manual_install")
    text = TC.module.render(module=module)
    print(text)

    article = Article(title="Hello World", path="hello-world/index.rst")
    text = TC.toc.render(header="Table of Content", article_list=[article, ])
    print(text)
