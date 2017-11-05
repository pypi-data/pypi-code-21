# Copyright (C) 2007-2017, Raffaele Salmaso <raffaele@salmaso.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from django import template
from django.utils.encoding import iri_to_uri
from django.utils.safestring import mark_safe
from reactjs import conf as settings

def is_installed(module):
    try:
        from django.apps import apps
        return apps.is_installed(module)
    except ImportError:
        return module in settings.INSTALLED_APPS
if is_installed('django.contrib.staticfiles'):
    from django.contrib.staticfiles.templatetags.staticfiles import static as _static
else:
    from django.templatetags.static import static as _static


register = template.Library()
MINIFIED = ".min" if settings.MINIFIED else ""


def _reactjs(script, context, version=settings.VERSION, minified=MINIFIED):
    return mark_safe("""<script type="text/javascript" src="{react}"></script>
<script type="text/javascript" src="{reactdom}"></script>""".format(
        reactdom=_static(iri_to_uri(
            "reactjs/{script}-{version}{minified}.js".format(
                script="react-dom",
                version=version,
                minified=minified,
            )
        )),
        react=_static(iri_to_uri(
            "reactjs/{script}-{version}{minified}.js".format(
                script=script,
                version=version,
                minified=minified,
            )
        )),
    ))


@register.simple_tag(takes_context=True, name="reactjs")
def tag_reactjs(context, version=settings.VERSION, minified=MINIFIED):
    return _reactjs("react", context=context, version=version, minified=minified)


@register.simple_tag(takes_context=True, name="reactjs_with_addons")
def tag_reactjs_with_addons(context, version=settings.VERSION, minified=MINIFIED):
    return _reactjs("react-with-addons", context=context, version=version, minified=minified)
