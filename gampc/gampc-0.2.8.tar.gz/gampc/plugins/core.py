# coding: utf-8
#
# Graphical Asynchronous Music Player Client
#
# Copyright (C) 2015 Itaï BEN YAACOV
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from gi.repository import GLib

import ampd

from gampc import plugin
from gampc.utils import action
from gampc.utils import omenu


class CoreExtension(plugin.Extension):
    def activate(self):
        self.ampd = self.shared.ampd
        self.fading = False
        self.provides['app'] = {}
        self.provides['app']['actions'] = [
            action.PropertyAction('restricted', self.shared),
            action.PropertyAction('dark', self.shared),
            action.PropertyAction('server-profile', self.shared),
            action.ActionModel('connect', self.shared.ampd_connect),
            action.ActionModel('disconnect', self.shared.ampd_disconnect),
            action.ActionModel('play-or-pause', self.play_or_pause_cb, restrict=True),
            action.ActionModel('absolute-jump', self.absolute_jump_cb, restrict=True, parameter_type=GLib.VariantType.new('i')),
            action.ActionModel('relative-jump', self.relative_jump_cb, restrict=True, parameter_type=GLib.VariantType.new('i')),
        ] + [
            action.ActionModel(name, self.mpd_command_cb, restrict=True) for name in
            ('play', 'stop', 'next', 'previous')
        ] + [
            action.ActionModel(name, self.mpd_command_cb) for name in
            ('update',)
        ] + [action.ActionModel('fade-to-' + name, self.fade_to_action_cb) for name in ('next', 'stop')] + [action.PropertyAction('option-' + option, self.shared.ampd_server_properties) for option in self.shared.ampd_server_properties.OPTION_NAMES]

        self.provides['app']['menubar_items'] = [
            omenu.Item('10#gampc/20#misc/50', 'app.restricted', _("Restricted mode"), ['<Control><Alt><Shift>s']),
            omenu.Item('10#gampc/20#misc/60', 'app.dark', _("Dark interface"), ['<Control><Alt><Shift>d']),
            omenu.Item('30#playback/10#play/10', 'app.play-or-pause', _("_Play/pause"), ['<Control>Up', 'AudioPlay', 'space'], accels_fragile=True),
            omenu.Item('30#playback/10#play/20', 'app.stop', _("_Stop"), ['<Control>Down', 'AudioStop'], accels_fragile=True),
            omenu.Item('30#playback/10#play/30', 'app.fade-to-stop', _("Fade to stop"), ['<Control><Shift>Down', '<Shift>AudioStop'], accels_fragile=True),
            omenu.Item('30#playback/20#move/10', 'app.previous', _("_Previous"), ['<Control>Left', 'AudioPrev'], accels_fragile=True),
            omenu.Item('30#playback/20#move/20', 'app.next', _("_Next"), ['<Control>Right', 'AudioNext'], accels_fragile=True),
            omenu.Item('30#playback/20#move/30', 'app.fade-to-next', _("_Fade to next"), ['<Control><Shift>Right'], accels_fragile=True),
            omenu.Item('30#playback/30#jump/10', 'app.absolute-jump(0)', _("Restart playback"), ['<Alt>Up']),
            omenu.Item('30#playback/30#jump/20', 'app.absolute-jump(-15)', _("End of song (-{} seconds)").format(15), ['<Alt>Down']),
            omenu.Item('30#playback/30#jump/30', 'app.relative-jump(-5)', _("Skip backwards ({} seconds)").format(5), ['<Alt>Left'], accels_fragile=True),
            omenu.Item('30#playback/30#jump/40', 'app.relative-jump(5)', _("Skip forwards ({} seconds)").format(5), ['<Alt>Right'], accels_fragile=True),
            omenu.Item('40#server/10#database/10', 'app.update', _("Update database")),
            omenu.Item('40#server/20#options/10', 'app.option-random', _("Random mode")),
            omenu.Item('40#server/20#options/20', 'app.option-repeat', _("Repeat mode")),
            omenu.Item('40#server/20#options/30', 'app.option-consume', _("Consume mode")),
            omenu.Item('40#server/20#options/40', 'app.option-single', _("Single mode")),
            omenu.Item('40#server/40#connection/10', 'app.connect', _("Connect"), ['<Alt><Shift>c']),
            omenu.Item('40#server/40#connection/20', 'app.disconnect', _("Disconnect"), ['<Alt><Shift>d']),
        ]

    @ampd.task
    async def mpd_command_cb(self, caller, *data):
        if not self.shared.ampd_server_properties.state:
            await self.ampd.idle(ampd.IDLE)
        await getattr(self.ampd, caller.get_name())()

    @ampd.task
    async def play_or_pause_cb(self, action_, parameter):
        if not self.shared.ampd_server_properties.state:
            await self.ampd.idle(ampd.IDLE)
        await (self.ampd.pause(1) if self.shared.ampd_server_properties.state == 'play' else self.ampd.play())

    @ampd.task
    async def fade_to_action_cb(self, action_, parameter):
        if self.fading:
            return
        try:
            self.fading = True
            N = 30
            T = 5

            if not self.shared.ampd_server_properties.state:
                await self.ampd.idle(ampd.IDLE)
            if self.shared.ampd_server_properties.state != 'play':
                return
            volume = self.shared.ampd_server_properties.volume
            for i in range(N):
                self.shared.ampd_server_properties.volume = volume * (N - i - 1) / N
                reply = await self.ampd.idle(ampd.PLAYER, timeout=T / N)
                if reply & ampd.PLAYER:
                    break
            else:
                await getattr(self.ampd, action_.get_name()[8:])()
            self.shared.ampd_server_properties.volume = volume
        finally:
            self.fading = False

    def absolute_jump_cb(self, action_, parameter):
        target = parameter.unpack()
        if self.shared.ampd_server_properties.state != 'stop':
            self.shared.ampd_server_properties.elapsed = target if target >= 0 else self.shared.ampd_server_properties.time + target

    def relative_jump_cb(self, action_, parameter):
        if self.shared.ampd_server_properties.state != 'stop':
            self.shared.ampd_server_properties.elapsed += parameter.unpack()
