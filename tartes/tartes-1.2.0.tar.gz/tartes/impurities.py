# -*-coding:utf-8 -*
#
# TARTES, Copyright (c) 2014, Quentin Libois, Picard Ghislain 
# All rights reserved. 
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# 


from numpy import log
import math

class Soot(object):
    """class defining soot"""

    density = 1800.0

    @classmethod
    def refractive_index_imag(cls,wavelength):
        """return the imaginary part of the refracive index (= absorption) for soot."""
        # index from Chang (1990)
        #wl_um=1e6*wavelength

        #index_soot_real=1.811+0.1263*log(wl_um)+0.027*log(wl_um)**2+0.0417*log(wl_um)**3
        #index_soot_im=0.5821+0.1213*log(wl_um)+0.2309*log(wl_um)**2-0.01*log(wl_um)**3

        #m_soot = index_soot_real -1j * index_soot_im
        
        m_soot = 1.95-1j * 0.79
        n=(m_soot**2-1)/(m_soot**2+2) #absorption cross section of small particles (Bohren and Huffman, 1983)

        return n.imag


class HULIS(object):

    density = 1500.0

    @classmethod
    def refractive_index_imag(cls,wavelength):
        """return the imaginary part of the refracive index (= absorption) for HULIS."""

        #HULIS from Hoffer (2006)
        wl_um=1e6*wavelength
        m_hulis=1.67-8e17*1j*(wl_um*1e3)**(-7.0639)*1e3*cls.density*wl_um*1e-6/(4*math.pi)
        n=(m_hulis**2-1)/(m_hulis**2+2)

        return n.imag
