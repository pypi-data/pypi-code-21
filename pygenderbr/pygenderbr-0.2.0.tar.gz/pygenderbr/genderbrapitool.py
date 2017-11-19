# -*- coding: utf-8 -*-
"""
    Module Class that interface with "Nomes" IBGE API

"""

import pandas as pd
from requests import get
from random import randint
from time import sleep
class Gender:
    """
    Class tool that run requests on 'Nomes' IBGE API

        Methods
            getgender()
            getgenderoccurrence()
            getoccurrence()
            getranking()

    """

    def __init__(self):
        """
        Create a empty object and initialize the attributes

        """

        self.urlsts = 'http://servicodados.ibge.gov.br/api/v1/localidades/estados'
        self.urlnames = 'http://servicodados.ibge.gov.br/api/v2/censos/nomes/'
        return

    def getgender(self, name, threshold=0.9):
        """
        Get the name(s) gender from the IBGE census database, based on a threshold
        value that represent the minimim limit of percent occurrence of name(s)
        to it be on a specific gender.
        Returns a dataframe resume with name(s) gender ('F' or 'M').

        :param name: string ou string list with name(s) to get occurrence.
        :param threshold: minimum percent value that represent a limit of gender.
        :return: dataframe with name(s) gender ('F' or 'M')
        """

        if not type(threshold) == float:
            print("ERROR: Threshold parameter should be a "
                  "float number.")
            return None
        if type(name) == str:
            pass
        elif type(name) == list:
            for n in name:
                if not type(n) == str:
                    print("ERROR: Name parameter should be a "
                          "string or list of string.")
                    return None
        else:
            print("ERROR: Name parameter should be a string or list of string.")
            return None
        gender = self.getgenderoccurrence(name)
        pgenderm = gender['M'] / (gender['M'] + gender['F'])
        pgenderf = gender['F'] / (gender['M'] + gender['F'])
        pgender = pd.DataFrame([pgenderf, pgenderm], index=['F', 'M']).transpose()
        isgenderf = pgender['F'] > threshold
        pgender['gender'] = isgenderf.map(lambda x: 'F' if x else 'M')
        return pgender['gender']

    def getgenderoccurrence(self, name, locale=None):
        """
        Get the name(s) occurrence(s) from the IBGE census database.
        Returns a dataframe resume with number of times that name(s) occurs per gender.

        :param name: string ou string list with name(s) to get occurrence.
        :param locale: specify locale (state abrev) to get the name(s) occurrence(s).
        :return: dataframe with name(s) occurrence(s) per gender
        """

        if locale:
            self.sts = self.__getsts()
            if not self.sts.empty:
                if not locale in self.sts['sigla'].tolist():
                    print("ERROR: State abbreviation not valid! Discarding "
                          "locale option.")
                    locale = None
            else:
                    print("ERROR: States Dataframe not loaded! Discarding "
                          "locale option.")
                    locale = None
        if type(name) == str:
            pass
        elif type(name) == list:
            for n in name:
                if not type(n) == str:
                    print("ERROR: Name parameter should be a "
                          "string or list of string.")
                    return None
        else:
            print("ERROR: Name parameter should be a string or list of string.")
            return None
        mgender = self.getoccurrence(name, gender='M', locale=locale)
        sleep(randint(1, 3))
        fgender = self.getoccurrence(name, gender='F', locale=locale)
        if type(mgender) is pd.DataFrame and type(fgender) is pd.DataFrame:
            mgender.set_index('name',inplace=True)
            fgender.set_index('name',inplace=True)
            gender = pd.concat([mgender, fgender], axis=1, ignore_index=True)
            gender.columns = ['M','F']
            gender.fillna(0,inplace=True)
            return gender
        else:
            print("ERROR: Gender missing data")
            return None

    def getoccurrence(self, name, gender=None, locale=None):
        """
        Get the name(s) occurrence(s) from the IBGE census database.
        Returns a dataframe with number of times that name(s) occurs.

        :param name: string ou string list with name(s) to get occurrence.
        :param gender: specify gender to get the name(s) occurrence(s).
        :param locale: specify locale (state abrev) to get the name(s) occurrence(s).
        :return: dataframe with name(s) occurrence(s)
        """

        urlpar = []
        if gender:
            if gender in ['M','F']:
                urlpar.append('sexo='+gender)
            else:
                print("ERROR: gender parameter should be 'M' or 'F'. " 
                      "Discarding gender option.")
                gender = None
        if locale:
            self.sts = self.__getsts()
            if not self.sts.empty:
                if locale in self.sts['sigla'].tolist():
                    st_id = self.sts[self.sts['sigla']==locale]['id'].item()
                    urlpar.append('localidade='+str(st_id))
                else:
                    print("ERROR: State abbreviation not valid! Discarding "
                          "locale option.")
                    locale = None
            else:
                    print("ERROR: States Dataframe not loaded! Discarding "
                          "locale option.")
                    locale = None
        if type(name) == str:
            url = self.urlnames + name
        elif type(name) == list:
            for n in name:
                if not type(n) == str:
                    print("ERROR: Name parameter should be a "
                          "string or list of string.")
                    return None
            url = self.urlnames + '|'.join(name)
        else:
            print("ERROR: Name parameter should be a string or list of string.")
            return None

        if urlpar:
            urlpar = '?'+'&'.join(urlpar)
        else:
            urlpar = ''
        names = self.__getresponse(url+urlpar)
        if names[0] == 200:
            names_dict = []
            values_dict = []
            for iname in names[1]:
                names_dict.append(iname['nome'])
                total = 0
                for occur in iname['res']:
                    total += occur['frequencia']
                values_dict.append(total)
            names_df = pd.DataFrame({'name':names_dict,'occurrence':values_dict})
            return names_df
        else:
            return None

    def getranking(self, gender=None, decade=None, locale=None):
        """
        Get the names ranking with 20's most used names on Brazil or state.
        The ranking would be on specific gender or specific decade (between
        1900 and 2010).

        :param gender: specify gender to get the names ranking.
        :param decade: specify decade to get the names ranking.
        :param locale: specify locale (state abrev) to get the names ranking.
        :return: dataframe with name(s) ranking
        """

        urlpar = []
        if gender:
            if gender in ['M','F']:
                urlpar.append('sexo='+gender)
            else:
                print("ERROR: gender parameter should be 'M' or 'F'. " 
                      "Discarding gender option.")
                gender = None
        if decade:
            decade = int(decade)
            if decade>1900 and decade <= 2011:
                urlpar.append('decada='+str(decade))
            else:
                print("ERROR: decade parameter should between 1900 and 2010. "
                      "Discarding decade option.")
                decade = None
        if locale:
            self.sts = self.__getsts()
            if not self.sts.empty:
                if locale in self.sts['sigla'].tolist():
                    st_id = self.sts[self.sts['sigla']==locale]['id'].item()
                    urlpar.append('localidade='+str(st_id))
                else:
                    print("ERROR: State abbreviation not valid! Discarding "
                          "locale option.")
                    locale = None
            else:
                    print("ERROR: States Dataframe not loaded! Discarding "
                          "locale option.")
                    locale = None
        if urlpar:
            urlpar = 'ranking?'+'&'.join(urlpar)
        else:
            urlpar = 'ranking'
        ranking = self.__getresponse(self.urlnames+urlpar)
        if ranking[0] == 200:
            ranking_df = pd.DataFrame(ranking[1][0]['res'])
            return ranking_df
        else:
            return None

    def __getsts(self):
        """
        Get the Brazil states data from 'localidades' IBGE API.

        :return: states dataframe
        """

        sts = self.__getresponse(self.urlsts)
        if sts[0] == 200:
            sts_dataframe = pd.DataFrame(sts[1])
            return sts_dataframe
        else:
            return None

    def __getresponse(self, url):
        """
        Get the response from 'Nomes' IBGE API. on error occurrence, returns
        the Error Status Code and Error reason.

        :param url: API url to get response.
        :return: Tuple with response status code and response content json
        """

        try:
            response = get(url)
        except:
            print("ERROR: Request timeout")
            return (0, 'Request Timeout')
        if response.ok:
            return (response.status_code,response.json())
        else:
            print("ERROR: Request - ",
                  response.status_code, " : ", response.reason)
            return (response.status_code, response.reason)