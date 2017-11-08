#!/usr/bin/python3

#    This file is part of 'papertrade'.
#
#    papertrade is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    papertrade is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with papertrade.  If not, see <http://www.gnu.org/licenses/>.


def switch_sign(number):
    return -1 * number

def growth(buy, sell):
    factor = float(sell)/float(buy)
    percent = round((factor-1)*100, 2)
    return (percent, factor)


def difference(earnings, losses):
    # If we get a number, don't raise an exception
    if not hasattr(losses, '__iter__'):
        losses = [losses]
    if not hasattr(earnings, '__iter__'):
        earnings = [earnings]
    else:
        earnings = list(earnings)
        losses = list(losses)

    buffer = []
    for e in losses:
        if e < 0:
            e = switch_sign(e)
        buffer.insert(0, e) # Push element onto beginning of list
    losses = buffer

    return round(sum(earnings) - sum(losses), 2)
