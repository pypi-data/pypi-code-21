import datetime
import json
import locale
import logging
import logging.config
import os
import string
import sys

import pause
import twitter
from pymongo import MongoClient

from almanacbot import config
from almanacbot import constants

DB_EPHEMERIS = 'ephemeris'
DB_FILES = 'files'

conf = None
twitter_api = None
mongo_client = None
mongo_db = None


def _setup_logging(
        path='logging.json',
        log_level=logging.DEBUG,
        env_key='LOG_CFG'
):
    env_path = os.getenv(env_key, None)
    if env_path:
        path = env_path
    if os.path.exists(path):
        with open(path, 'rt') as f:
            log_conf = json.load(f)
        logging.config.dictConfig(log_conf)
    else:
        logging.basicConfig(level=log_level)


def _setup_twitter():
    logging.info("Setting up Twitter API client...")

    global twitter_api
    twitter_api = twitter.Api(
        consumer_key=conf.config["twitter"]["consumer_key"],
        consumer_secret=conf.config["twitter"]["consumer_secret"],
        access_token_key=conf.config["twitter"]["access_token_key"],
        access_token_secret=conf.config["twitter"]["access_token_secret"])

    logging.info("Verifying Twitter API client credentials...")
    twitter_api.VerifyCredentials()
    logging.info("Twitter API client credentials verified.")

    logging.info("Twitter API client set up.")


def _setup_mongo():
    logging.info("Setting up MongoDB client...")

    global mongo_client
    global mongo_db
    mongo_client = MongoClient(conf.config["mongodb"]["uri"])

    logging.info("Verifying MongoDB client credentials...")
    mongo_db = mongo_client[conf.config["mongodb"]["database"]]
    mongo_db.authenticate(
        conf.config["mongodb"]["user"],
        conf.config["mongodb"]["password"],
        mechanism=conf.config["mongodb"]["mechanism"])
    logging.info("MongoDB client credentials verified.")

    logging.info("MongoDB client set up.")


def _get_next_ephemeris(date):
    p_day_of_year = {
        "$project": {
            "date": 1,
            "todayDayOfYear": {"$dayOfYear": date},
            "leap": {"$or": [
                {"$eq": [0, {"$mod": [{"$year": "$date"}, 400]}]},
                {"$and": [
                    {"$eq": [0, {"$mod": [{"$year": "$date"}, 4]}]},
                    {"$ne": [0, {"$mod": [{"$year": "$date"}, 100]}]}
                ]}
            ]},
            "dayOfYear": {"$dayOfYear": "$date"}
        }
    }

    p_leap_year = {
        "$project": {
            "date": 1,
            "todayDayOfYear": 1,
            "dayOfYear": {
                "$subtract": [
                    "$dayOfYear",
                    {
                        "$cond": [
                            {"$and":
                                 ["$leap",
                                  {"$gt": ["$dayOfYear", 59]}
                                  ]},
                            1,
                            0]
                    }
                ]},
            "diff": {"$subtract": ["$dayOfYear", "$todayDayOfYear"]}
        }
    }

    p_past = {
        "$project": {
            "diff": 1,
            "birthday": 1,
            "positiveDiff": {
                "$cond": {
                    "if": {"$lt": ["$diff", 0]},
                    "then": {"$add": ["$diff", 365]},
                    "else": "$diff"
                },
            }
        }
    }

    p_sort = {
        "$sort": {
            "positiveDiff": 1
        }
    }

    p_first = {
        "$group": {
            "_id": "first_birthday",
            "first": {
                "$first": "$$ROOT"
            }
        }
    }

    res = mongo_db[DB_EPHEMERIS].aggregate([p_day_of_year, p_leap_year, p_past,
                                            p_sort, p_first])
    obj_id = res.next()['first']['_id']
    return mongo_db[DB_EPHEMERIS].find_one({"_id": obj_id})


def _tweet_ephemeris(eph):
    if eph['location']:
        twitter_api.PostUpdate(status=_process_tweet_text(eph['text'], eph),
                               latitude=eph['location']['latitude'],
                               longitude=eph['location']['longitude'],
                               display_coordinates=True)
    else:
        twitter_api.PostUpdate(status=eph.text)


def _process_tweet_text(text, eph):
    today = datetime.datetime.utcnow()

    template = string.Template(text)

    values = {
        "date": eph['date'].strftime("%d de %B de %Y"),
        "years_ago": today.year - eph['date'].year
    }

    return template.substitute(values)


def _get_next_eph_datetime(eph, now):
    eph_datetime = eph['date']
    eph_this_year = eph_datetime.replace(year=now.year)

    if eph_this_year < now:
        eph_next_year = eph_this_year.replace(year=eph_this_year.year + 1)
        return eph_next_year

    return eph_this_year


def main():
    # configure logger
    _setup_logging()

    # read configuration
    global conf
    try:
        conf = config.Configuration(constants.CONFIG_FILE_NAME)
    except Exception as exc:
        logging.error("Error getting configuration.", exc)
        sys.exit(1)

    # setup language
    try:
        locale.setlocale(locale.LC_TIME, conf.config["language"]["locale"])
    except Exception as exc:
        logging.error("Error setting up language.", exc)
        sys.exit(1)

    # setup Twitter API client
    try:
        _setup_twitter()
    except Exception as exc:
        logging.error("Error setting up Twitter API client.", exc)
        sys.exit(1)

    # setup MongoDB client
    try:
        _setup_mongo()
    except Exception as exc:
        logging.error("Error setting up MongoDB client.", exc)
        sys.exit(1)

    # loop over ephemeris
    interrupted = False
    while not interrupted:
        # get next ephemeris
        logging.info("Getting next ephemeris...")
        now = datetime.datetime.utcnow()
        next_eph = _get_next_ephemeris(now)
        logging.debug("Next ephemeris:"
                      + "\n\t -     text: " + next_eph['text']
                      + "\n\t -     date: " + str(next_eph['date'])
                      + "\n\t - location: "
                      + str(next_eph['location']['latitude']) + ", "
                      + str(next_eph['location']['longitude']))

        # wait until publication
        eph_pub_date = _get_next_eph_datetime(next_eph, now)
        logging.info("Waiting until publication time: " + str(eph_pub_date))
        try:
            pause.until(eph_pub_date)
        except (KeyboardInterrupt, SystemExit):
            interrupted = True
            logging.warning("Waiting time has been interrupted. Exiting!")
            continue

        # tweet ephemeris
        logging.info("Tweeting ephemeris...")
        _tweet_ephemeris(next_eph)

        # wait a day to avoid duplicates
        pause.days(1)


if __name__ == '__main__':
    main()
