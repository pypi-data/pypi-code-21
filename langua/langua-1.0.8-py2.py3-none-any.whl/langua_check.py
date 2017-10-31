# coding=utf-8
import sys

from langua import Predict

p = Predict()

print(p.get_lang("This is english"))

print(p.get_lang(u"ഇംഗ്ലീഷ്"))