#!/usr/bin/python

from xconnectpy.lib.base import Facet


class Address(Facet):
    def __init__(self, AddressLine1: str="", AddressLine2: str="", AddressLine3: str="", AddressLine4: str="",
                 City: str="", PostalCode: str="", CountryCode: str="", GeoCoordinate: str="", StateOrProvince: str=""):

        if AddressLine1:
            self.AddressLine1 = AddressLine1
        if AddressLine2:
            self.AddressLine2 = AddressLine2
        if AddressLine3:
            self.AddressLine3 = AddressLine3
        if AddressLine4:
            self.AddressLine4 = AddressLine4
        if City:
            self.City = City
        if PostalCode:
            self.PostalCode = PostalCode
        if CountryCode:
            self.CountryCode = CountryCode
        if GeoCoordinate:
            self.GeoCoordinate = GeoCoordinate
        if StateOrProvince:
            self.StateOrProvince = StateOrProvince
