"""
 # Copyright (c) 2017 Boolein Integer Indonesia, PT.
 # suryakencana 1/27/17 @author nanang.suryadi@boolein.id
 #
 # You are hereby granted a non-exclusive, worldwide, royalty-free license to
 # use, copy, modify, and distribute this software in source code or binary
 # form for use in connection with the web services and APIs provided by
 # Boolein.
 #
 # As with any software that integrates with the Boolein platform, your use
 # of this software is subject to the Boolein Developer Principles and
 # Policies [http://developers.Boolein.com/policy/]. This copyright notice
 # shall be included in all copies or substantial portions of the software.
 #
 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 # THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 # FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 # DEALINGS IN THE SOFTWARE
 # 
 # directive
"""
from pyramid.compat import iteritems_
from pyramid.util import InstancePropertyHelper
from zope.interface import Interface, Attribute, implementer


def add_widgets_ui(config, name, module, reify=False):
    module = config.maybe_dotted(module)

    exts = config.registry.queryUtility(IWidgetExtensions)
    if exts is None:
        exts = _WidgetsExtensions()
        config.registry.registerUtility(exts, IWidgetExtensions)

    callable = exts.descriptors if reify else exts.methods
    callable[name] = module


def add_subscriber_widgets(event):
    request = event['request']
    extensions = request.registry.queryUtility(IWidgetExtensions)

    if extensions is not None:
        for name, fn in iteritems_(extensions.methods):
            # TODO: validasi widget interface di decorator function
            setattr(extensions, name, fn)

        InstancePropertyHelper.apply_properties(
            extensions, extensions.descriptors)
    # if not hasattr(event, 'widgets'):
    #     event.update({'widgets': {'__name__': 'widgets'}})
    event.update({'baka': extensions})


def includeme(config):
    config.add_directive('add_widgets', add_widgets_ui)
    config.add_subscriber(
        add_subscriber_widgets,
        'pyramid.events.BeforeRender'
    )


class IWidgetExtensions(Interface):
    """ Marker interface for storing widget extensions (properties and
    methods) which will be added to the widget object."""
    descriptors = Attribute(
        """A list of descriptors that will be added to each widget.""")
    methods = Attribute(
        """A list of methods to be added to each widget.""")


@implementer(IWidgetExtensions)
class _WidgetsExtensions(object):
    def __init__(self):
        self.descriptors = {}
        self.methods = {}
