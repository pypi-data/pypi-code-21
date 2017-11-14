#!/usr/bin/env python3
#-*-coding:utf-8-*-

#==================================================================================
#  Copyright:
#            
#      Copyright (C) 2012 - 2015 Konstas Marmatakis <marmako@gmail.com>
#
#   License:
#  
#      This program is free software; you can redistribute it and/or modify
#      it under the terms of the GNU General Public License version 3 as
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

__enimerothike__ = '13-04-2015'

PSIFIA = {1: "Ένα",
          2: "Δύο",
          3: "Τρία",
          4: "Τέσσερα",
          5: "Πέντε",
          6: "Έξι",
          7: "Επτά",
          8: "Οκτώ",
          9: "Εννέα"}

DEKADES = {10: "Δέκα",
          11: "Έντεκα",
          12: "Δώδεκα",
          13: "Δεκατρία",
          14: "Δεκατέσσερα",
          15: "Δεκαπέντε",
          16: "Δεκαέξι",
          17: "Δεκαεπτά",
          18: "Δεκαοκτώ",
          19: "Δεκαεννέα"}

EIKOSIENENINTA = {2: "Είκοσι ",
                 3: "Τριάντα ",
                 4: "Σαράντα ",
                 5: "Πενήντα ",
                 6: "Εξήντα ",
                 7: "Εβδομήντα ",
                 8: "Ογδόντα ",
                 9: "Ενενήντα "}

EKATONTADES = {1: "Εκατό ",
              2: "Διακόσια ",
              3: "Τριακόσια ",
              4: "Τετρακόσια ",
              5: "Πεντακόσια ",
              6: "Έξακόσια ",
              7: "Επτακόσια ",
              8: "Οκτακόσια ",
              9: "Εννιακόσια "}


def _metatropi_psifion(psifio, psifia=PSIFIA):
    """
     Converts digits to greek words
    """
   
    try:
        psifio = int(psifio)
        if psifio in psifia.keys():
            return psifia[psifio]
        else:
            return ""
    except ValueError as err:
        print("Πρέπει να δώσετε ψηφίο 0-9.\nΣφάλμα: {0}".format(err))


def _metatropi_dekadon(dekad, dekades=DEKADES, eikosieneninta=EIKOSIENENINTA):
    """Converts tens to greek words
    """
    
    apotelesma =''
    
    if int(dekad) in dekades.keys():
        apotelesma = dekades[int(dekad)]
        return apotelesma
    elif int(str(dekad)[0]) in eikosieneninta.keys():
        apotelesma = eikosieneninta[int(str(dekad)[0])]

    return apotelesma + _metatropi_psifion(int(str(dekad)[1]))


def _metatropi_ekatontadon(arithmos, ekatontades=EKATONTADES):
    """Converts hundrets to greek words
    """
    apotelesma = ''
    
    try:
        if int(arithmos) == 0:
            exit
    except ValueError as err:
            print('\nΟ αριθμός που δώσατε είναι πολύ μεγάλος για χειρισμό, ή δεν είνσι αριθμός: {0}\n\n'.format(err))
            exit
        
    arithmos = "000"+ str(arithmos)
    arithmos = arithmos[-3:]

    if arithmos[0] != "0":
        try:
            if int(arithmos[0]) in ekatontades.keys():
                apotelesma = ekatontades[int(arithmos[0])]
        except ValueError as err:
            print('\nΟ αριθμός που δώσατε είναι πολύ μεγάλος για χειρισμό, ή δεν είνσι αριθμός: {0}\n\n'.format(err))
            exit
##            raise ValueError('Ο αριθμός που δώσατε είναι πολύ μεγάλος ή δεν είναι αριθμός.')
        
    if arithmos[1] != "0":
        apotelesma = apotelesma + _metatropi_dekadon(arithmos[1:])
    
    else:
        apotelesma = apotelesma + _metatropi_psifion(arithmos[2])

    return apotelesma
