import uuid
import requests
import simplejson
import logging

from bson import ObjectId
from pymongo import MongoClient


class DatabaseUtils(object):
    def __init__(self, dbconfig, fbaccesstoken):
        self.dbconfig = dbconfig
        self.fbaccesstoken = fbaccesstoken
        client = MongoClient(dbconfig['host'], dbconfig['port'])
        # client.drop_database(constants.DATABASE_NAME)
        self.db = client[dbconfig['name']]

    def get_user(self, sender):
        """Returns user object from database."""
        user = self.db.User
        current_sender = None
        current_user = user.find({
            'user_id': str(sender)})
        for document in current_user:
            current_sender = document
        if current_sender is None:
            if sender.isdigit():
                current_sender = self.generate_new_fb_user(sender)
            else:
                current_sender = self.generate_new_user()
        logging.debug('{}: Getting user from database. User = {}'.format(sender, current_user))
        return current_sender

    def generate_new_fb_user(self, sender):
        """Generates new Facebook user in database."""
        user = self.db.User
        current_sender = None
        try:
            logging.info(' Fetching user({0}) data from Facebook({1}).....'.format(sender, self.fbaccesstoken))
            resp = requests.get(
                'https://graph.facebook.com/v2.6/' + sender + '?fields=first_name,last_name,profile_pic,locale,'
                                                              'timezone,gender&access_token=' + self.fbaccesstoken)
            logging.info(' Facebook response: {0}'.format(str(resp.text)))
            fb_user = simplejson.loads(str(resp.text))
            current_sender = dict()
            current_sender['_id'] = ObjectId()
            current_sender["is_input_expected"] = False
            current_sender["expected_input"] = ""
            current_sender['user_id'] = sender
            current_sender['active'] = True
            if fb_user.get('first_name'):
                current_sender['first_name'] = fb_user['first_name']
            if fb_user.get('last_name'):
                current_sender['last_name'] = fb_user['last_name']
            if fb_user.get('gender'):
                current_sender['gender'] = fb_user['gender']
            if fb_user.get('profile_pic'):
                current_sender['profile_pic'] = fb_user['profile_pic']
            if fb_user.get('locale'):
                current_sender['locale'] = fb_user['locale']
            if fb_user.get('timezone'):
                current_sender['timezone'] = fb_user['timezone']
            user.insert(current_sender)
            logging.info(' Created new user: {0}'.format(current_sender['user_id']))
        except:
            logging.error(' Error creating new user')
        return current_sender

    def generate_new_user(self):
        """Generates new user in database."""
        user = self.db.User
        user_id = uuid.uuid4().urn[9:]
        logging.debug(' generated user = {0}'.format(user_id))
        current_sender = None
        current_user = user.find({
            'user_id': str(user_id)})
        for document in current_user:
            current_sender = document
        if current_sender is None:
            try:
                current_sender = self.constants.USER_OBJECT
                current_sender['user_id'] = user_id
                current_sender["is_input_expected"] = False
                current_sender["expected_input"] = ""
                logging.info(' Created new user: {0}'.format(user.insert_one(current_sender).inserted_id))
            except:
                logging.error(' Error creating new user')
        return current_sender

    def update_user(self, sender, data_for_update):
        """Updates user object in database."""
        self.db.User.update_one({
            'user_id': sender
        }, {
            '$set': data_for_update
        }, upsert=False)
        logging.debug('{}: Updating user. Data = {}'.format(sender, data_for_update))

    def is_input_expected(self, sender):
        """Checks if input is expected."""
        user = self.db.User
        current_user = user.find({
            "user_id": str(sender)})
        is_expected = False
        try:
            for document in current_user:
                is_expected = document["is_input_expected"]
        except:
            return False
        return is_expected

    def get_expected_input_type(self, sender):
        """Returns expected input type."""
        user = self.db.User
        current_user = user.find({
            "user_id": str(sender)})
        expected_input = ""
        for document in current_user:
            expected_input = document["expected_input"]
        return expected_input

    def get_users(self):
        """Returns list of all users in database."""
        userslist = []
        user = self.db.User
        users = user.find({})
        for u in users:
            userslist.append(u)
        return userslist

    def change_chatbot_active(self, sender):
        """Changes current chatbot status."""
        user = self.db.User
        isactive = True
        current_user = user.find({
            "user_id": str(sender)})
        try:
            for document in current_user:
                isactive = document["active"]
        except KeyError:
            isactive = True
        if isactive:
            isactive = False
        else:
            isactive = True
        self.db.User.update_one({
            'user_id': sender
        }, {
            '$set': {'active': isactive}
        }, upsert=False)

    def is_chatbot_active(self, sender):
        """Returns chatbot status."""
        user = self.db.User
        isactive = True
        current_user = user.find({
            "user_id": str(sender)})
        try:
            for document in current_user:
                isactive = document["active"]
        except KeyError:
            return isactive
        return isactive

