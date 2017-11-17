#! /usr/bin/python3

"""Gstreamer SliceBuffer element

Copyright 2011-2017 Olivier Aubert <contact@olivieraubert.net>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 2.1 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import logging
logger = logging.getLogger(__name__)

import sys

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstBase', '1.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import GObject, Gst, GstBase, GstVideo
GObject.threads_init()
Gst.init(None)

import cairo

# WIP. See https://github.com/tripzero/opencvfilter/blob/master/opencvfilter.py
# and https://github.com/tripzero/MaxVideoRenderer/blob/master/gst_hacks.py
class SliceBuffer(GstVideo.VideoFilter):
#class SliceBuffer(GstBase.BaseTransform):
    __gstmetadata__ = ("Slice buffer",
                       "Filter/Editor/Video",
                       "Buffers slices of data",
                       "Olivier Aubert <contact@olivieraubert.net>")

    __gproperties__ = {
        'slicewidth':  (GObject.TYPE_INT, 'slicewidth', 'Width of slices',
                        0, 65536, 0, GObject.PARAM_WRITABLE),
        'offset': (GObject.TYPE_INT, 'offset', 'Offset of samples in the source video. If < 0, use the original offset.',
                   -65536, 65536, 0, GObject.PARAM_WRITABLE),
    }

    _sinkpadtemplate = Gst.PadTemplate.new("sink",
                                           Gst.PadDirection.SINK,
                                           Gst.PadPresence.ALWAYS,
                                           Gst.Caps.from_string("video/x-raw,format=RGBx"))
    _srcpadtemplate = Gst.PadTemplate.new("src",
                                          Gst.PadDirection.SRC,
                                          Gst.PadPresence.ALWAYS,
                                          Gst.Caps.from_string("video/x-raw,format=RGBx"))

    #register our pad templates
    __gsttemplates__ = (_srcpadtemplate, _sinkpadtemplate)

    def __init__(self):
        super().__init__(self)
        self.set_passthrough(False)
        self.set_in_place(False)

        self.slicewidth = 1
        self.offset = 128
        self._index = 0
        self._buffer  = None
        self._surface = None

    def do_prepare_ouput_buffer(self, inbuf, outbuf):
        logger.warn("prepare_output_buffer")
        outbuf.copy(inbuf)
        return True

    def do_transform_frame_ip(self, inframe):
        logger.warn("transform_frame in place")
        return Gst.FlowReturn.OK

    def do_transform_ip(self, inframe):
        logger.warn("transform in place")
        return Gst.FlowReturn.OK

    def no_do_transform(self, inbuffer, outbuffer):
        logger.warn("do_transform")
        import pdb; pdb.set_trace()
        return Gst.FlowReturn.OK

    def do_transform_frame(self, inframe, outframe):
        logger.warn("transform_frame")
        width = inframe.info.width
        height = inframe.info.height
        import pdb; pdb.set_trace()
        if self._surface is None:
            # Need to initialize
            self._surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            self._ctx = cairo.Context(self._surface)
            self._ctx.set_source_rgb(0, 0, 0)
            self._ctx.rectangle(0, 0, width, height)
            self._ctx.fill()
            self._index = 0

        # Get rectangle
        if self.offset < 0:
            # get the rectangle at the position it will be in the destination buffer
            source_x = (self._index * self.slicewidth) % width
        else:
            # Get the rectangle at the position specified by offset
            source_x = self.offset
        dest_x = (self._index * self.slicewidth) % (width - self.slicewidth)
        self._index += 1

        # Copy slice into buffer
        (res, mapinfo) = inframe.buffer.map(Gst.MapFlags.READ)
        if not res:
            logger.warn("Error in converting buffer")
            return
        else:
            surf = cairo.ImageSurface.create_for_data(bytes(mapinfo.data), cairo.FORMAT_ARGB32, width, height, 4 * width)
            self._ctx.set_operator(cairo.OPERATOR_SOURCE)
            self._ctx.set_source_surface(surf, dest_x - source_x, 0)
            self._ctx.rectangle(dest_x, 0, self.slicewidth, height)
            self._ctx.fill()

        # Restamp result buffer using incoming buffer information
        self._buffer.stamp(inframe.buffer)
        outframe.copy(self._surface.get_buffer())
        if self.callback is not None:
            self.callback(self._buffer)
        return Gst.FlowReturn.OK

    def do_set_property(self, key, value):
        logger.warn("set_property %s %s", key, value)
        if key.name == 'slicewidth':
            self.slicewidth = value
        elif key.name == 'offset':
            self.offset = value
        else:
            logger.error("No property %s" % key.name)

    def do_set_info(self, incaps, in_info, outcaps, out_info):
        logger.warn("set_info %s %s %s %s", incaps, in_info, outcaps, out_info)
        return True

    def setCallback(self, cb):
        logger.warn("set_callback %s", cb)
        self.callback = cb

__gstelementfactory__ = ("slicebuffer", Gst.Rank.NONE, SliceBuffer)
def plugin_init(plugin, userarg):
    SliceBufferType = GObject.type_register(SliceBuffer)
    Gst.Element.register(plugin, 'slicebuffer', 0, SliceBufferType)
    return True

version = Gst.version()
reg = Gst.Plugin.register_static_full(version[0], version[1],
                                      'slicebuffer_plugin', 'SliceBuffer plugin',
                                      plugin_init, '1.0', 'Proprietary', 'abc', 'def', 'ghi', None)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    mainloop = GObject.MainLoop()

    files = [ a for a in sys.argv[1:] if not '=' in a ]
    params = [ a for a in sys.argv[1:] if '=' in a ]

    if files:
        player=Gst.element_factory_make('playbin')
        player.props.uri = 'file://' + files[0]

        bin=Gst.Bin()
        elements = [
            Gst.element_factory_make('videoconvert'),
            Gst.element_factory_make('videoscale'),
            Gst.element_factory_make('slicebuffer', 'slicer'),
            Gst.element_factory_make('capsfilter', 'capsfilter'),
            Gst.element_factory_make('videoconvert'),
            Gst.element_factory_make('autovideosink'),
            ]
        bin.add(*elements)
        Gst.element_link_many(*elements)
        bin.add_pad(Gst.GhostPad('sink', elements[0].get_pad('video_sink') or elements[0].get_pad('sink')))

        slicer = bin.get_by_name('slicer')
        capsfilter = bin.get_by_name('capsfilter')
        for p in params:
            name, value = p.split('=')
            if name == 'width':
                caps = Gst.caps_from_string('video/x-raw-rgb,%s' % p)
                capsfilter.set_property('caps', caps)
            else:
                slicer.set_property(name, int(value))
        player.props.video_sink=bin
    else:
        player = Gst.parse_launch('videotestsrc ! videoscale ! videoconvert ! slicebuffer %s ! videoconvert ! autovideosink' % " ".join(params))
        bin = player

    pipe=player
    overlay=bin.get_by_name('overlay')


    def on_msg(bus, msg):
        s = msg.get_structure()
        if s is None:
            return True
        if s.has_field('gerror'):
            logger.error("MSG %s", s['debug'])

    def on_eos (bus, msg):
        mainloop.quit()
    bus = pipe.get_bus()
    bus.add_signal_watch()
    bus.connect('message::eos', on_eos)
    bus.connect('message', on_msg)

    logger.info("PLAYING")
    pipe.set_state (Gst.State.PLAYING)

    try:
        mainloop.run()
    except:
        pass

    pipe.set_state (Gst.State.NULL)
