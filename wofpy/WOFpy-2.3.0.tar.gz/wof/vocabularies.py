from __future__ import (absolute_import, division, print_function)

import datetime
import json
import logging
import pytz
import os

from lxml import objectify
from suds.client import Client


def parse_xml(xml):
    termarr = []
    root = objectify.XML(xml)
    for r in root.Records.getchildren():
        if root.tag == 'GetSpatialReferencesResponse':
            termarr.append(r.SRSName.text)
        elif root.tag == 'GetUnitsResponse':
            termarr.append(r.UnitsType.text)
        else:
            termarr.append(r.Term.text)

    return list(set(termarr))


def update_watermlcvs():
    WSDL_URL = 'http://his.cuahsi.org/odmcv_1_1/odmcv_1_1.asmx?WSDL'

    work_dir = os.path.abspath(os.path.curdir)

    try:
        CLIENT = Client(url=WSDL_URL)

        watermlcvs = {
            'updated': datetime.datetime.now(pytz.utc).isoformat(),
            'cv': {
                'datatype': parse_xml(CLIENT.service.GetDataTypeCV()),
                'unitstype': parse_xml(CLIENT.service.GetUnits()),
                'samplemedium': parse_xml(CLIENT.service.GetSampleMediumCV()),
                'generalcategory': parse_xml(CLIENT.service.GetGeneralCategoryCV()),
                'valuetype': parse_xml(CLIENT.service.GetValueTypeCV()),
                'censorcode': parse_xml(CLIENT.service.GetCensorCodeCV())
            }
        }

        json.dump(watermlcvs, open(os.path.join(work_dir, 'watermlcvs.json'), 'wb'))
        print('Success, WaterML 1.1 controlled vocabularies have been updated.')
    except:
        print('Can\'t connect to CUAHSI Service, WaterML 1.1 controlled vocabularies are not updated.')


def get_watermlcvs():
    return json.load(open(os.path.join(os.path.abspath(os.path.curdir),
                                       'watermlcvs.json'), 'rb'))


def check_dataTypeEnum(term, validate=True):
    cv, default = "datatype", "Unknown"
    return _check_CVTerm(cv, term, default, checknone=True, validate=validate)


def check_UnitsType(term, validate=True):
    # "Unknown" is not actually a valid WaterML 1.1 UnitsType term, but there is no equivalent. So be it
    cv, default = "unitstype", "Unknown"
    return _check_CVTerm(cv, term, default, checknone=True, validate=validate)


def check_SampleMedium(term, validate=True):
    cv, default = "samplemedium", "Unknown"
    return _check_CVTerm(cv, term, default, checknone=True, validate=validate)


def check_generalCategory(term, validate=True):
    cv, default = "generalcategory", "Unknown"
    return _check_CVTerm(cv, term, default, checknone=True, validate=validate)


def check_valueType(term, validate=True):
    cv, default = "valuetype", "Unknown"
    return _check_CVTerm(cv, term, default, checknone=True, validate=validate)


def check_censorCode(term, validate=True):
    cv, default = "censorcode", "nc"
    return _check_CVTerm(cv, term, default, checknone=False, validate=validate)


# This checker is odd, as it's not actually checking against an existing WaterML 1.1 CV
# So, it's not using the common _check_CVTerm machinery at this time
def check_QualityControlLevel(term):
    default = "Unknown"
    cvterms = [
        "Raw data",
        "Quality controlled data",
        "Derived products",
        "Interpreted products",
        "Knowledge products",
        "Unknown",
    ]

    if term in cvterms:
        return term
    else:
        return default


def _check_CVTerm(cv, term, termdefault, checknone=True, validate=True):

    if checknone and term is None:
        logging.warn('default returned: {} term is not specified'.format(cv))
        return termdefault

    if validate:
        cvterms = get_watermlcvs()['cv'][cv]

        if term in cvterms:
            return term
        else:
            logging.warn('default returned: {0} {1} term does not match CV terms list'.format(cv, term))
            return termdefault
    else:
        return term