from ..mongo import Mongo

import datetime

class MongoWebApp(Mongo):
    def __init__(self,host, port, db):
        super(MongoWebApp,self).__init__(host, port, db)


    def get_news_reccomandations2(self, user_id,category):
        category = category.replace(" ", "")
        collection_name = "Raccomandations_" + category
        racc_list = []
        try:
            selected_collection = self.connection[collection_name]
            raccomandations = selected_collection.find_one({'_id': str(user_id)}, {'raccomandations': 1})['raccomandations']

            selected_collection = self.connection["News"]
            for key in raccomandations:
                id_news = key
                weight = raccomandations[key]
                racc_news = {}
                news = selected_collection.find_one({"_id": int(id_news)})
                #import pdb
                #pdb.set_trace()
                racc_news["_id"] = id_news
                racc_news["weight"] = weight
                #print(str(news)+" id:"+id_news+" weight:"+str(weight))
                racc_news["category_title"] = news["category_title"]
                racc_news["news_source"] = news["news_source"]
                racc_news["url"] = news["url"]
                racc_news["article"] = news["article"]
                racc_news["title"] = news["title"]
                racc_list.append(racc_news)
        except Exception as e:
            print(str(e))
        return racc_list

    def get_news_reccomandations(self, user_id):
        selected_collection = self.connection["Raccomandations_Sport"]
        result = selected_collection.find_one({"_id": str(user_id)},{"raccomandations":1})
        selected_collection = self.connection["News"]
        racc_list = []
        raccomandations = result["raccomandations"]

        for key in raccomandations:
            id_news = key
            weight = raccomandations[key]
            racc_news = {}
            news = selected_collection.find_one({"_id": int(id_news)})
            racc_news["_id"] = id_news
            racc_news["weight"] = weight
            #print(str(news)+" id:"+id_news+" weight:"+str(weight))
            racc_news["category_title"] = news["category_title"]
            racc_news["news_source"] = news["news_source"]
            racc_news["url"] = news["url"]
            racc_news["article"] = news["article"]
            racc_news["title"] = news["title"]
            racc_list.append(racc_news)

        return racc_list
    # def get_news_reccomandations(self, user_id):
    #     selected_collection = self.connection["Users"]
    #     result = selected_collection.find_one({"_id": str(user_id)},{"raccomandations":1})
    #     selected_collection = self.connection["News"]
    #     racc_list = []
    #     for id_news, weight in result["raccomandations"].iteritems():
    #         racc_news = {}
    #         news = selected_collection.find_one({"_id": int(id_news)})
    #         racc_news["_id"] = id_news
    #         racc_news["weight"] = weight
    #         #print(str(news)+" id:"+id_news+" weight:"+str(weight))
    #         racc_news["category_title"] = news["category_title"]
    #         racc_news["news_source"] = news["news_source"]
    #         racc_news["url"] = news["url"]
    #         racc_news["article"] = news["article"]
    #         racc_news["title"] = news["title"]
    #         racc_list.append(racc_news)
    #
    #     return racc_list


    def get_news_for_learning(self, category, user_id):
        id_news_for_learning = []
        news_for_learning = []

        selected_collection = self.connection["ControllerCurrent"]
        result = selected_collection.find_one({}, {category: 1})

        id_current_jobs = result[category]
        if id_current_jobs != 0:
            pass

        selected_collection = self.connection["Indexes"]
        result = selected_collection.find_one({"_id": id_current_jobs}, {"id_to_idcorpus":1})

        news_in_current_model = result["id_to_idcorpus"]

        selected_collection = self.connection["NewsVotes"]
        for elem in news_in_current_model:
            id_news = news_in_current_model[elem]
            vote_register = selected_collection.find_one({"_id": id_news}, {"register":1})

            if vote_register is not None and str(user_id) in vote_register["register"]:
                continue
            else:
                id_news_for_learning.append(id_news)

        selected_collection = self.connection["News"]
        for elem in id_news_for_learning:
            result = selected_collection.find_one({"_id":elem}, {"article":1, "category_title":1, "title":1, "url":1, "_id":1})
            news_for_learning.append(result)

        return news_for_learning


    def get_history_racc(self, category, user_id):
        category = category.replace(" ", "")
        collection_name = "Raccomandations_"+category
        selected_collection = self.connection[collection_name]
        result = selected_collection.find_one({'_id': str(user_id)}, {'history_raccomandations':1})#['history_raccomandations']
        if result == None:
            return result
        selected_collection = self.connection["News"]
        racc_list = []
        if "history_raccomandations" not in result:
            return None
        raccomandations = result["history_raccomandations"]
        for key in raccomandations:
            id_news = key
            weight = raccomandations[key]
            racc_news = {}
            news = selected_collection.find_one({"_id": int(id_news)})
            racc_news["_id"] = id_news
            racc_news["weight"] = weight
            #print(str(news)+" id:"+id_news+" weight:"+str(weight))
            racc_news["category_title"] = news["category_title"]
            racc_news["news_source"] = news["news_source"]
            racc_news["url"] = news["url"]
            racc_news["article"] = news["article"]
            racc_news["title"] = news["title"]
            racc_list.append(racc_news)

        return racc_list
        #return result


    def get_voted_news(self, category, user_id):
        selected_collection = self.connection["News"]
        news_in_category = selected_collection.find({'category_title': category}, {'title':1, 'article':1})
        voted_news = []
        for news in news_in_category:
            news_id = news['_id']
            news_title = news['title']
            news_article = news['article']
            #print(str(news_id))
            selected_collection = self.connection["NewsVotes"]
            news_register = selected_collection.find({'_id':news_id},{'register.'+str(user_id):1})
            if news_register.count() != 0:
                register = news_register[0]['register']
                if register: # news votata
                    news_vote = register[str(user_id)]
                    elem = {
                            "_id": str(news_id),
                            "vote": news_vote,
                            "title": news_title,
                            "article": news_article
                            }
                    voted_news.append(elem)

        return voted_news


    # Funzione che recupera le news degli ultimi due giorni relative ad una categoria
    def get_last_news(self, category):
        selected_collection = self.connection["News"]
        last_news = selected_collection.find({"category_title":category}, {"_id":1, "article":1, "category_title":1, "title":1, "url":1, "date":1}).limit(300).sort('_id', -1)
        selected = []

        now = datetime.datetime.now()
        yesterday = now - datetime.timedelta(days=1)
        today_year = now.year
        today_month = now.month
        today_day = now.day
        yesterday_year = yesterday.year
        yesterday_month = yesterday.month
        yesterday_day = yesterday.day

        for t in last_news:
            date = t["date"]
            article = t["article"]
            if article is None:
                continue
            if (date[0]==today_year and date[1]==today_month and date[2]==today_day) or (date[0]==yesterday_year and date[1]==yesterday_month and date[2]==yesterday_day):
                selected.append(t)

        # se non ci sono notizie negli ultimi due giorni, prendo le notizie dell'ultimo giorno di attivita'
        if len(selected) == 0:
            last_news = selected_collection.find({"category_title":category}, {"_id":1, "article":1, "category_title":1, "title":1, "url":1, "date":1}).limit(300).sort('_id', -1)
            today_year = last_news[0]["date"][0]
            today_month = last_news[0]["date"][1]
            today_day = last_news[0]["date"][2]

            for t in last_news:
                date = t["date"]
                article = t["article"]
                if article is None:
                    continue
                if (date[0]==today_year and date[1]==today_month and date[2]==today_day):
                    selected.append(t)

        return selected
        #last_news = selected_collection.find_one({"date":elem}, {"article":1, "category_title":1, "title":1, "url":1, "_id":1})