#!/usr/bin/env python
# -*- coding: utf-8 -*-
# title           :menu_datasource.py
# description     :This program displays an interactive menu on CLI for user to select data source
# author          :Rubing Duan
# date            :
# version         :0.1
# notes           :
# python_version  :2.7.6
# =======================================================================

# Import the modules needed to run the script.
import sys
import os
import flyshare.ApiConfig as ac
import flyshare.util.conn as conn

# =======================
#     MENUS FUNCTIONS
# =======================

# Main menu
def main_menu():
    # os.system('clear')

    print "Welcome,\n"
    print "Please choose data source you want to use:"
    print "1. Flyshare"
    print "2. Tushare"
    print "3. Datareader"
    print "4. TDX"
    print "\n0. Quit"
    choice = raw_input(" >>  ")
    exec_menu(choice)

    return


# Execute menu
def exec_menu(choice):
    # os.system('clear')
    ch = choice.lower()
    if ch == '':
        menu_actions['main_menu']()
    else:
        try:
            menu_actions[ch]()
        except KeyError:
            print "Invalid selection, please try again.\n"
            menu_actions['main_menu']()
    return


# Menu 1
def menu1():
    ac.DATA_SOURCE = 'flyshare'
    print "Flyshare !\n"
    print "9. Back"
    print "0. Quit"
    choice = raw_input(" >>  ")
    exec_menu(choice)
    return


# Menu 2
def menu2():
    ac.DATA_SOURCE = 'tushare'
    print "Tushare !\n"
    print "9. Back"
    print "0. Quit"
    choice = raw_input(" >>  ")
    exec_menu(choice)
    return

def menu3():
    ac.DATA_SOURCE = 'datareader'
    print "Datareader !\n"
    print "9. Back"
    print "0. Quit"
    choice = raw_input(" >>  ")
    exec_menu(choice)
    return

def menu4():
    ac.DATA_SOURCE = 'tdx'
    print "get apis..."
    ac.TDX_CONN = conn.get_apis()
    return


# Back to main menu
def back():
    menu_actions['main_menu']()


# Exit program
def exit():
    print "You have select the following data source:"
    print ac.DATA_SOURCE
    # sys.exit()

# =======================
#    MENUS DEFINITIONS
# =======================

# Menu definition
menu_actions = {
    'main_menu': main_menu,
    '1': menu1,
    '2': menu2,
    '3': menu3,
    '4': menu4,
    '9': back,
    '0': exit,
}

def set_datasource():
    main_menu()

# =======================
#      MAIN PROGRAM
# =======================

# Main Program
if __name__ == "__main__":
    # Launch main menu
    main_menu()