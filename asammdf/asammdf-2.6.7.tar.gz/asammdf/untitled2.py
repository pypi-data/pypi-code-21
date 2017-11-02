# -*- coding: utf-8 -*-
"""
Created on Sun Oct 29 11:57:37 2017

@author: Daniel
"""

from asammdf import MDF

MDF('d:\Work\mdf\Examples\DataList\Vector_DL_Linked_List.MF4').get('channel1').plot()