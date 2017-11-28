# encoding: utf-8
from ..mongo import Mongo

class MongoNewsConsumer(Mongo):
    def __init__(self,host, port, db):
        super(MongoNewsConsumer,self).__init__(host, port, db)

    def get_all_categories(self):
        selected_collection = self.connection['CategoriesNewsConsumer']
        return selected_collection.find()

    def update_category(self, id, name, enabled):
        selected_collection = self.connection['CategoriesNewsConsumer']
        selected_collection.update({'_id': id}, {'$set': {'name': name, 'enabled': enabled}})

    def insert_category(self, id, name, enabled, status):
        selected_collection = self.connection['CategoriesNewsConsumer']
        to_insert = {'_id': id, 'name': name, 'enabled': enabled, 'status': status}
        selected_collection.insert(to_insert)

    def update_category_status(self, category):
        selected_collection = self.connection['CategoriesNewsConsumer']
        selected_collection.update({'name': category}, {'$set': {'status': 1}})