#!/usr/bin/python3
# Author : GMFTBY
# Time : 2017.10.23

'''This model define the spider for http://bing.ioliu.cn'''

import requests
from bs4 import BeautifulSoup
import time
import pickle
import os
import hashlib
import urllib.request
import glob
import curses
import multiprocessing as mp

# Return the text of the photo 
def load_text(filename):
    with open(filename + '.txt' , 'r') as f:
        text = f.read()
    return text

def get_photo_name(work_path):
    '''
    This function get the photo from the work_path
    '''
    filenames = []    # Collect the photo file name
    photo_list = glob.glob(work_path + '*')    # GET all the file under the work_path
    for i in photo_list:
        filename , postfix = os.path.splitext(i)
        if postfix != '.txt' and postfix != '.pkl' and \
                filename != work_path + 'Wallpapers':
            # the photo
            filenames.append(i)
    return filenames            

def init_time(work_path):
    with open(work_path + 'time.pkl' , 'wb') as f:
        pickle.dump('19970106' , f)

# This function call to change to tight_now photo name
def init_rightnow_wallpaper(work_path , photo_name):
    with open(work_path + 'rightnow.pkl' , 'wb') as f:
        # Write the photo_name into the pickle file
        pickle.dump(photo_name , f)

def linux_change_wallpaper_cmd(work_path , filename):
    # File name is the path to the right now photo
    os.system('gsettings set org.gnome.desktop.background picture-uri "file:%s"' \
            % filename)
    # Change the right_now photo name
    init_rightnow_wallpaper(work_path , filename)

# Save the photo to work_path
# Change the url for getting the highlight photo
def save_photo(work_path , filenames , photo):
    last_href = photo.a['href']
    src = 'https://bing.ioliu.cn' + last_href
    page = requests.get(src , headers = {'User-Agent' : 'Mozilla/5.0 \
            (Windows NT 10.0; Win64; x64)'})    # GET the page
    soup = BeautifulSoup(page.text , 'lxml')
    url = soup.img['src']
    img = requests.get(url)    # GET the photo of highlight
    filename , postfix = os.path.splitext(src)
    md5 = hashlib.md5()
    md5.update(filename.encode('utf8'))
    md5_src = md5.hexdigest()
    if work_path + md5_src + postfix in filenames :
        # Have already download the photo
        return None
    with open(work_path + md5_src + postfix , 'wb') as f:
        f.write(img.content)    # Write the binary data into the file 
    with open(work_path + md5_src + '.txt' , 'w') as f:
        # Write Gthe description of the photo into another file
        desc = soup.find(class_ = 'description')
        text = desc.get_text()
        f.write(text)
    return work_path + md5_src + postfix

def ioliu_today(work_path):
    filename = None    # GET the fallback filename
    filenames = get_photo_name(work_path)
    url = 'https://bing.ioliu.cn'
    today = time.localtime()
    today = str(today[0]) + str(today[1]) + str(today[2])    # GET TIME
    with open(work_path + 'time.pkl' , 'rb') as f:
        lastday = pickle.load(f)
    if today >= lastday : 
        # Have not been renewed the Wallpaper
        # crawl the new picture from the url 
        page = requests.get(url , headers = {'User-Agent' : 'Mozilla/5.0 \
                (Windows NT 10.0; Win64; x64)'})
        page.encoding = 'utf'
        soup = BeautifulSoup(page.text , 'lxml')
        photos = soup.find_all(class_ = 'item')    # Found all the photo
        for photo in photos:
            # Iterate all the photo in this page and found today's Wallpaper
            calendar = photo.find(class_ = 'calendar').get_text()
            photo_date = ''.join(calendar.split('-'))
            if photo_date == today:
                # Found the destination 
                filename = save_photo(work_path , filenames , photo)
                # Renew the time.pkl
                with open(work_path + 'time.pkl' , 'wb') as f:
                    pickle.dump(today , f)
                break
        else:
            # Some error
            raise Exception("Can not found day : %s 's Wallpaper" % today)
        # Renew the Wallpaper of today
    else:
        raise Exception("Have already get the photo of today")
    linux_change_wallpaper_cmd(work_path , filename)

# This module init the Pictures folder and init the necessary things
# This function try to get some photo from the Wensite
# One page has 12 photos
def init_photos(page_number , work_path):
    url = 'http://bing.ioliu.cn'
    filenames = get_photo_name(work_path)    # GET the photo name from the work path
    done_number = 0
    while page_number:
        page_number -= 1
        page = requests.get(url)
        soup = BeautifulSoup(page.text , 'lxml')
        photos = soup.find_all(class_ = 'item')
        # Save this page's photo
        for photo in photos: 
            flag = save_photo(work_path , filenames , photo)
            if flag != None : done_number += 1
        url = urllib.request.urljoin(url , \
                soup.find(class_ = 'page').a.next_sibling.next_sibling['href'])

# Main Loop
def show_photo_desc(myscreen , text):
    myscreen.addstr(14 , 1 , text)
    myscreen.addstr(13 , 1 , 'Please any key to continue ... ')

def show_help():
   myscreen = curses.initscr()
   myscreen.border(0)
   myscreen.refresh()
   myscreen.addstr(1 , 1 , "========================================")
   myscreen.addstr(2 , 1 , '               Help Menu')
   myscreen.addstr(3 , 1 , "========================================")
   myscreen.addstr(4 , 1 , '  exit : exit the process')
   myscreen.addstr(5 , 1 , '  do : change the wallpaper')
   myscreen.addstr(6 , 1 , '  next : change to next photo')
   myscreen.addstr(7 , 1 , '  before : change to last photo')
   myscreen.addstr(8 , 1 , '  loop : loop show the photo under the work path')
   myscreen.addstr(9 , 1 , '  help : show the help menu')
   myscreen.addstr(10 , 1 , '  crawl : crawl more photo from Bing')
   myscreen.addstr(11 , 1 , '  today : crawl today wallpaper')
   myscreen.addstr(13 , 1 , 'Press any key to continue ... ')
   curses.endwin()

def subprocess_loop(work_path , filenames , index , step , period):
    starttime = time.time()
    while time.time() - starttime <= period:
        time.sleep(step - 0.05)
        linux_change_wallpaper_cmd(work_path , filenames[index])
        index += 1
        if index >= len(filenames) : index -= len(filenames)
        elif index < 0 : index = len(filenames) - 1


def key_in(work_path , key):
    filenames = get_photo_name(work_path)
    index = 0
    if len(filenames) == 0 : 
        print('No photo can be used! Check your work path!')
    myscreen = curses.initscr()
    myscreen.border(0)
    while key in ['exit' , 'do' , 'next' , 'before' , 'loop' , 'help' , 'crawl' , 'today']:
        myscreen.refresh()
        key = myscreen.getstr()    # GET the user input
        myscreen.addstr(13 , 1 , ' ' * 80)    # Refresh the line
        myscreen.addstr(13 , 1 , 'Please input the command : ')
        key = key.decode('utf8').strip().lower()
        if key == 'help':
            show_help()
        elif key == 'exit':
            break    # Exit the program
        elif key == 'do':
            linux_change_wallpaper_cmd(work_path , filenames[index])
        elif key == 'next':
            index += 1
            if index >= len(filenames) : 
                index -= len(filenames)
            show_photo_desc(myscreen , load_text(filenames[index]))
        elif key == 'before':
            index -= 1
            if index < 0 :
                index = len(filenames) - 1
            show_photo_desc(myscreen , load_text(filenames[index]))
        elif key == 'loop':
            # TODO : try to add the cmd to stop this command
            # TODO : try to terminate the subprocess by the user
            myscreen.addstr(13 , 1 , ' ' * 80)
            myscreen.addstr(13 , 1 , 'Please input the step(s) : ')
            step = int(myscreen.getstr().decode('utf8'))
            myscreen.addstr(13 , 1 , 'Please input the period(s) : ')
            period = int(myscreen.getstr().decode('utf8'))
            subp = mp.Process(target = subprocess_loop ,\
                    args = (work_path , filenames , index , step , period ,))
            subp.start()    # Begin the subprocess
            myscreen.addstr(13 , 1 , 'Please input the stop-sign (stop) : ')
            stop = myscreen.getstr().decode('utf8')
        elif key == 'crawl':
            myscreen.addstr(13 , 1 , ' ' * 80)
            myscreen.addstr(13 , 1 , 'Please input the page number(s) : ')
            page_number = int(myscreen.getstr().decode('utf8'))
            subp = mp.Process(target = init_photos , \
                    args = (page_number , work_path))
            subp.start()
            myscreen.addstr(13 , 1 , ' ' * 80)
            myscreen.addstr(13 , 1 , 'Please input the command : ')
        elif key == 'today':
            ioliu_today(work_path)
        else :
            key = 'help'
    curses.endwin()

def main_loop(work_path , key):
    filenames = glob.glob(work_path + '*')
    if work_path + 'time.pkl' not in filenames:
        init_time('/home/lantian/Pictures/')
    show_help()    # Show he help menu for the user
    key_in(work_path , key)

# This function change the work_path to the right format
def change_work_path(work_path):
    if work_path[-1] != '/':
        return work_path + '/'
    else:
        return work_path

if __name__ == "__main__":
    # init_time('/home/lantian/Pictures/')
    # ioliu_today('/home/lantian/Pictures/')
    # init_photos(2 , '/home/lantian/Pictures/')
    main_loop('/home/lantian/Pictures/' , 'help')

