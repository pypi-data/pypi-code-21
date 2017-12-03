#!/usr/bin/python
# -*- coding: utf-8 -*-
from kivy.uix.button import Button
from kivy.graphics import BorderImage
from ConfigParser import SafeConfigParser
import os

_thisfiledir=os.path.dirname(os.path.abspath(__file__))
_parser = SafeConfigParser()
_parser.read(['%s/config.cfg' % _thisfiledir, os.path.expanduser("~/.getradiourl/config.cfg")])

class ConfConstants(object):
    screen_size=eval(_parser.get('common', 'screen_size'))
    selected_image="%s/%s" % (_thisfiledir, _parser.get('common', 'selected_image'))
    normal_image="%s/%s" % (_thisfiledir, _parser.get('common', 'normal_image'))
    general_bg_color=eval(_parser.get('common', 'general_bg_color'))
    general_text_color=eval(_parser.get('common', 'general_text_color'))
    emphasized_text_color=eval(_parser.get('common', 'emphasized_text_color'))
    bt_text_color=eval(_parser.get('common', 'bt_text_color'))
    screen_bg_color=eval(_parser.get('common', 'screen_bg_color'))
    adevice=_parser.get('getradiourl', 'audio_device')
    # count up playtimes when a station is played longer than this time in seconds
    playtime_criterion=_parser.getfloat('radiovy', 'playtime_criterion')
    stations_in_one_scroll=_parser.getint('radiovy', 'stations_in_one_scroll')
    stations_list_selected_color=eval(_parser.get('radiovy', 'stations_list_selected_color'))
    stations_list_deselected=eval(_parser.get('radiovy', 'stations_list_deselected'))
    radio_top_text_color=eval(_parser.get('radiovy', 'radio_top_text_color'))
    stations_list_text_color=eval(_parser.get('radiovy', 'stations_list_text_color'))
    play_image="%s/%s" % (_thisfiledir, _parser.get('radiovy', 'play_image'))
    pause_image="%s/%s" % (_thisfiledir, _parser.get('radiovy', 'pause_image'))

class HkBaseButton(Button):
    def __init__(self, selected_text="", not_selected_text="", **kwargs):
        if not kwargs.has_key('text'): kwargs['text']=not_selected_text
        if not kwargs.has_key('color'): kwargs['color']=ConfConstants.bt_text_color
        super(HkBaseButton, self).__init__(**kwargs)
        self.background_selected=ConfConstants.selected_image
        self.background_normal=ConfConstants.normal_image
        self.default_background_normal=self.background_normal
        self.selected_text=selected_text
        self.not_selected_text=not_selected_text

    def set_selected(self, selected):
        if selected:
            self.text=self.selected_text
            self.background_normal=self.background_selected
        else:
            self.text=self.not_selected_text
            self.background_normal=self.default_background_normal

