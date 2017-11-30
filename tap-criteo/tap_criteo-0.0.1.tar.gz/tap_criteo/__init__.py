#!/usr/bin/env python3

import sys
import time
import datetime
import argparse
import xml.etree.ElementTree as ET
from urllib.request import urlopen
from pyrfc3339 import parse
from suds.client import Client as soapclient
from suds import WebFault
import singer
from singer import utils

PARSER = argparse.ArgumentParser()
PARSER.add_argument('--config', action='store', dest='path',
                    help='Path for configuration file')
PARSER.add_argument('--state', action='store', dest='state',
                    help='Path for state file')

ARGUMENTS = PARSER.parse_args()

LOGGER = singer.logger.get_logger()
URL = 'https://advertising.criteo.com/API/v201305/AdvertiserService.asmx'

if ARGUMENTS.path is None:
    LOGGER.error('Specify configuration file folder.')
    sys.exit(1)

PATH = ARGUMENTS.path
AUTH = utils.load_json(PATH)

CLIENT = soapclient('https://advertising.criteo.com/API/v201305/AdvertiserService.asmx?WSDL')
HEADERS = CLIENT.factory.create('apiHeader')


if ARGUMENTS.state:
    STATE = utils.load_json(ARGUMENTS.state)
    STATE_DEFINED = True
else:
    STATE = {"aggregationType": "Hourly",\
                       "startDate":"",\
                       "reportType":"",\
                       "endDate": "",\
            	           "reportSelector": {},\
            	           "isResultGzipped": "False",\
            	           "selectedColumns": []\
            }
    STATE_DEFINED = False

CAMPAIGN_SCHEMA = {"type": ["null", "object"], \
                  "properties":\
                     {"campaignID": {"type":["number"]},
                      "campaignName": {"type":["null", "string"]},
                      "biddingStrategy": {"type":["null", "string"]},
                      "cpc": {"type":["null", "number"]},
                      "cpa": {"type":["null", "number"]},
                      "budgetID": {"type":["null", "number"]},
                      "remainingDays": {"type":["null", "number"]},
                      "status": {"type":["null", "string"]},
                      "categoryBids":{"type":["null", "string"]}
                     }
                  }

CATEGORY_SCHEMA = {"type": ["null", "object"],
                   "properties":{"categoryID": {"type":["number"]},
                                 "categoryName": {"type":["null", "string"]},
                                 "avgPrice": {"type":["null", "number"]},
                                 "numberOfProducts":{"type":["null", "number"]},
                                 "selected": {"type":["null", "boolean"]}
                                }
                  }

BUDGET_SCHEMA = {"type": ["null", "object"],
                 "properties":{"budgetID":{"type":["number"]},
                               "budgetName": {"type":["string"]},
                               "totalAmount": {"type":["number"]},
                               "remainingBudget": {"type":["number"]},
                               "remainingBudgetUpdated": {"type":["string"]}
                              }
                }

ACCOUNT_SCHEMA = {"type": ["null", "object"],
                  "properties":{"advertiserName": {"type":["string"]},
                                "email": {"type":["null", "string"]},
                                "currency": {"type":["null", "string"]},
                                "timezone": {"type":["null", "string"]},
                                "country": {"type":["null", "string"]}
                               }
                 }

CAMPAIGN_METRICS_SCHEMA = {"type": ["null", "object"],
                           "properties":{"campaignID": {"type":["string"]},
                                        	"dateTimePosix": {"type":["string"]},
                                        	"dateTime":{"type":["string"]},
                                        	"click":{"type":["string"]},
                                        	"impressions":{"type":["string"]},
                                        	"CTR":{"type":["string"]},
                                        	"revcpc":{"type":["string"]},
                                        	"ecpm":{"type":["string"]},
                                        	"cost":{"type":["string"]},
                                        	"sales":{"type":["string"]},
                                        	"convRate":{"type":["string"]},
                                        	"orderValue":{"type":["string"]},
                                        	"salesPostView":{"type":["string"]},
                                        	"convRatePostView":{"type":["string"]},
                                        	"orderValuePostView":{"type":["string"]},
                                        	"costOfSale":{"type":["string"]},
                                        	"overallCompetitionWin":{"type":["string"]},
                                        	"costPerOrder":{"type":["string"]}
                        	               }
                          }
CATEGORY_METRICS_SCHEMA = {"type": ["null", "object"],
                           "properties":{"campaignID": {"type":["string"]},
                                        	"dateTimePosix": {"type":["string"]},
                                        	"dateTime":{"type":["string"]},
                                        	"click":{"type":["string"]},
                                        	"impressions":{"type":["string"]},
                                        	"CTR":{"type":["string"]},
                                        	"revcpc":{"type":["string"]},
                                        	"ecpm":{"type":["string"]},
                                        	"cost":{"type":["string"]},
                                        	"sales":{"type":["string"]},
                                        	"convRate":{"type":["string"]},
                                        	"orderValue":{"type":["string"]},
                                        	"salesPostView":{"type":["string"]},
                                        	"convRatePostView":{"type":["string"]},
                                        	"orderValuePostView":{"type":["string"]},
                                        	"costOfSale":{"type":["string"]},
                                        	"overallCompetitionWin":{"type":["string"]},
                                        	"costPerOrder":{"type":["string"]}
                                        }
                          }

def login():
    try:
        HEADERS.authToken = CLIENT.service.clientLogin(AUTH['username'], \
                                                       AUTH['password'], \
                                                       AUTH['clientversion'])
    except WebFault:
        LOGGER.error('Login error, please check config file')
        sys.exit(1)
    HEADERS.appToken = AUTH['apptoken']
    HEADERS.clientVersion = AUTH['clientversion']
    CLIENT.set_options(soapheaders=HEADERS)

def getacc():
    try:
        account = CLIENT.service.getAccount()
        LOGGER.info('Login Done')
    except WebFault:
        LOGGER.error('Login error, please check config file')
        sys.exit(1)
    except:
        LOGGER.error('Login error, please check config file')
        sys.exit(1)
    singer.write_schema('accounts', ACCOUNT_SCHEMA, ['advertiserName'])
    time.sleep(1)
    acc = dict(account)
    if any(acc):
        singer.write_record('accounts', acc)

def getbudget():
    budgets = CLIENT.service.getBudgets()
    singer.write_schema('budgets', BUDGET_SCHEMA, ['budgetID'])
    for budget in budgets:
        for bud in budget[1:]:
            singer.write_record('budgets', dict(bud[0]))

def getcampaign():
    campaigns = CLIENT.service.getCampaigns()
    singer.write_schema('campaigns', CAMPAIGN_SCHEMA, ['campaignID'])
    campaigns_list = []
    for acmp in campaigns:
        for cmp in acmp[1:]:
            camp = dict(cmp[0])
            if camp['campaignBid'] != None:
                camp['biddingStrategy'] = camp['campaignBid']['biddingStrategy']
                if camp['campaignBid']['cpcBid'] != None:
                    camp['cpc'] = camp['campaignBid']['cpcBid']['cpc']
                if camp['campaignBid']['cpaBid'] != None:
                    camp['cpa'] = camp['campaignBid']['cpaBid']['cpa']
            camp['categoryBids'] = str(camp['categoryBids'])
            camp.pop('campaignBid')
            campaigns_list.append(camp['campaignID'])
            singer.write_record('campaigns', camp)
    return campaigns_list

def filterconstructure(filters, incrementby):
    if STATE_DEFINED:
        start_date = datetime.datetime(int(filters['endDate'].split('-')[0]),
                                       int(filters['endDate'].split('-')[1]),
                                       int(filters['endDate'].split('-')[2])) \
                     + datetime.timedelta(days=1)
    else:
        start_date = parse(AUTH['start_date'])
    end_date = str(start_date + datetime.timedelta(days=incrementby)).split(' ')[0]
    filters['startDate'] = str(start_date).split(' ')[0]
    filters['endDate'] = end_date
    filters['isResultGzipped'] = False

def downloadcampaignreport():
    filters = STATE
    camp = getcampaign()
    filterconstructure(filters, int(AUTH['increment']))
    if not camp:
        LOGGER.info('0 rows for campaign')
    else:
        filters['reportSelector'] = {'CampaignIDs':camp}
        filters['reportType'] = 'Campaign'
        jobid = CLIENT.service.scheduleReportJob(filters)
        while True:
            if CLIENT.service.getJobStatus(jobid) == 'Completed':
                tab = ET.parse(urlopen(CLIENT.service.getReportDownloadUrl(jobid))) \
                        .getroot().getchildren()[0]
                break
        rows = [i for i in tab if i.tag == 'rows'][0]
        singer.write_schema('campaignmertics', CAMPAIGN_METRICS_SCHEMA, ['campaignID', 'dateTime'])
        for row in rows:
            singer.write_record('campaignmertics', row.attrib)

def getcategory():
    category = CLIENT.service.getCategories()
    singer.write_schema('categories', CATEGORY_SCHEMA, ['categoryID'])
    categories_list = []
    for catlist in category:
        for cat in catlist[1:]:
            catdict = dict(cat[0])
            singer.write_record('categories', catdict)
            categories_list.append(catdict['categoryID'])
    return categories_list


def downloadcategoryreport():
    filters = STATE
    cate = getcategory()
    if not cate:
        LOGGER.info('0 rows for category report')
    else:
        filters['reportSelector'] = {'CategoryIDs':cate}
        filters['reportType'] = 'Category'
        jobid = CLIENT.service.scheduleReportJob(filters)
        while True:
            if CLIENT.service.getJobStatus(jobid) == 'Completed':
                tab = ET.parse(urlopen(CLIENT.service.getReportDownloadUrl(jobid))) \
                        .getroot().getchildren()[0]
                break
        rows = [i for i in tab if i.tag == 'rows'][0]
        singer.write_schema('categoriemetrics', CATEGORY_METRICS_SCHEMA, ['categoryID', 'dateTime'])
        for row in rows:
            singer.write_record('campaignsmetrics', row.attrib)

def main():
    login()
    getacc()
    LOGGER.info('Account data downloaded')
    getbudget()
    LOGGER.info('Budget data downloaded')
    downloadcampaignreport()
    LOGGER.info('Campaign report downloaded')
    downloadcategoryreport()
    LOGGER.info('Category Report downloaded')
    singer.write_state(STATE)


if __name__ == "__main__":
    main()
