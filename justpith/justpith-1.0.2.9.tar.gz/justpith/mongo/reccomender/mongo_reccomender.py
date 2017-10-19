from ..mongo import Mongo

class MongoReccomender(Mongo):
    def __init__(self,host, port, db):
        super(MongoReccomender,self).__init__(host, port, db)

    def add_user_raccomandations(self, user_id, new_raccomandations, category):
        category = category.replace(" ", "")
        collection_name = "Raccomandations_"+category
        selected_collection = self.connection[collection_name]
        for id_news, weight in new_raccomandations.iteritems():
            res = selected_collection.update({'_id': str(user_id)}, {'$set': {'raccomandations.'+str(id_news): weight}}, upsert=True)


    def remove_user_raccomandation(self, user_id, news_id, category):
        category = category.replace(" ", "")
        collection_name = "Raccomandations_"+category
        selected_collection = self.connection[collection_name]
        selected_collection.update({'_id': str(user_id)}, {'$unset': {'raccomandations.'+str(news_id): ""}})


    def add_user_history_raccomandation(self, user_id, news_id, category, weight = 0):
        category = category.replace(" ", "")
        collection_name = "Raccomandations_"+category
        selected_collection = self.connection[collection_name]
        raccomandations = selected_collection.find({'_id': str(user_id)},{'raccomandations.'+str(news_id):1})
        if raccomandations and raccomandations.count()!=0:
            racc = raccomandations[0]['raccomandations']
            if racc:
                weight = racc[str(news_id)]
        selected_collection.update({'_id': str(user_id)}, {'$set': {'history_raccomandations.'+str(news_id): weight}}, upsert=True)


    # funzione che azzera il campo tot della collezione newsVotes per una categoria
    def reset_count_vote(self, category_id):
        collection_name = "News"
        selected_collection = self.connection[collection_name]
        cat_news = selected_collection.find({'category_id': category_id}, {'_id': 1})
        for news in cat_news:
            collection_name = "NewsVotes"
            selected_collection = self.connection[collection_name]
            news_id = news['_id']
            selected_collection.update({'_id': news_id},{"$set":{"tot":0}})