#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# getradiourl.py
# python module to get internet radio station URLs from a public internet site
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

from ZODB import FileStorage, DB
from persistent import Persistent
import transaction
import datetime
import urllib2
import re
import hashlib
import os
import logging
import sys

#
# baseurl (base url of the internet site to get radio stations info.)
#   genres (a list of genres which is obtained from 'baseurl')
#     genre (one genre, this has a list of stations)
#       playlist_url (url of the playlist file)
#       station_url (url of to play the station, which is in the above playlist file
#
# 1) download genres data
#    it is saved into 'GenreDb'
# 2) get a stations list for a genre by going through 'baseurl/genre/[pageN]'
#    playlist_url is obtained fromt he page data
#    it is saved into 'StationDb'
# 3) get station_url by going thourh the stations list
#    the playlist is downloaded from 'playlist_url'
#    station_url is obtained from the downloaded data
#    it updates 'StationDb'
# 4) repeat 2)-3) for genres
#

NOT_ACCESSIBLE_THRESH = 1
DATA_SAVE_DIR = "%s/.getradiourl" % os.path.expanduser("~")
module_logger=logging.getLogger(__name__)

class RadioDb(object):
    def __init__(self, path):
        self.storage = FileStorage.FileStorage(path)
        self.db = DB(self.storage)
        self.connection = self.db.open()
        self.dbroot = self.connection.root()

    def close(self):
        self.connection.close()
        self.db.close()
        self.storage.close()
        
    def update_item(self, item):
        item.lastupdatetime = datetime.datetime.now()
        if self.dbroot.has_key(item.name):
            if item.regorder!=0:
                # if new regorder, update it
                self.dbroot[item.name].regorder = item.regorder
            # update lastupdatetime
            self.dbroot[item.name].lastupdatetime = item.lastupdatetime
            # keep all the other items
            transaction.commit()
            return
        if item.regorder==0: item.regorder=len(self.dbroot)+1
        self.dbroot[item.name] = item
        transaction.commit()

class GenreDb(RadioDb):
    pass
        
class StationDb(RadioDb):
    def get_one_genre(self, genre):
        retd=[]
        for sd in self.dbroot.values():
            if genre in sd.genre: retd.append(sd)
        return retd
    
    def update_item(self, item):
        if self.dbroot.has_key(item.name):
            std=self.dbroot[item.name]
            std.urlpls=item.urlpls
            std.urlst=item.urlst
            std.genre=tuple(set(std.genre) | set(item.genre))
        super(StationDb, self).update_item(item)
        
class RadioBaseData(Persistent):
    def __init__(self, name, description, lastupdatetime=None,
                 accesstimes=0, favorite=0):
        self.name=name
        self.description=description
        self.lastupdatetime=lastupdatetime
        self.accesstimes=accesstimes
        self.favorite=favorite
        self.regorder=0

    @classmethod
    def sort_by_lastupdatetime(cls, ds):
        # later access comes first
        rocomp=lambda x,y: cmp(y.lastupdatetime, x.lastupdatetime)
        return [i for i in sorted(ds, rocomp)]
    
    @classmethod
    def sort_by_regorder(cls, ds):
        rocomp=lambda x,y: cmp(x.regorder, y.regorder)
        return [i for i in sorted(ds, rocomp)]
    
    @classmethod
    def sort_by_favorite(cls, ds):
        # higher favorite comes first
        rocomp=lambda x,y: cmp(y.favorite, x.favorite)
        return [i for i in sorted(ds, rocomp)]

class GenreData(RadioBaseData):
    pass

class StationData(RadioBaseData):
    def __init__(self, name, description, genre, urlpls, urlst=None,
                 lastplay=None, playtimes=0):
        super(StationData, self).__init__(name, description)
        self.genre=(genre,)
        self.urlpls=urlpls
        self.urlst=urlst
        self.lastplay=lastplay
        self.playtimes=playtimes
        self.noaccess=0
        
    @classmethod
    def sort_by_playtimes(cls, ds):
        # more playtimes comes first
        rocomp=lambda x,y: cmp(y.playtimes, x.playtimes)
        return [i for i in sorted(ds, rocomp)]

class StationMan(object):
    def __init__(self, logger=None, baseurl="https://www.internet-radio.com/stations/",
                 update_genres=None):
        global module_logger
        if logger: module_logger=logger
        if not os.path.exists(DATA_SAVE_DIR): os.makedirs(DATA_SAVE_DIR)
        self.baseurl=baseurl
        self.genres=GenreDb('/'.join([DATA_SAVE_DIR,'radio_genres.fs']))
        self.stations=StationDb('/'.join([DATA_SAVE_DIR,'radio_stations.fs']))
        self.genres_num=0
        self.list_of_genres_update()
        if self.genres_num and len(self.stations.dbroot)==0:
            module_logger.info("No genres info., going to download; it may take a few minutes")
            self.update_genres_playlist_url(update_genres=update_genres)
        module_logger.info("StationMan started")

    def close(self):
        self.stations.close()
        self.genres.close()

    # get a list of the saved genres in registered order
    def saved_genres_name(self):
        genres=RadioBaseData.sort_by_regorder(self.genres.dbroot.values())
        return [i.name for i in genres]

    def sorted_genres_favorite(self):
        genres=RadioBaseData.sort_by_regorder(self.genres.dbroot.values())
        genres=RadioBaseData.sort_by_favorite(genres)
        return genres

    # get a description list of the saved stations for the genre
    def saved_stations_description(self, genre):
        return [i.description for i in self.stations.get_one_genre(genre)]

    # get a number of stations in a genre
    def num_of_stations_in_genre(self, genre):
        return len(self.stations.get_one_genre(genre))

    # get a sorted list of the saved stations for the genre
    def sorted_stations_favorite_playtimes(self, genre):
        stds=StationData.sort_by_playtimes(self.stations.get_one_genre(genre))
        stds=RadioBaseData.sort_by_favorite(stds)
        return stds

    def station_update(self, std):
        if self.stations.dbroot.has_key(std.name):
            transaction.commit()
            return
        self.stations.update_item(std)

    def genre_update(self, grd):
        if self.genres.dbroot.has_key(grd.name):
            transaction.commit()
            return
        self.genres.update_item(grd)
        
    # update the genres list
    def list_of_genres_update(self, renew_update=False):
        if renew_update or len(self.genres.dbroot)==0:
            module_logger.info("update genres list by %s" % self.baseurl)
            dbupdate=False
            count=1
            for n,d in self.get_genres():
                module_logger.debug("genre name: %s" % n)
                module_logger.debug("description: %s" % d)
                gd=GenreData(n, d)
                gd.regorder=count
                self.genres.update_item(gd)
                dbupdate=True
                count+=1
            if dbupdate: self.genres.db.pack()
        else:
            module_logger.info("using the saved genres list")
            genres = RadioBaseData.sort_by_regorder(self.genres.dbroot.values())
            genres = [i.name for i in genres]
            module_logger.debug(",".join(genres))
        self.genres_num = len(self.genres.dbroot)

    # update the stations playlist url list for update_genres
    # if update_genres=[], update for all the genres, which takes a long time
    def update_genres_playlist_url(self, update_genres=[], renew_update=False):
        if update_genres==None: return
        if not update_genres: update_genres=self.genres.dbroot.keys()
        for genre in update_genres:
            if renew_update or len(self.stations.get_one_genre(genre))==0:
                self.get_one_genre_playlist_urls(genre)
            module_logger.info("%s has %d stations" % \
                               (genre, len(self.stations.get_one_genre(genre))))

        
    def check_next_mark(self, line):
        next_mark = "<span class=\"sr-only\">Next</span>"
        ucre = re.compile(r"<li class=\"next\"><a href=\"/stations/.*(page[0-9]+).*")
        if line.find(next_mark)==-1: return 0
        red=ucre.search(line)
        if not red:
            self.next_page=None
            return -1
        self.next_page=red.group(1)
        return 1
        
    def get_one_genre_page(self, name, page=""):
        if not page: page=""
        module_logger.info("reading a new page:%s%s/%s" % (self.baseurl, name, page))
        try:
            uc = urllib2.urlopen("%s%s/%s" % (self.baseurl, name, page))
        except:
            module_logger.warn("%s%s/%s is not accessible" % (self.baseurl, name, page))
            return
        ucre1 = re.compile(r"<a title=\"PLS Playlist File\".*'(http[^'?]+).*")
        ucre2 = re.compile(r"<h4 class=\"text-danger[^>]*><[^>]+>([^<]+).*")
        ucre3 = re.compile(r"<h4 class=\"text-danger[^>]*>([^<]+).*")
        state = 0
        while True:
            line=uc.readline()
            if line=="": break
            if state==0:
                red=ucre1.search(line)
                if not red:
                    if not self.check_next_mark(line): continue
                    break
                playlist_url=red.group(1)
                state=1
            else:
                red=ucre2.search(line)
                if not red:
                    red=ucre3.search(line)
                    if not red: continue
                name=hashlib.md5(red.group(1)).hexdigest()
                desc=red.group(1)
                state=0
                yield (name, desc, playlist_url)
        uc.close()

    # update playlist url list for one genre
    # this access multiple web pages and takes a while, especiall for a big genre like 'pop'
    def get_one_genre_playlist_urls(self, name):
        self.next_page=None
        dbupdate=False
        while True:
            lastpage=self.next_page
            for (sname, desc, playlist_url) in self.get_one_genre_page(name, self.next_page):
                sd=StationData(sname, desc, genre=name, urlpls=playlist_url)
                self.stations.update_item(sd)
                dbupdate=True
            if not self.next_page: break
            if lastpage==self.next_page: break
        if dbupdate: self.stations.db.pack()

    def get_genres(self):
        try:    
            uc = urllib2.urlopen(self.baseurl, timeout=10)
        except:
            module_logger.warn("%s is not accessible" % self.baseurl)
            return
        ucre = re.compile(r"<a href=\"/stations/([^/]+)/\">.*")
        udre = re.compile(r"<dd>(.*)</dd>.*")
        udre2 = re.compile(r"<dd>(.*)$")
        state = 0
        while True:
            line=uc.readline()
            if line=="": break
            if state==0:
                red=ucre.search(line)
                if not red: continue
                name=red.group(1)
                state=1
            else:
                red=udre.search(line)
                if not red:
                    red=udre2.search(line)
                    if not red:
                        continue
                desc=red.group(1)
                state=0
                yield (name, desc)
        uc.close()

    # update stations play url for 'update_genres', this may take a long time
    def update_genres_station_urls(self, update_genres=None, renew_update=False):
        stcount=0
        if update_genres==None: return 0
        if not update_genres: update_genres=self.genres.dbroot.keys()
        for genre in update_genres:
            stcount+=self.update_station_urls(genre, renew_update)
        return stcount

    # update stations play url for a genre
    def update_station_urls(self, genre, renew_update=False):
        stcount=0
        ucre = re.compile(r".*(http://[^ \t\n\r;]*).*")
        dbupdate=False
        for sd in self.stations.get_one_genre(genre):
            if sd.noaccess >= NOT_ACCESSIBLE_THRESH: continue
            if sd.urlst:
                module_logger.debug("%s --- %s, %s" % (sd.description, sd.urlpls, sd.urlst))
                stcount+=1
                if not renew_update: continue
            else:
                module_logger.info("%s --- %s" % (sd.description, sd.urlpls))

            if (sd.urlpls.rfind(".pls")!=len(sd.urlpls)-4) and \
               (sd.urlpls.rfind(".m3u")!=len(sd.urlpls)-4):
                module_logger.info("looks not a playlist:%s" % sd.urlpls)
                sd.noaccess+=1
                transaction.commit()
                dbupdate=True
                continue
            
            try:    
                uc = urllib2.urlopen(sd.urlpls, timeout=5)
            except:
                module_logger.info("this stantion is not accessible")
                sd.noaccess+=1
                transaction.commit()
                dbupdate=True
                continue
                
            while True:
                line=uc.readline()
                if line=="": break
                red=ucre.search(line)
                if not red: continue
                sd.urlst=red.group(1)
                module_logger.info("station url = %s" % sd.urlst)
                transaction.commit()
                dbupdate=True
                stcount+=1
                break
            uc.close()
        if dbupdate: self.stations.db.pack()
        return stcount

    # when a new attribute is added on StationData, apply this for all existing genres
    def add_new_attribute(self, genre, attr, value):
        for sd in self.stations.get_one_genre(genre):
            if hasattr(sd, attr): continue
            setattr(sd, attr, value)
            transaction.commit()

    def get_station_by_desc(self, desc):
        name=hashlib.md5(desc).hexdigest()
        try:
            return self.stations.dbroot[name]
        except:
            module_logger.warn("no such a station:%s" % desc)
            return None
        
    def get_station_url_by_desc(self, desc):
        std=self.get_station_by_desc(desc)
        if not std: return None
        return std.urlst
            
def main():
    # at the first call, this obtains genres list from the 'baseurl'
    stm=StationMan()

    # if any genre doesn't exist, can't do anything
    if stm.genres_num==0: return

    if len(sys.argv)<2:
        print "set 'genre' in parameters"
        return
        
    genre=sys.argv[1]
    if not genre in stm.saved_genres_name():
        print "%s is not in the genres list" % genre
        return
    renew=False
    if len(sys.argv)>2 and sys.argv[2]=='renew':
        renew=True
        
    # this updates playlist urls for 'genre'
    # if the list is already there, it doesn't update unless setting 'renew_update'
    stm.update_genres_playlist_url(update_genres=[genre], renew_update=renew)

    # this update station urls for 'genre'
    # if the staion url is already there, it doesn't update unless setting 'renew_update'
    stm.update_genres_station_urls([genre], renew_update=renew)

    stations=stm.saved_stations_description(genre)
    print ",".join(stations)
    print
    print "pick one station to play"
    print "at this time, pick the first station=%s" % stations[0]
    print

    station_url=stm.get_station_url_by_desc(stations[0])
    if station_url:
        print "play this url:%s" % station_url
    else:
        print "station_url doesn't exist"

    stm.close()

