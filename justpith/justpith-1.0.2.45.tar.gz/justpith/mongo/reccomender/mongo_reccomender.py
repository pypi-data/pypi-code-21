# encoding: utf-8
from ..mongo import Mongo
import operator

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


    def get_reccomendations_for_user(self, user_id, category_id_list, num_recs=10, order=0):
        # order = 0 per score raccomandazione
        # order = 1 per tempo (id news)
        collection_name = "Categories"
        selected_collection = self.connection[collection_name]
        result = selected_collection.find({ "_id" : { "$in": category_id_list } })
        #{ "_id" : 11, "name" : "Attualità", "reccomendations" : "Raccomandations_Attualità" }
        #{ "_id" : 13, "name" : "Sport" }
        #{ "_id" : 14, "name" : "Viaggi" }
        #{ "_id" : 15, "name" : "Arte e Cultura" }
        #{ "_id" : 16, "name" : "Intrattenimento", "reccomendations" : "Raccomandations_Intrattenimento" }

        reccomendations = []
        for elem in result:
            if ("name" not in elem) or ("reccomendations" not in elem):
                return -1

            category_id = int(elem["_id"])
            category_name = elem["name"]
            collection_reccomendation = elem["reccomendations"]

            selected_collection = self.connection[collection_reccomendation]

            tmp_rec = selected_collection.find_one({'_id':str(user_id)})
            if tmp_rec is None:
                #o non esiste la collezione Raccomandations_{categoria} o l'utente non esiste nella collezione
                continue

            if "raccomandations" not in tmp_rec:
                return -1

            recs_for_one_category = tmp_rec["raccomandations"]
            if order == 0:
                sorted_recs_for_one_category = sorted(recs_for_one_category.items(), key=operator.itemgetter(1), reverse=True)[0:int(num_recs)]
            elif order == 1:
                sorted_recs_for_one_category = sorted(recs_for_one_category.items(), key=operator.itemgetter(0),reverse=True)[0:int(num_recs)]
            list_id_news = [int(elem_[0]) for elem_ in sorted_recs_for_one_category]
            tmp = {
                "category_id":category_id,
                "category_name": category_name,
                "reccomendations": sorted_recs_for_one_category,
                "list_ids": list_id_news
            }
            reccomendations.append(tmp)

        return reccomendations


    def update_users_for_push_notifications(self, users):
        collection_name = "PushReccomendations"
        selected_collection = self.connection[collection_name]
        selected_collection.update({}, {"$addToSet": {"users": {"$each": users}}}, upsert=True)

    def clean_users_for_push_notifications(self):
        collection_name = "PushReccomendations"
        selected_collection = self.connection[collection_name]
        selected_collection.update({}, {"$set": {"users": []}}, upsert=True)

    def get_users_for_push_notifications(self):
        collection_name = "PushReccomendations"
        selected_collection = self.connection[collection_name]
        result = selected_collection.find_one({})
        return result

    def get_all_categories(self):
        selected_collection = self.connection['CategoriesReccomender']
        return selected_collection.find()

    def insert_category(self, id, name, enabled):
        selected_collection = self.connection['CategoriesReccomender']
        selected_collection.update_one({"_id":int(id)}, {"$set": {"name":name, "enabled": int(enabled)}},upsert=True)