#! usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 00:17:15 2017

@author: vijay

"""

from itertools import groupby
import pandas as pd

"""
RLE-RunLengthEncoding is a framework in python
using pandas and groupby

It is majorly used to compress the data by finding 
the correct indices required to compress

Example:
--------

input = pd.DataFrame([10, 10, 10, 20, 20, 11, 21, 11, 20,
                       20, 10, 10], columns=["data"])
or

input = "aabbbaababacccddbbddaa"

or

input = [10, 10, 10, 20, 20, 11, 21, 11, 20,
                       20, 10, 10]

So, it can take dataframe or list or string as an input for data
compression

rle = RLE(data_for_rle=input) or RLE(input)
rle.solve(otype=params) or rle.solve(params)

# For output you can check the attributes of RLE.solve method

rle.df will return ~
       length  status  cumsum  start_index  end_index
    0       3      10       3            0          2
    1       2      20       5            3          4
    2       1      11       6            5          5
    3       1      21       7            6          6
    4       1      11       8            7          7
    5       2      20      10            8          9
    6       2      10      12           10         11

rle.start_index will return ~
[0, 3, 5, 6, 7, 8, 10]

rle.end_index will return ~
[2, 4, 5, 6, 7, 9, 11]

"""


class RLE(object):

    def __init__(self, data_for_rle="No Data"):
        self.data_for_rle = data_for_rle

    def _convertor(self):
        if type(self.data_for_rle) is list:
            self.data_for_rle = self.data_for_rle
        elif type(self.data_for_rle) is str:
            self.data_for_rle = self.data_for_rle
        elif type(self.data_for_rle) is pd.core.series.Series:
            self.data_for_rle = self.data_for_rle.tolist()

    def encoder(self):
        self._convertor()
        return [(len(list(j)), i) for i, j in groupby(self.data_for_rle)]

    def solve(self, otype="start"):
        """
        Performs index search for given data
        :param otype: It's a string which give user to find what type of index from the \
                data whether it is start index or end index or both. For start_index it is "start"\
                end index it is "end" and for both it is "both"
        :type otype: string
        :default otype: "start"

        Attributes:
        ==========
        :df : which gives complete dataframe after finding the index
        :start_index: which gives start_index of the given data in list\
                if you used both or start as a otype
        :end_index: which gives end_index of the given data in list\
                if you used both or end as a otype
        """

        self.df = pd.DataFrame({
            "length": [data[0] for data in self.encoder()],
            "status": [data[1] for data in self.encoder()]
        })

        self.df["cumsum"] = self.df["length"].cumsum()

        if otype is "start":
            self.df["start_index"] = self.df["cumsum"] - self.df["length"]
            self.start_index = self.df["start_index"].tolist()
        elif otype is "end":
            self.df["end_index"] = self.df["cumsum"] - 1
            self.end_index = self.df["end_index"].tolist()
        elif otype is "both":
            self.df["start_index"] = self.df["cumsum"] - self.df["length"]
            self.df["end_index"] = self.df["cumsum"] - 1
            self.start_index = self.df["start_index"].tolist()
            self.end_index = self.df["end_index"].tolist()


# if __name__ == "__main__":
#     df = pd.DataFrame([10, 10, 10, 20, 20, 11, 21, 11, 20,
#                        20, 10, 10], columns=["data"])
#     # [1,1,1,0,0,1,0,1,0,1,0,0] #df["ign_status"]
#     input_list = "aabbbaababacccddbbddaa"
#     #input_list = [0,1,2,3,4,5,6,7,8,9,10,11]
#     rle = RLE(data_for_rle=df["data"])
#     #print (rle.encoder())
#     rle.solve("both")
#     print(rle.start_index)
