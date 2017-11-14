#!/usr/bin/env python3
#-*-coding:utf-8-*-
import sys

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
# ==================================================================================

__enimerothike__ = '30-03-2015'


class NumbersToGreek:
    """
    Converts Numbers to Greek Words.
    """
    def __init__(self, number=0, nomisma=False, onomanomismatos= 'Ευρώ', onomaekatoston='λεπτά', case='lower'):
        self.number = number
        self.nomisma = nomisma
        self.onomanomismatos = onomanomismatos
        self.onomaekatoston = onomaekatoston
        self.case = case

    def convertnumber(self):
        """Converts numbers to greek words
        """

        if self.case not in ('lower', 'upper', 'title'):
            return

        place = {0: " ",
                1: " Χιλιάδες ",
                2: " Εκατομμύρια ",
                3: " Δισεκατομμύρια ",
                4: " Τρισεκατομμύρια ",
                5: " Τετράκις Εκατομμύρια ",
                6: " Πεντάκις Εκατομμύρια ",
                7: " ",
                8: " "}

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

        self.number = str(self.number).strip()
        dekadika = ''
        dol = ''
        decplace = self.number.find(".")
        count = 0

        if decplace >= 0:
            temp = self.number[decplace + 1:]
            if len(temp) > 2:
                temp = temp[:2]
            if len(temp) == 1: # If the number is .6 make it .60
                temp = temp + '0'

            if int(temp[:2]) == 0:
                dekadika = ''
            else:
                dekadika = self.metatropi_dekadon(temp[:2])
            self.number = self.number[:decplace]

        while self.number != "":
            temp = self.metatropi_ekatontadon(self.number[-3:])
            if temp != "":
                if count == 1:
                    for k, v in replacements.items():
                        if k in temp:
                            temp = temp.replace(k, replacements[k])

                dol = temp + place[count] + dol

            if len(self.number) > 3:
                self.number = self.number[:-3]
            else:
                self.number = ""
            count += 1

        if dol == "":
            dol = "Μηδέν"
        elif dol == "Ένα Χιλιάδες ":
            dol = "Χίλια"

        else:
            if dol.startswith("Ένα Χιλιάδες "):
                dol = dol.replace("Ένα Χιλιάδες ", "Χίλια ")
            if dol.find("Ένα Εκατομμύρια") != -1:
                dol = dol.replace( "Ένα Εκατομμύρια", "Ένα εκατομμύριο")
            if dol.find("Ένα Δισεκατομμύρια") != -1:
                dol = dol.replace("Ένα Δισεκατομμύρια", "Ένα Δισεκατομμύριο")
            if dol.find("Ένα Τρισεκατομμύρια") != -1:
                dol = dol.replace("Ένα Τρισεκατομμύρια", "Ένα Τρισεκατομμύριo")
    #         if dol.find("Τρείς Εκατομμύρια") != -1:
    #             dol = dol.raplace("Τρείς Εκατομμύρια", "Τρία εκατομμύρια")
    #         if dol.find("Τέσσερις Εκατομμύρια") != -1:
    #             dol = dol.replace("Τέσσερις Εκατομμύρια", "Τέσσερα Εκατομμύρια")
            if dol.find("Ένα Τετράκις Εκατομμύρια") != -1:
                dol = dol.replace("Ένα Τετράκις Εκατομμύρια", "Ένα Τετράκις Εκατομμύριο")
            if dol.find("Ένα Πεντάκις Εκατομμύρια") != -1:
                dol = dol.replace("Ένα Πεντάκις Εκατομμύρια", "Ένα Πεντάκις Εκατομμύριο")

        if self.nomisma:
            if dekadika == '':
                return dol.strip() + ' ' + self.onomanomismatos
            else:
                return dol.strip() + ' ' + self.onomanomismatos + ' ' + dekadika + ' λεπτά'
        else:
            return dol.strip() + ' ' + dekadika


    def metatropi_ekatontadon(self, arithmos):
        """Converts hundrets to greek words
        """
        apotelesma = ''

        ekatontades = {1: "Έκατό ",
                  2: "Διακόσια ",
                  3: "Τριακόσια ",
                  4: "Τετρακόσια ",
                  5: "Πεντακόσια ",
                  6: "Έξακόσια ",
                  7: "Επτακόσια ",
                  8: "Οκτακόσια ",
                  9: "Εννιακόσια "}

        try:
            if int(arithmos) == 0:
                exit
        except ValueError as err:
            print('\n\nΟ αριθμός που δώσατε είναι πολύ μεγάλος για χειρισμό, ή δεν είνσι αριθμός: {0}\n\n'.format(err))
            sys.exit(128)

        arithmos = "000"+ str(arithmos)
        arithmos = arithmos[-3:]

        if arithmos[0] != "0":
            try:
                if int(arithmos[0]) in ekatontades.keys():
                    apotelesma = ekatontades[int(arithmos[0])]
            except ValueError as err:
                print('\n\nΟ αριθμός που δώσατε είναι πολύ μεγάλος για χειρισμό, ή δεν είνσι αριθμός: {0}\n\n'.format(err))
                sys.exit(128)

        if arithmos[1] != "0":
            apotelesma = apotelesma + self.metatropi_dekadon(arithmos[1:])

        else:
            apotelesma = apotelesma + self.metatropi_psifion(arithmos[2])

        return apotelesma


    def metatropi_dekadon(self, dekad):
        """Converts tens to greek words
        """

        apotelesma =''

        dekades = {10: "Δέκα",
                  11: "Έντεκα",
                  12: "Δώδεκα",
                  13: "Δεκατρία",
                  14: "Δεκατέσσερα",
                  15: "Δεκαπέντε",
                  16: "Δεκαέξι",
                  17: "Δεκαεπτά",
                  18: "Δεκαοκτώ",
                  19: "Δεκαεννέα"}

        eikosieneninta ={2: "Είκοσι ",
                         3: "Τριάντα ",
                         4: "Σαράντα ",
                         5: "Πενήντα ",
                         6: "Εξήντα ",
                         7: "Εβδομήντα ",
                         8: "Ογδόντα ",
                         9: "Ενενήντα "}

        try:
            if int(dekad) in dekades.keys():
                apotelesma = dekades[int(dekad)]
                return apotelesma
            elif int(str(dekad)[0]) in eikosieneninta.keys():
                apotelesma = eikosieneninta[int(str(dekad)[0])]
            else:
                apotelesma = ''
        except ValueError as err:
            print('\n\nΟ αριθμός που δώσατε είναι πολύ μεγάλος για χειρισμό, ή δεν είνσι αριθμός: {0}\n\n'.format(err))
            sys.exit(128)

        return apotelesma + self.metatropi_psifion(int(str(dekad)[1]))

    def metatropi_psifion(self, psifio):
        """
         Converts digits to greek words
        """
        psifia = {1: "Ένα",
                  2: "Δύο",
                  3: "Τρία",
                  4: "Τέσσερα",
                  5: "Πέντε",
                  6: "Έξι",
                  7: "Επτά",
                  8: "Οκτώ",
                  9: "Εννέα"
                  }

        try:
            psifio = int(psifio)
            if psifio in psifia.keys():
                return psifia[psifio]
            else:
                return ""
        except ValueError as err:
            print("Πρέπει να δώσετε ψηφίο 0-9. Δώσατε: {1}\nΣφάλμα: {0}".format(err, psifio))

if __name__ == '__main__':
    n = NumbersToGreek(1963.03, True)
    print(n.convertnumber())
    for i in range(7900, 8002):
        print(i, NumbersToGreek(i, True).convertnumber())

    for i in range(7900, 8002):
        print(i, NumbersToGreek(i, False, case='upper').convertnumber())

    print(NumbersToGreek(21000.01).convertnumber())
    print(NumbersToGreek(21000.01, True).convertnumber())
    print(NumbersToGreek(999999999999999999999.09).convertnumber())
