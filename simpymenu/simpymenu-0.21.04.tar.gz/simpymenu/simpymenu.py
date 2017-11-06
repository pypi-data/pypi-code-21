#!/usr/bin/env python3
'''
Project:      Python Simple Text Menu
Version:      0.21.03
Version Date: 5 November 2017
Versin Note:  Added subprocess call to allow ANSI escape keys to work
              in Windows 10 environment

Copyright 2017 by Tai-Fong Foong

License: GPL. This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or any later
version.

Description: Display a simple menu system for terminal based applications.
'''
import time
import subprocess


CURSOR_UP = '\033[F'
ERASE_LINE = '\033[K'

class SimpleTextMenu:

    def __init__(self,menu_items,header='',sub_header='',align='CENTER',box_style="DOUBLE", delay=1.5):
        if not menu_items:
            raise ValueError("[!]Empty menu")
        elif type(menu_items) != list:
            raise TypeError("[!]Menu must be list type")
        elif len(menu_items) > 20:
            raise ValueError("[!]Too many items in menu!")
        else:
            for i in menu_items:
                if type(i) != list:
                    raise TypeError("[!]Individual menu items must be list type")
            self.menu_items = menu_items

        self.header = header
        self.sub_header = sub_header
        self.valid_choice = [str(i+1) for i in range(len(menu_items))]
        self.__selector = self.get_selector()
        self.box_width = self.get_box_width()
        self.box_style = self.get_char_set(box_style)
        self.align = align if align in ['LEFT', 'CENTER'] else 'CENTER'
        self.delay = 1.5 if delay < 0 else delay
        subprocess.call('', shell=True)


    def get_char_set(self, box_style):
        '''
        return the unicode style for boxes, the unicode can be obtained
        from using ord() function, example, ord(u'\u2501')
        '''
        if box_style not in ['DOUBLE', 'SINGLE', 'SOLID', 'THICK', 'SOLIDMIX','NOBOX']:
            box_style = 'NOBOX'

        char_set = {
                    "DOUBLE": { 'TOP_LEFT' : chr(9556),
                                'TOP_RIGHT': chr(9559),
                                'H_LINE'   : chr(9552),
                                'DIV_LEFT' : chr(9567),
                                'DIV_RIGHT': chr(9570),
                                'DIV_LINE' : chr(9472),
                                'BOT_LEFT' : chr(9562),
                                'BOT_RIGHT': chr(9565),
                                'V_LINE'   : chr(9553)
                              },
                    "NOBOX":  { 'TOP_LEFT' : ' ',
                                'TOP_RIGHT': ' ',
                                'H_LINE'   : ' ',
                                'DIV_LEFT' : ' ',
                                'DIV_RIGHT': ' ',
                                'DIV_LINE' : '-',
                                'BOT_LEFT' : ' ',
                                'BOT_RIGHT': ' ',
                                'V_LINE'   : ' '
                               },
                    "SINGLE":  { 'TOP_LEFT': chr(9484),
                                'TOP_RIGHT': chr(9488),
                                'H_LINE'   : chr(9472),
                                'DIV_LEFT' : chr(9500),
                                'DIV_RIGHT': chr(9508),
                                'DIV_LINE' : chr(9472),
                                'BOT_LEFT' : chr(9492),
                                'BOT_RIGHT': chr(9496),
                                'V_LINE'   : chr(9474)
                               },
                    "SOLID":  { 'TOP_LEFT' : chr(9618),
                                'TOP_RIGHT': chr(9618),
                                'H_LINE'   : chr(9618),
                                'DIV_LEFT' : chr(9618),
                                'DIV_RIGHT': chr(9618),
                                'DIV_LINE' : chr(9618),
                                'BOT_LEFT' : chr(9618),
                                'BOT_RIGHT': chr(9618),
                                'V_LINE'   : chr(9618)
                               },
                    "THICK":  { 'TOP_LEFT' : chr(9487),
                                'TOP_RIGHT': chr(9491),
                                'H_LINE'   : chr(9473),
                                'DIV_LEFT' : chr(9504),
                                'DIV_RIGHT': chr(9512),
                                'DIV_LINE' : chr(9472),
                                'BOT_LEFT' : chr(9495),
                                'BOT_RIGHT': chr(9499),
                                'V_LINE'   : chr(9475)
                               },
                    "SOLIDMIX":{ 'TOP_LEFT' : chr(9618),
                                 'TOP_RIGHT': chr(9618),
                                 'H_LINE'   : chr(9618),
                                 'DIV_LEFT' : chr(9618),
                                 'DIV_RIGHT': chr(9618),
                                 'DIV_LINE' : chr(9472),
                                 'BOT_LEFT' : chr(9618),
                                 'BOT_RIGHT': chr(9618),
                                 'V_LINE'   : chr(9618)
                               }
                }
        return char_set[box_style]

    def get_selector(self):
        s = "Enter your selection [1"
        if len(self.menu_items) == 1:
            return s + "] > "
        else:
            return s + "-" + str(len(self.menu_items)) + "] > "

    def change_selector(self, new_selector):
        '''
        The class does not allow direct acess to the selection text due to len
        calculation, changes have to be made through this method.
        '''
        self.__selector = new_selector
        self.box_width = self.get_box_width()
        return self.__selector

    def get_box_width(self):
        '''
        Determine the width of the box to be drawn.
        '''
        header_len = len(self.header) if self.header else 0
        sub_header_len = len(self.sub_header) if self.sub_header else 0
        selector_len = len(self.__selector)

        # get the maximum length of menu items
        menu_items_len = [len(i[0]) for i in self.menu_items]
        max_menu_item_len = self.get_max_len(menu_items_len)
        # add the prefix length, eg., 1., 2., ...10.,11., ...
        # Eg, 1. Enter Selection
        if len(self.menu_items) < 10:
            max_menu_item_len += 3
        elif len(self.menu_items) >= 10:
            max_menu_item_len += 4

        len_array = [header_len, sub_header_len, selector_len, max_menu_item_len]
        # +2 for the left & right padding
        return self.get_max_len(len_array) + 2

    def get_max_len(self, items_array):
        '''
        return the length of the longest item in the array
        '''
        max_len = items_array[0]
        for i in items_array:
            max_len = i if i > max_len else max_len
        return max_len

    def draw_line(self, begin_char, line_char, last_char):
        line = line_char * self.box_width
        print(begin_char + line + last_char)
        return

    def lead_space(self, line):
        return (self.box_width - len(line))//2

    def print_content(self, box_char, content, align):
        if align == 'LEFT':
            line = box_char + ' ' + content
        elif align == 'CENTER':
            line = box_char + ' ' * self.lead_space(content) + content
        # add 1 because box_width calculation excluded the box_char width,
        # while len(line) is including the box_char width, if does not
        # add 1, there will be one space short
        line = line + ' '*(self.box_width-len(line) + 1) + box_char
        print(line)
        return

    def draw_box(self):
        print('')
        # Box top line
        self.draw_line(self.box_style['TOP_LEFT'], self.box_style['H_LINE'], self.box_style['TOP_RIGHT'])
        # print empty line
        self.draw_line(self.box_style['V_LINE'], ' ', self.box_style['V_LINE'])

        if self.header or self.sub_header:
            # print headers
            self.print_content(self.box_style['V_LINE'], self.header, self.align)
            self.print_content(self.box_style['V_LINE'], self.sub_header, self.align)
            # print empty line
            self.draw_line(self.box_style['V_LINE'], ' ', self.box_style['V_LINE'])
            # print divider
            self.draw_line(self.box_style['DIV_LEFT'], self.box_style['DIV_LINE'], self.box_style['DIV_RIGHT'])
            self.draw_line(self.box_style['V_LINE'], ' ', self.box_style['V_LINE'])

        # print menu_items
        for j,k in enumerate(self.menu_items):
            s = '{num}. {description}'.format(num=str(j+1), description=k[0])
            self.print_content(self.box_style['V_LINE'], s, 'LEFT')

        self.draw_line(self.box_style['V_LINE'], ' ', self.box_style['V_LINE'])
        # print bottom line
        self.draw_line(self.box_style['BOT_LEFT'], self.box_style['H_LINE'], self.box_style['BOT_RIGHT'])
        return

    def run_menu(self):
        self.draw_box()
        while True:
            selection = input('  ' + self.__selector)
            if selection in self.valid_choice:
                break
            else:
                print("  [!]Please enter a valid selection.")
                time.sleep(self.delay)
                print(CURSOR_UP + ERASE_LINE + CURSOR_UP + ERASE_LINE + CURSOR_UP)

        try:
            if len(self.menu_items[int(selection)-1]) >= 2:
                if callable(self.menu_items[int(selection)-1][1]):
                    return self.menu_items[int(selection)-1][1]
            return selection
        except:
            return selection


###############
if __name__ == '__main__':
    header = 'ABC CORPORATION'
    sub_header = 'Employee Records Management System'
    menu_items = [
                  ["Enter Employee Record"],
                  ["Update Employee Record"],
                  ["Search Employee Record"],
                  ["Quit"]
                 ]
    stm = SimpleTextMenu(menu_items,header=header,sub_header=sub_header)
    #stm.change_selector('Hello > ')
    choice = stm.run_menu()
    print(choice)
