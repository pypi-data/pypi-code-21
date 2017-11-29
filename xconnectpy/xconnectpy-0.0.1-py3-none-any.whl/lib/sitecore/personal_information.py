#!/usr/bin/python

from datetime import datetime

from xconnectpy.lib.base import Facet


class PersonalInformation(Facet):

    DefaultFacetKey = "Personal"

    def __init__(self, BirthDate: datetime=None, FirstName: str="", MiddleName: str="",
                 LastName: str="", Gender: str="", JobTitle: str="", Nickname: str="", Suffix: str="",
                 Title: str="", PreferredLanguage: str =""):

        if BirthDate:
            self.BirthDate = BirthDate
        if FirstName:
            self.FirstName = FirstName
        if MiddleName:
            self.MiddleName = MiddleName
        if LastName:
            self.LastName = LastName
        if Gender:
            self.Gender = Gender
        if JobTitle:
            self.JobTitle = JobTitle
        if Nickname:
            self.Nickname = Nickname
        if Suffix:
            self.Suffix = Suffix
        if Title:
            self.Title = Title
        if PreferredLanguage:
            self.PreferredLanguage = PreferredLanguage
