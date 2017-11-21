####################################################################################################
#
# SimpleMorphoMath - A simple mathematical morphology library.
# Copyright (C) 2012 Salvaire Fabrice
#
####################################################################################################

""" This module provide pretty printing tools.
"""

####################################################################################################

class Filet(object):

    """ This class defines a type of Unicode filet. """

    ##############################################

    def __init__(self,
                 horizontal, vertical,
                 top_left, top_right, bottom_left, bottom_right,
                 cross, up_t, down_t):

        self.horizontal, self.vertical = horizontal, vertical
        self.top_left, self.top_right = top_left, top_right
        self.bottom_left, self.bottom_right = bottom_left, bottom_right
        self.cross = cross
        self.up_t, self.down_t = up_t, down_t

####################################################################################################

empty_filet = Filet('', '', '', '', '', '', '', '', '')

ascii_filet = Filet('-', '|',
                    '+', '+', '+', '+',
                    '+', '+', '+')

solid_thin_filet = Filet(chr(9472), chr(9474),
                         chr(9484), chr(9488),
                         chr(9492), chr(9496),
                         chr(9532), chr(9516), chr(9524))

solid_wide_filet = Filet(chr(9473), chr(9475),
                         chr(9487), chr(9491),
                         chr(9495), chr(9499),
                         chr(9535), chr(9523), chr(9531))

solid_thin_double_filet = Filet(chr(9552), chr(9553),
                                chr(9556), chr(9559),
                                chr(9562), chr(9565),
                                chr(9580), chr(9574), chr(9577))

####################################################################################################

class UmbraCharacter(object):

    """ This class defines a type of umbra characters. """

    ##############################################

    def __init__(self, black_pattern, minus_pattern, plus_pattern):

        self.black_pattern = black_pattern
        self.minus_pattern = minus_pattern
        self.plus_pattern = plus_pattern

standard_filet = solid_thin_filet

####################################################################################################

ascii_umbra = UmbraCharacter(black_pattern='#',
                             minus_pattern='-',
                             plus_pattern='+')

rectangle_umbra = UmbraCharacter(black_pattern=chr(9609),
                                 minus_pattern=chr(9015), # chr(9984)
                                 plus_pattern=chr(9617))

small_square_umbra = UmbraCharacter(black_pattern=chr(9642),
                                    minus_pattern=chr(9643),
                                    plus_pattern=chr(9670))

small_square2_umbra = UmbraCharacter(black_pattern=chr(9726),
                                     minus_pattern=chr(9725),
                                     plus_pattern=chr(9679))

large_square_umbra = UmbraCharacter(black_pattern=chr(9724),
                                    minus_pattern=chr(9723),
                                    plus_pattern=chr(9679))

large_square2_umbra = UmbraCharacter(black_pattern=chr(9632),
                                    minus_pattern=chr(9633),
                                    plus_pattern=chr(9640))

standard_umbra = large_square_umbra
