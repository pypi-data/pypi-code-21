#!/usr/bin/env python3

#==================================================================================
#  Copyright:
#            
#      Copyright (C) 2012 - 2017 Konstas Marmatakis <marmako@gmail.com>
#
#   License:
#  
#      This program is free software; you can redistribute it and/or modify
#      it under the terms of the GNU General Public License version 2 as
#      published by the Free Software Foundation.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this package; if not, write to the Free Software
#      Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#================================================================================== 

__all__ = ["numtogreek"]

__version__ = "1.0.1"

__doc__ =   """Converts numbers to greek words.
    
    USAGE: n2g(thenumber) or
           n2g(thenumber, currency) or
           n2g(thenumber, currency, case) or
           n2g(thenumber, currency=True, case='lower').
    
    PARAMETERS:
           thenumber: Integer or Float.
           currency:   True or False. Displays Ευρώ. Default: False.
           case:      String 'title', 'lower', 'capfirst' or 'upper'. Displays the string as Title Case, lower case, Upper the first letter or UPPER CASE.
                      Default 'title'.
onverts numbers to greek words.
    
    USAGE: n2g(thenumber) or
           n2g(thenumber, currency) or
           n2g(thenumber, currency, case) or
           n2g(thenumber, currency=True, case='lower').
    
    PARAMETERS:
           thenumber: Integer or Float.
           currency:   True or False. Displays Ευρώ. Default: False.
           case:      String 'title', 'lower', 'capfirst' or 'upper'. Displays the string as Title Case, lower case, Capitalized first letter or UPPER CASE.
                      Default 'title'.
"""

from . import numtogreek

def n2g(thenumber, currency=False, case='title'):
    """Converts numbers to greek words.
    
    USAGE: n2g(thenumber) or
           n2g(thenumber, currency) or
           n2g(thenumber, currency, case) or
           n2g(thenumber, currency=True, case='lower').
    
    PARAMETERS:
           thenumber: Integer or Float.
           currency:   True or False. Displays Ευρώ. Default: False.
           case:      String 'title', 'lower', 'capfirst' or 'upper'. Displays the string as Title Case, lower case, Upper the first letter or UPPER CASE.
                      Default 'title'.

    >>> n2g(129.929)
    'Εκατό Είκοσι Εννέα και Ενενήντα Δύο'
    >>> n2g(999999999999999.99)
    'Ένα Τετράκις Εκατομμύριο'
    >>> n2g(999999999999999)
    'Εννιακόσια Ενενήντα Εννέα Τρισεκατομμύρια Εννιακόσια Ενενήντα Εννέα Δισεκατομμύρια Εννιακόσια Ενενήντα Εννέα Εκατομμύρια Εννιακόσιες Ενενήντα Εννέα Χιλιάδες Εννιακόσια Ενενήντα Εννέα'
    >>> n2g(333333.33)
    'Τριακόσιες Τριάντα Τρείς Χιλιάδες Τριακόσια Τριάντα Τρία και Τριάντα Τρία'
    >>> n2g(333333.33, True, 'lower')
    'τριακόσιες τριάντα τρείς χιλιάδες τριακόσια τριάντα τρία ευρώ  και τριάντα τρία λεπτά'
    >>> n2g(333333.00, True, 'upper')
    'ΤΡΙΑΚΌΣΙΕΣ ΤΡΙΆΝΤΑ ΤΡΕΊΣ ΧΙΛΙΆΔΕΣ ΤΡΙΑΚΌΣΙΑ ΤΡΙΆΝΤΑ ΤΡΊΑ ΕΥΡΏ'
    >>> 
    """
    
    if case not in ('lower', 'upper', 'title', 'capfirst'):
        print("Το όρισμα «{0}», που δώσατε, δεν είναι έγκυρο.".format(case))
        return
        
    place = {0: " ",
            1: " Χιλιάδες ",
            2: " Εκατομμύρια ",
            3: " Δισεκατομμύρια ",
            4: " Τρισεκατομμύρια ",
            5: " Τετράκις Εκατομμύρια ",
            6: " Πεντάκις Εκατομμύρια ",
            7: " Εξάκις Εκατομμυρια ",
            8: " Έπτάκις Εκατομμύρια ",
            9: " Οκτάκις Εκατομμύρια "}
    
    replacements = {"Ένα": "Μία",
                  "Τρία": "Τρείς",
                  "Τέσσερα": "Τέσσερις",
                  "Δεκατρία": "Δεκατρείς",
                  "Δεκατέσσερα": "Δεκατέσσερις",
                   "Διακόσια": "Διακόσιες",
                  "Τριακόσια": "Τριακόσιες",
                  "Τετρακόσια": "Τετρακόσιες",
                  "Πεντακόσια": "Πεντακόσιες",
                  "Έξακόσια": "Έξακόσιες",
                  "Επτακόσια": "Επτακόσιες",
                  "Οκτακόσια": "Οκτακόσιες",
                  "Εννιακόσια": "Εννιακόσιες"
                    }
    
    thenumber = str(thenumber).strip()
    dekadika = ''
    dol = ''
    decplace = thenumber.find(".")
    count = 0
    
    if decplace >= 0:
        temp = thenumber[decplace + 1:]
        if len(temp) > 2:
            temp = temp[:2]
        if len(temp) == 1: # If the number is .6 make it .60
            temp = temp + '0'
        
        if int(temp[:2]) == 0:
            dekadika = ''
        else:
            dekadika = numtogreek._metatropi_dekadon(temp[:2])
        thenumber = thenumber[:decplace]

    while thenumber != "":
        temp = numtogreek._metatropi_ekatontadon(thenumber[-3:])
        if temp != "":
            if count == 1:
                for k, v in replacements.items():
                    if k in temp:
                        temp = temp.replace(k, v)
            try:
                dol = temp + place[count] + dol
            except KeyError as err:
                print('\nΟ αριθμός που δώσατε είναι πολύ μεγάλος για χειρισμό: {0}\n\n'.format(err))
                return
                #exit #raise
            
        if len(thenumber) > 3:
            thenumber = thenumber[:-3]
        else:
            thenumber = ""
        count += 1
    
    if dol == "":
        dol = "Μηδέν"
    elif dol == "Ένα Χιλιάδες ":
        dol = "Χίλια"

    else:
        if dol.startswith("Ένα Χιλιάδες "):
            dol = dol.replace("Ένα Χιλιάδες ", "Χίλια ")
        if dol.startswith("Μία Χιλιάδες "):
            dol = dol.replace("Μία Χιλιάδες ", "Χίλια ")
        if dol.find("Ένα Εκατομμύρια") != -1:
            dol = dol.replace( "Ένα Εκατομμύρια", "Ένα εκατομμύριο")
        if dol.find("Ένα Δισεκατομμύρια") != -1:
            dol = dol.replace("Ένα Δισεκατομμύρια", "Ένα Δισεκατομμύριο")
        if dol.find("Ένα Τρισεκατομμύρια") != -1:
            dol = dol.replace("Ένα Τρισεκατομμύρια", "Ένα Τρισεκατομμύριo")
        if dol.find("Ένα Τετράκις Εκατομμύρια") != -1:
            dol = dol.replace("Ένα Τετράκις Εκατομμύρια", "Ένα Τετράκις Εκατομμύριο")
        if dol.find("Ένα Πεντάκις Εκατομμύρια") != -1:
            dol = dol.replace("Ένα Πεντάκις Εκατομμύρια", "Ένα Πεντάκις Εκατομμύριο")
                
    if dekadika == '':
        dekadika = ' '
    else:
        if dekadika == "Ένα":
            dekadika = " και Ένα"
        else:
            dekadika = " και {0}".format(dekadika)  
    if currency:
        if dekadika == '' or dekadika == ' ' or dekadika == None:
            greekword = "{0} Ευρώ".format(dol.strip())
        else:
            if dekadika == " και Ένα":
                greekword = "{0} Ευρώ {1} Λεπτό".format(dol.strip(), dekadika)
            else:
                greekword = "{0} Ευρώ {1} Λεπτά".format(dol.strip(), dekadika)
    else:
        greekword = dol.strip() + dekadika
        
    if case == 'lower':
        return greekword.lower().strip()
    elif case == 'upper':
        return greekword.upper().strip()
    elif case == 'capfirst':
        return greekword.capitalize().strip()
    else:
        return greekword.strip()
