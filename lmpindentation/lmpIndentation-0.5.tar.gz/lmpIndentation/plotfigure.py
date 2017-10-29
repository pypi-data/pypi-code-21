#!python
# -*- coding:utf-8 -*-
########################################################
# Created Date: Thursday October 26th 2017
# Author: Linyuan Shi
# Email:  Linyuan.Shi@outlook.com
# Copyright (c) 2017 Linyuan Shi
########################################################
import matplotlib.pyplot as plt
import pandas as pd


class ElasticData:
    def __init__(self, file_name, seperator=' '):
        self.data = pd.read_csv(file_name, sep=seperator)
        self.data[(self.data < 1) & (self.data > -1)] = 0

    def plot_elastic(*args, **kwargs):
