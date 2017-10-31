# coding=utf-8
import sys

from langua import Predict
p = Predict()

print(p.get_lang(u"böcker > philipp richter Trigger Points and Muscle Chains in Osteopathy	REST"))
print(p.get_lang(u"Ein, zwei, drei, vier"))
print(p.get_lang(u"தாய்"))
print(p.get_lang(u"English sentence"))

"""
for i in xrange(250):
    p.get_lang(u"böcker > philipp richter Trigger Points and Muscle Chains in Osteopathy	REST")
    p.get_lang(u"Ein, zwei, drei, vier")
    p.get_lang(u"தாய்")
    p.get_lang(u"English sentence")
"""