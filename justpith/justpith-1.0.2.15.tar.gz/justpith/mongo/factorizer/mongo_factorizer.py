from ..mongo import Mongo

class MongoFactorizer(Mongo):
    def __init__(self,host, port, db):
        super(MongoFactorizer,self).__init__(host, port, db)


    # def get_staged_news(self):
    #     selected_collection = self.connection["NewsStage"]
    #     result = selected_collection.find_one({})
    #     return result

    def get_voted_news(self, news_list):
        selected_collection = self.connection["NewsVotes"]
        result = selected_collection.find({"_id": {"$in": news_list}})
        return result

    def write_mf_raccomandation(self, id_job, id_user, raccomandation_list):
        selected_collection = self.connection["Users"]
        result = selected_collection.update({"_id": id_user}, {"$set": {"mf_raccomandations."+str(id_job): raccomandation_list}}, upsert=True)

    def insert_matrix(self, data):
        selected_collection = self.connection["Matrix"]
        result = selected_collection.insert(data)


