#!/usr/bin/python
# -*- coding: utf-8 -*-
# radiovy.py
# python gui module to play internet radio stations
#
# Copyright (C) 2017 Shiro Ninomiya
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
#
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.config import Config
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivy.uix.scrollview import ScrollView
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.listview import ListView, ListItemButton
from kivy.graphics import Color, Rectangle, Point, GraphicException
import datetime, time
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.logger import Logger
import sys
from hkbase.hkbase import ConfConstants, HkBaseButton
from getradiourl.getradiourl import StationMan
from getradiourl.gstplayer import GstAplay

_radio_station_man=None

class MarkGenreButton(HkBaseButton):
    def __init__(self, gstpage, **kwargs):
        super(MarkGenreButton, self).__init__(**kwargs)
        self.gstpage=gstpage
        
    def on_release(self):
        if self.gstpage.genre.favorite:
            self.gstpage.genre.favorite=0
        else:
            self.gstpage.genre.favorite=1
        self.set_selected(self.gstpage.genre.favorite)
        _radio_station_man.genre_update(self.gstpage.genre)
        # re-create genres screen to change the order to show genres
        self.gstpage.raman.create_genres_screen()


class MarkStationButton(HkBaseButton):
    def __init__(self, gstpage, **kwargs):
        super(MarkStationButton, self).__init__(**kwargs)
        self.gstpage=gstpage

    def on_release(self):
        # favorite, 0:never favorite, 1:once favorite but removed, 2:now favorite
        if not self.gstpage.raman.playing_station: return
        if self.gstpage.raman.playing_station.favorite>1:
            self.gstpage.raman.playing_station.favorite=1
        else:
            self.gstpage.raman.playing_station.favorite=2
        self.update_text()
        _radio_station_man.station_update(self.gstpage.raman.playing_station)
        self.gstpage.stselect_pane.lupdate()

    def update_text(self):
        self.set_selected(self.gstpage.raman.playing_station and \
                          self.gstpage.raman.playing_station.favorite>1)
        if not self.gstpage.raman.playing_station:
            self.text="no playing station"
            
class StationsPageSelect(BoxLayout):
    def __init__(self, max_page, **kwargs):
        super(StationsPageSelect, self).__init__(**kwargs)
        self.bnum=int((self.width - 2)/70) # min. button width=70
        bw=int((self.width - 2)/self.bnum) # 2 is padding_right
        gt=self.width - 2 - bw*self.bnum
        if gt>=(self.bnum-2):
            self.pb_width=bw-1
            self.pa_width=bw-1
        else:
            self.pb_width=bw-2
            self.pa_width=bw-1+gt/2
        self.bnum-=2
        self.padding[2]+=gt%2
        self.spacing=2            
        self.sbp=0
        self.max_page=max_page
        self.pbuttons=[]

        la=HkBaseButton(text="<", font_size=30, size_hint=(None, 1), width=self.pa_width)
        la.bind(on_release=self.ppage)
        self.add_widget(la)
        
        for i in range(self.bnum):
            bt=self.ptext(i)
            b=HkBaseButton(text=bt, font_size=30, size_hint=(None, 1), width=self.pb_width)
            b.bind(on_release=self.ipage)
            self.add_widget(b)
            self.pbuttons.append(b)
            
        ra=HkBaseButton(text=">", font_size=30, size_hint=(None, 1), width=self.pa_width)
        ra.bind(on_release=self.npage)
        self.add_widget(ra)

    def ptext(self, n):
        if n < self.max_page:
                return "%d" % (n + 1)
        return ""
        
    def ppage(self, btn):
        if self.sbp>0:
            self.sbp-=self.bnum
            if self.sbp<0: self.sbp=0
        for i, b in enumerate(self.pbuttons):
            bt=self.ptext(self.sbp+i)
            b.text=bt

    def npage(self, btn):
        if self.sbp < self.max_page-self.bnum:
            self.sbp+=self.bnum
        for i, b in enumerate(self.pbuttons):
            bt=self.ptext(self.sbp+i)
            b.text=bt

    def ipage(self, btn):
        if btn.text=="": return
        self.parent.update_stlist_page(int(btn.text))

class StationListItemButton(ListItemButton):
    selected_color = ConfConstants.stations_list_selected_color
    deselected_color = ConfConstants.stations_list_deselected
    color = ConfConstants.stations_list_text_color

class StationSelectLayout(BoxLayout):
    stitem_height=50
    def __init__(self, **kwargs):
        super(StationSelectLayout, self).__init__(**kwargs)
        self.one_list_num=ConfConstants.stations_in_one_scroll
        self.lstart=0
        self.lscroll=None
        self.page_select=None

    def update_stlist_page(self, page):
        self.lstart=(page-1)*self.one_list_num
        self.stlist_view.adapter=self.stlist_update()
        self.scroll_to_playing_station()

    def scroll_to_playing_station(self):
        self.stlist_view.scroll_to(0)
        if self.stlist_view.height:
            self.lscroll.scroll_y = 1.0 -  float(self.next_top_index) * \
                                    self.stitem_height/self.stlist_view.height
        else:
            self.lscroll.scroll_y = 1.0

    def stlist_update(self):
        self.lstds=self.stations[self.lstart:self.lstart+self.one_list_num]
        stlist_adapter=ListAdapter(data=self.lstds,
                                   args_converter=self.list_item_args_converter,
                                   selection_mode='single',
                                   allow_empty_selection=True,
                                   cls=StationListItemButton)
        # set up the initial selection
        self.next_top_index=0
        for i,s in enumerate(self.lstds):
            if self.parent.raman.playing_station==s:
                stlist_adapter.handle_selection(stlist_adapter.get_view(i))
                self.next_top_index=i
                break;
        stlist_adapter.bind(on_selection_change=self.parent.station_selected)
        return stlist_adapter

    def list_item_args_converter(self, row_index, selectable):
        return {'text': selectable.description,
                'size_hint_y': None,
                'height': self.stitem_height}
        
    def lupdate(self):
        self.lstart=0
        if self.lscroll:
            self.remove_widget(self.lscroll)
        if self.page_select:
            self.remove_widget(self.page_select)
        self.lscroll=ScrollView(size_hint=(1, None), do_scroll_x=False, width=self.width)
        lcontainer=BoxLayout(size_hint=(1, None), do_scroll_x=False, width=self.width,
                             orientation='vertical')
        self.stations = _radio_station_man.sorted_stations_favorite_playtimes(
            self.parent.genre.name)
        self.num_station=len(self.stations)
        if self.num_station <= self.one_list_num:
            # fit in one list
            self.page_select=None
            self.lscroll.height=ConfConstants.screen_size[1]
        else:
            self.page_select=StationsPageSelect(
                max_page=(self.num_station+self.one_list_num-1)/self.one_list_num,
                size_hint=(None, None), orientation='horizontal',
                width=self.width, height=80, padding=[0,0,2,0])
            self.lscroll.height=ConfConstants.screen_size[1]-80

        self.stlist_view=ListView(adapter=self.stlist_update(), size_hint=(1,None),
                                  width=self.width, height=len(self.lstds)*self.stitem_height,
                                  container=lcontainer)
        self.scroll_to_playing_station()
        self.lscroll.add_widget(lcontainer)
        self.add_widget(self.lscroll)
        if self.page_select:
            self.add_widget(self.page_select)
    
class GenreStationsPage(BoxLayout):
    list_width=0.625*ConfConstants.screen_size[0]
    def __init__(self, genrebt, **kwargs):
        super(GenreStationsPage, self).__init__(**kwargs)
        self.genrebt=genrebt
        self.raman=genrebt.raman
        self.genre=genrebt.genre
        self.stg_width=ConfConstants.screen_size[0]-self.list_width
        with self.canvas.before:
            Color(*ConfConstants.general_bg_color)
            Rectangle(size=self.size)
            
        self.stselect_pane=StationSelectLayout(orientation='vertical', size_hint=(None, None),
                                               width=self.list_width,
                                               height=ConfConstants.screen_size[1])
        stginfo_pane=BoxLayout(orientation='vertical', size_hint=(None, None),
                               width=self.stg_width, height=ConfConstants.screen_size[1],
                               spacing=2)
        self.add_widget(self.stselect_pane)
        self.add_widget(stginfo_pane)
        self.stselect_pane.lupdate()
        self.stg_infoview(stginfo_pane)

    def stg_infoview(self, stginfo_pane):
        fsize = 40 if len(self.genre.name)<=12 else 30
        genre_title=Label(text=self.genre.name, color=ConfConstants.general_text_color,
                          font_size=fsize, size_hint=(1,None), height=50)
        stginfo_pane.add_widget(genre_title)
        genre_desc=Label(text=self.genre.description, color=ConfConstants.general_text_color,
                         font_size=20, size_hint=(1, None), text_size=(self.stg_width-10, None),
                         valign='top', halign='left')
        genre_desc.texture_update()
        genre_desc.height=genre_desc.texture_size[1]
        gscroll=ScrollView(size_hint=(1, 1), do_scroll_x=False,
                           width=self.stg_width)
        gscroll.add_widget(genre_desc)
        stginfo_pane.add_widget(gscroll)

        self.genre_favorite=MarkGenreButton(gstpage=self,
                                            selected_text="this genre is marked",
                                            not_selected_text="mark this genre",
                                            size_hint=(1,None), height=80, font_size=20)
        self.genre_favorite.set_selected(self.genre.favorite)
        stginfo_pane.add_widget(self.genre_favorite)

        self.station_favorite=MarkStationButton(gstpage=self,
                                                selected_text="playing station is marked",
                                                not_selected_text="mark playing station",
                                                size_hint=(1,None),
                                                height=80, font_size=20)
        self.station_favorite.update_text()
        stginfo_pane.add_widget(self.station_favorite)

        back_buttons=BoxLayout(orientation='horizontal', size_hint=(1,None), height=80,
                               spacing=2)
        back_to_genre=HkBaseButton(text="Back\nGenre", font_size=20)
        back_to_genre.bind(on_release=self.back_to_genre)
        back_to_top=HkBaseButton(text="Back\nTop", font_size=20)
        back_to_top.bind(on_release=self.back_to_top)
        back_buttons.add_widget(back_to_top)
        back_buttons.add_widget(back_to_genre)
        stginfo_pane.add_widget(back_buttons)

    def station_playing_close(self):
        if self.raman.gstaplay.get_state()=='init': return
        if self.raman.gstaplay.close() < ConfConstants.playtime_criterion: return
        self.raman.playing_station.playtimes += 1
        _radio_station_man.station_update(self.raman.playing_station)
                
    def station_selected(self, adapter, *args):
        self.raman.delete_backup_page()
        if len(adapter.selection):
            if self.raman.playing_station:
                if self.raman.playing_station.description == adapter.selection[0].text:
                    return # continue to play the same station
                self.station_playing_close()
                    
            self.raman.playing_station = _radio_station_man.get_station_by_desc(
                adapter.selection[0].text)
            if self.raman.playing_genrebt: self.raman.playing_genrebt.set_selected(False)
            self.raman.playing_genrebt = self.genrebt
            self.station_favorite.update_text()            
            if not self.raman.playing_station or not self.raman.playing_station.urlst:
                # show it is not playable
                self.raman.playing_genrebt = None
                return
            self.genrebt.set_selected(True)
            if self.raman.playing_station.urlst:
                self.raman.gstaplay.open(self.raman.playing_station.urlst)
                self.raman.gstaplay.play()
                Logger.info("play  '%s'" % self.raman.playing_station.urlst)
            return
        if self.raman.playing_station:
            self.station_playing_close()
            Logger.info("stop  playing")
            self.raman.playing_station = None
            self.raman.playing_genrebt = None
            self.genrebt.set_selected(False)
            self.station_favorite.update_text()     
        
    def back_to_genre(self, btn):
        self.raman.scm.current='genres'
        
    def back_to_top(self, btn):
        if self.raman.scm.has_screen('radio_top'):
            self.raman.tw.status_update()
            self.raman.scm.current='radio_top'
        
class GenreButton(HkBaseButton):
    def __init__(self, raman, radiosm, genre, **kwargs):
        super(GenreButton, self).__init__(**kwargs)
        self.raman=raman
        self.genre=genre

    def on_release(self):
        if self.raman.scm.has_screen('stations'):
            if self.raman.gstations_page and self.raman.gstations_page.genre == self.genre:
                # re-visiting the same page
                self.raman.scm.current='stations'
                return
        self.raman.switch_to_stations_page(self)

class GenresLayout(StackLayout):
    def __init__(self, raman, **kwargs):
        super(GenresLayout, self).__init__(**kwargs)
        self.raman=raman
        sw=0
        sh=0
        for g in _radio_station_man.sorted_genres_favorite():
            b=GenreButton(raman=self.raman, radiosm=_radio_station_man, genre=g,
                          selected_text=g.name, not_selected_text=g.name,
                          font_size=30, size_hint=(None,None),
                          width=20+len(g.name)*20, height=80)
            self.add_widget(b)
            sw+=b.width
            if(sw > self.width):
                sw=b.width
                sh+=b.height
        sh+=b.height
        self.height=sh
    
class GenresWidget(BoxLayout):
    def __init__(self, raman, **kwargs):
        super(GenresWidget, self).__init__(**kwargs)
        self.raman=raman
        with self.canvas.before:
            Color(*ConfConstants.screen_bg_color)
            Rectangle(size=self.size)
        scrollv=ScrollView(size_hint=(1, None), size=self.size, do_scroll_x=False)
        self.add_widget(scrollv)
        genres_buttons=GenresLayout(raman=self.raman, width=self.size[0], size_hint_y=None, \
                                    spacing=(2,2))
        scrollv.add_widget(genres_buttons)
        
class UpdateDbox(BoxLayout):
    def __init__(self, **kwargs):
        super(UpdateDbox, self).__init__(**kwargs)
        with self.canvas.before:
            Color(*ConfConstants.general_bg_color)
            Rectangle(size=self.size, pos=self.pos)
        
class UpdateModal(ModalView):
    left_col_size=200
    not_selected_genre="not selected"
    def __init__(self, raman, selected_genre, need_st=False, **kwargs):
        super(UpdateModal, self).__init__(**kwargs)
        self.raman=raman
        self.right_col_size=self.width-self.left_col_size
        self.sgname=selected_genre if selected_genre else self.not_selected_genre
        self.need_st="\n(need this)" if need_st else ""

    def on_open(self):
        dbox=UpdateDbox(size=self.size, pos=self.pos, orientation='vertical')
        tbox=GridLayout(size_hint=(1, 1), cols=2, padding=[0,5,2,5], spacing=(0,20))
        desc_text=[("Udate Genres:","Update genres information."
                   " This may take a few minutes."),
                   ("Udate Stations:%s" % self.need_st,
                   "Update stations information for the selected genre."
                   " This may take a few minutes to several tens of minutes."
                   " For a big genre like 'pop', it will take quite a long time.\n"
                   "Selected genre = '%s'" % self.sgname),
                   ("Udate All:","Update stations information for all genres."
                    " This may take a few HOURS. Be careful to run this")]
        for i,t in enumerate(desc_text):
            if self.need_st and i==1:
                tc=ConfConstants.emphasized_text_color
            else:
                tc=ConfConstants.general_text_color
            desc=Label(text=t[0], font_size=26, size_hint=(None, 1), width=self.left_col_size,
                       color=tc, halign='left', valign='middle')
            desc.texture_update()
            #desc.height=desc.texture_size[1]
            tbox.add_widget(desc)
            desc=Label(text=t[1], font_size=20, size_hint=(1, None),
                       text_size=(self.right_col_size, None),
                       color=ConfConstants.general_text_color, halign='left', valign='top')
            desc.texture_update()
            desc.height=desc.texture_size[1]
            desc.text_size[1]=desc.height
            tbox.add_widget(desc)
            
        bbox=BoxLayout(orientation='horizontal', size_hint=(1, None), height=80)
        self.btexts=["Update\nGenres", "Update\nStations", "Update\nAll", "Done"]
        for i,t in enumerate(self.btexts):
            b=HkBaseButton(text=t, font_size=30, halign='center')
            b.idnum=i
            b.bind(on_release=self.run_update)
            bbox.add_widget(b)
            
        dbox.add_widget(tbox)
        dbox.add_widget(bbox)
        self.add_widget(dbox)

    def run_update(self, btn):
        if btn.idnum==3:
            if self.parent:
                self.parent.remove_widget(self)
            else:
                self.dismiss()
            return
        elif btn.idnum==0:
            Logger.info("start list_of_genres_update")
            _radio_station_man.list_of_genres_update(renew_update=True)
            Logger.info("done")
            self.raman.create_genres_screen()
            return
        elif btn.idnum==1:
            if self.sgname==self.not_selected_genre: return
            Logger.info("start update_genres_playlist_url for %s, num=%d" % (
                self.sgname, _radio_station_man.num_of_stations_in_genre(self.sgname)))
            _radio_station_man.update_genres_playlist_url(update_genres=[self.sgname],
                                                          renew_update=True)
            Logger.info("start update_genres_station_urls for %s" % self.sgname)
            _radio_station_man.update_genres_station_urls(update_genres=[self.sgname],
                                                          renew_update=True)
            Logger.info("done for %s, num=%d" % (
                self.sgname, _radio_station_man.num_of_stations_in_genre(self.sgname)))
        elif btn.idnum==2:
            Logger.info("start update_genres_playlist_url for all")
            _radio_station_man.update_genres_playlist_url(update_genres=[],
                                                          renew_update=True)
            Logger.info("start update_genres_station_urls for all")
            _radio_station_man.update_genres_station_urls(update_genres=[],
                                                          renew_update=True)
            Logger.info("done")
        else:
            return
        self.raman.re_init()

class PlayPauseButton(Button):
    def set_play(self):
        self.background_normal=ConfConstants.play_image
    def set_pause(self):
        self.background_normal=ConfConstants.pause_image

    
class RadioTopWidget(FloatLayout):
    def __init__(self, raman, **kwargs):
        super(RadioTopWidget, self).__init__(**kwargs)
        self.raman=raman
        with self.canvas.before:
            Color(*ConfConstants.screen_bg_color)
            Rectangle(size=self.size)
        l=Label(text="Radiovy", font_size=80, size_hint=(0.4,0.2), pos_hint={'x':.3, 'y':.5},
                color=ConfConstants.radio_top_text_color)
        self.add_widget(l)
        
        self.play_pause=PlayPauseButton(text="", font_size=40, size_hint=(0.25,0.15),
                                     pos_hint={'x':.37, 'y':.35})
        self.play_pause.bind(on_release=self.control_play)
        
        self.status=Label(text="", font_size=30, halign='left',
                          size_hint=(0.9, 0.32), pos_hint={'x':.05, 'y':.1},
                          color=ConfConstants.radio_top_text_color)
        self.add_widget(self.status)
        
        gb=HkBaseButton(text="genres", font_size=40, size_hint=(0.24,0.1),
                        pos_hint={'x':.5, 'y':.0})
        gb.bind(on_release=self.goto_genres)
        self.add_widget(gb)
        
        sb=HkBaseButton(text="stations", font_size=40, size_hint=(0.24,0.1),
                        pos_hint={'x':.75, 'y':.0})
        sb.bind(on_release=self.goto_stations)
        self.add_widget(sb)

        ub=HkBaseButton(text="Update Genres/STs", font_size=40, size_hint=(0.48,0.1),
                        pos_hint={'x':.01, 'y':.0})
        ub.bind(on_release=self.update_dialogue)
        self.add_widget(ub)

    def update_play_pause_state(self, btn):
        if self.raman.gstaplay.get_state()=='init' or not self.raman.playing_station:
            if not btn.parent: return
            self.remove_widget(btn)
            return
        if not btn.parent:
            self.add_widget(btn)
        if self.raman.gstaplay.get_state()=='playing':
            btn.set_pause()
        else:
            btn.set_play()

    def control_play(self, btn):
        if self.raman.gstaplay.get_state()=='ready':
            self.raman.gstaplay.play()
        elif self.raman.gstaplay.get_state()=='playing':
            self.raman.gstaplay.pause()
        self.update_play_pause_state(btn)

    def goto_genres(self, btn):
        if self.raman.scm.has_screen('genres'):
            self.raman.scm.current='genres'

    def goto_stations(self, btn):
        self.raman.recover_stations_page()
        if self.raman.scm.has_screen('stations'):
            self.raman.scm.current='stations'

    def update_dialogue(self, btn):
        selected_genre = self.raman.gstations_page.genre.name \
                         if self.raman.gstations_page else None
        update_modal=UpdateModal(self.raman, selected_genre,
                                 size_hint=(None,None), size=(660,360),
                                 auto_dismiss=False)
        update_modal.open()
            
    def status_update(self):
        gs=""
        ss=""
        gs=self.raman.playing_genrebt.genre.name if self.raman.playing_genrebt else ""
        ss=self.raman.playing_station.description if self.raman.playing_station else ""
        self.status.text="Playing\nGenre: %s\nStation: %s" % (gs, ss)
        self.status.text_size=self.status.size
        self.update_play_pause_state(self.play_pause)

class RadioMan(object):
    def __init__(self, scm):
        global _radio_station_man
        self.scm=scm
        self.playing_station=None
        self.playing_genrebt=None
        self.gstations_page=None
        _radio_station_man=StationMan(Logger)
        self.gstaplay=GstAplay(adevice=ConfConstants.adevice)
        
        if not self.scm.has_screen('radio_top'):
            self.create_top_screen()
            
        if not self.scm.has_screen('genres'):
            self.create_genres_screen()
        self.scm.current='radio_top'

    def close(self):
        global _radio_station_man
        Logger.info("RadioMan closing")
        self.gstaplay.close()
        for scname in ['stations', 'genres', 'radio_top']:
            if self.scm.has_screen(scname):
                self.scm.remove_widget(self.scm.get_screen(scname))
        _radio_station_man.close()
        _radio_station_man=None

    def re_init(self, init_genre=False):
        if init_genre: self.create_genres_screen()
        self.delete_backup_page()
        self.playing_station=None
        self.playing_genrebt=None
        if self.scm.has_screen('stations'):
            self.scm.remove_widget(self.scm.get_screen('stations'))
        self.gstations_page=None

    def create_genres_screen(self):
        if self.scm.has_screen('genres'):
            self.scm.remove_widget(self.scm.get_screen('genres'))
        genres_screen=Screen(name='genres')
        self.gw=GenresWidget(self, size=ConfConstants.screen_size)
        genres_screen.add_widget(self.gw)
        self.scm.add_widget(genres_screen)

    def create_top_screen(self):
        top_screen=Screen(name='radio_top')
        self.tw=RadioTopWidget(self, size=ConfConstants.screen_size)
        top_screen.add_widget(self.tw)
        self.scm.add_widget(top_screen)

    def delete_backup_page(self):
        if not self.scm.has_screen('playing_stations'): return
        pgstpage=self.scm.get_screen('playing_stations')
        self.scm.remove_widget(pgstpage)
        Logger.info("deleted 'playing_stations' screen")
        
    def backup_stations_page(self):
        # when it is not playing, the backup is not needed
        if not self.playing_station: return False
        # when it was already backed up, don't overwrite it
        if self.scm.has_screen('playing_stations'): return False
        pgstpage=self.scm.get_screen('stations')
        self.scm.remove_widget(pgstpage)
        self.gstations_page=None
        pgstpage.name='playing_stations'
        self.scm.add_widget(pgstpage)
        Logger.info("'stations' backed up to 'playing_stations'")
        return True

    def recover_stations_page(self):
        if not self.scm.has_screen('playing_stations'): return False
        pgstpage=self.scm.get_screen('playing_stations')
        self.scm.remove_widget(pgstpage)
        self.gstations_page=None
        if self.scm.has_screen('stations'):
            self.scm.remove_widget(self.scm.get_screen('stations'))
        pgstpage.name='stations'
        self.scm.add_widget(pgstpage)
        Logger.info("'stations' recovered from 'playing_stations'")
        return True

    def switch_to_stations_page(self, genrebt):
        if self.scm.has_screen('stations'):
            if self.playing_genrebt == genrebt:
                self.recover_stations_page()
            else:
                if not self.backup_stations_page():
                    self.scm.remove_widget(self.scm.get_screen('stations'))
                
        if not self.scm.has_screen('stations'):
            if _radio_station_man.num_of_stations_in_genre(genrebt.genre.name)==0:
                # no stations data in the genre
                update_modal=UpdateModal(self, selected_genre = genrebt.genre.name,
                                         need_st=True,
                                         size_hint=(None,None), size=(660,360),
                                         auto_dismiss=False)
                update_modal.open()
                return
            stations_screen=Screen(name='stations')
            Logger.info("created new 'stations' screen")
            self.gstations_page=GenreStationsPage(genrebt, orientation='horizontal',
                                                  size=ConfConstants.screen_size)
            stations_screen.add_widget(self.gstations_page)
            self.scm.add_widget(stations_screen)
            
        self.scm.current='stations'
            
        
class RadiovyApp(App):
    def __init__(self, **kwargs):
        super(RadiovyApp, self).__init__(**kwargs)
        self.rm=None
        
    def build(self):
        scm=ScreenManager()
        self.rm=RadioMan(scm)
        return scm

    def on_stop(self):
        self.rm.close()
    
def main():
    Config.set('graphics', 'width',  ConfConstants.screen_size[0])
    Config.set('graphics', 'height', ConfConstants.screen_size[1])
    app=RadiovyApp()
    app.run()

if __name__ == '__main__':
    main()
        
