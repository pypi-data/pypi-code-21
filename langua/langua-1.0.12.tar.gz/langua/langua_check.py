# coding=utf-8
import sys

from langua.predict_lang import  Predict
from langdetect import detect
p = Predict()

for i in range(250):
    detect(u"böcker > philipp richter Trigger Points and Muscle Chains in Osteopathy	REST")
    detect(u"Ein, zwei, drei, vier")
    detect(u"தாய்")
    detect(u"English sentence")



