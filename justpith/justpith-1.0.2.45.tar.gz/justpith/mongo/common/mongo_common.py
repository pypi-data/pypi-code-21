from ..mongo import Mongo

class MongoCommon(Mongo):
    def __init__(self,host, port, db):
        super(MongoCommon,self).__init__(host, port, db)

    def get_staged_news(self, category):
        selected_collection = self.connection["NewsStage"]
        result = selected_collection.find_one({})[category]
        return result

    def get_news_list_by_id(self, list_id):
        selected_collection = self.connection["News"]
        result = selected_collection.find({"_id": {"$in": list_id}}, {"article_cleaned": 1})
        return result