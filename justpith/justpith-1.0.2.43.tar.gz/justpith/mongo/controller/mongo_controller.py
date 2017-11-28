# encoding: utf-8
from ..mongo import Mongo

class MongoController(Mongo):
    def __init__(self,host, port, db):
        super(MongoController,self).__init__(host, port, db)
        self.collection_job = "ControllerJobs"
        self.connection_mode = "ControllerModes"
        self.connection_current = "ControllerCurrent"
        self.connection_next = "ControllerNext"

    def insert_job(self,job):
        selected_collection = self.connection[self.collection_job]
        selected_collection.insert_one(job)

    def insert_model_into_job(self, job_id, model_id, type):
        selected_collection = self.connection[self.collection_job]
        if type == "text":
            result = selected_collection.update_one({"_id":job_id},{"$set":{"id_text": str(model_id)}})
        elif type == "matrix":
            result = selected_collection.update_one({"_id":job_id}, {"$set": {"id_matrix": str(model_id)}})

    def get_job(self, job_id):
        selected_collection = self.connection[self.collection_job]
        result = selected_collection.find_one({"_id": job_id} )
        return result

    def get_job_from_id_text(self, id_text):
        selected_collection = self.connection[self.collection_job]
        result = selected_collection.find_one({"id_text": id_text})
        return result

    def deactive_job(self, job_id):
        selected_collection = self.connection[self.collection_job]

        result_find = selected_collection.find({"_id": job_id})
        if result_find:
            category = result_find[0]["analyzer"]["category"]
        else:
            return -1

        if category:
            result = selected_collection.update_many({"analyzer.category": category}, {"$set": {"active": 0}})
            return 1
        else:
            return -1

    def active_job(self, job_id):
        selected_collection = self.connection[self.collection_job]
        result = selected_collection.update_one({"_id": job_id}, {"$set": {"active": 1}})

    def get_active_job(self):
        selected_colection = self.connection[self.collection_job]
        result = selected_colection.find({"active":1})
        return result

    def get_active_job_by_category(self,category):

        selected_collection = self.connection[self.collection_job]
        result = selected_collection.find({"active":1, "analyzer.category":category})
        if result.count() > 0:
            return result.sort([("timestamp",-1)])[0]
        else:
            return None


    def create_modes(self):

        categories = self.get_all_categories()

        selected_collection = self.connection[self.connection_mode]
        result = selected_collection.find({})
        if result.count() == 0:
            data = {}
        else:
            data = result[0]
        for cat in categories:
            if cat["name"] not in data:
                name = cat["name"]
                selected_collection.update_one({}, {"$set": {name: 1}}, upsert=True)

        # result = selected_collection.find_one({})
        # if result is None:
        #
        #     tmp = {
        #         "Arte e Cultura": 1,
        #         "Attualità": 1,
        #         "Benessere": 1,
        #         "Intrattenimento": 1,
        #         "Motori": 1,
        #         "Musica": 1,
        #         "Scienze": 1,
        #         "Spettacoli": 1,
        #         "Sport": 1,
        #         "Tecnologia": 1,
        #         "Viaggi": 1
        #     }
        #
        #     selected_collection.insert_one(tmp)
        # else:
        #     pass

    def change_mode(self,type,mode):
        selected_collection = self.connection[self.connection_mode]
        selected_collection.update_one({}, {"$set": {type: mode} })

    def get_mode(self, type):
        selected_collection = self.connection[self.connection_mode]
        result = selected_collection.find_one({})
        return result[type]

    def create_current(self):
        selected_collection = self.connection[self.connection_current]
        result = selected_collection.find_one({})
        if result is None:

            tmp = {
                "Arte e Cultura": 0,
                "Attualità": 0,
                "Benessere": 0,
                "Intrattenimento": 0,
                "Motori": 0,
                "Musica": 0,
                "Scienze": 0,
                "Spettacoli": 0,
                "Sport": 0,
                "Tecnologia": 0,
                "Viaggi": 0
            }

            selected_collection.insert_one(tmp)
        else:
            pass


    def change_current(self,type,id):
        selected_collection = self.connection[self.connection_current]
        selected_collection.update_one({}, {"$set": {type: id}})

    def get_current(self, type):
        selected_collection = self.connection[self.connection_current]
        result = selected_collection.find_one({})
        return result[type]

    def create_next(self):
        selected_collection = self.connection[self.connection_next]
        result = selected_collection.find_one({})
        if result is None:

            tmp = {
                "Arte e Cultura": 0,
                "Attualità": 0,
                "Benessere": 0,
                "Intrattenimento": 0,
                "Motori": 0,
                "Musica": 0,
                "Scienze": 0,
                "Spettacoli": 0,
                "Sport": 0,
                "Tecnologia": 0,
                "Viaggi": 0
            }

            selected_collection.insert_one(tmp)
        else:
            pass


    def change_next(self,type,id):
        selected_collection = self.connection[self.connection_next]
        selected_collection.update_one({}, {"$set": {type: id}})

    def get_next(self, type):
        selected_collection = self.connection[self.connection_next]
        result = selected_collection.find_one({})
        return result[type]


    ####################    RACCOMANDATIONS ####################################
    def get_mf_users_raccomandations(self, job_id):
        selected_collection = self.connection['Users']
        #result = selected_collection.find({},{'mf_raccomandations.{}'.format(str(job_id)):1})
        result = selected_collection.find({"mf_raccomandations.{}".format(str(job_id)):{"$exists": True}}, {'mf_raccomandations.{}'.format(str(job_id)):1})
        #result = selected_collection.find({})
        return result

    def update_users_raccomandations(self, news_id, users_to_raccomand):
        selected_collection = self.connection['Users']
        for elem in users_to_raccomand:
            id_user = elem[0]
            weight_racc = elem[1]
            selected_collection.update({'_id': str(id_user)}, {'$set': {'raccomandations.{}'.format(str(news_id)): weight_racc}}, upsert=True)

    def is_voted_news(self, news_id, user_id):
        selected_collection = self.connection['NewsVotes']
        result = selected_collection.find({'_id':int(news_id), 'register.'+str(user_id):{'$exists': True}}).count()
        if result == 0: # News non votata dall'utente
            return False
        else: # News votata dall'utente
            return True

    def get_user_raccomandations(self, user_id, category):
        category = category.replace(" ", "")
        collection_name = "Raccomandations_"+category
        selected_collection = self.connection[collection_name]
        result = selected_collection.find_one({'_id': str(user_id)}, {'raccomandations':1})['raccomandations']
        return result

    def get_all_user_raccomandations(self, category):
        category = category.replace(" ", "")
        collection_name = "Raccomandations_"+category
        selected_collection = self.connection[collection_name]
        result = selected_collection.find({}, {'_id':1,'raccomandations':1})
        return result

    def update_user_raccomandation(self, user_id, new_raccomandations, category):
        category = category.replace(" ", "")
        collection_name = "Raccomandations_"+category
        selected_collection = self.connection[collection_name]
        result = selected_collection.update({'_id': str(user_id)}, {'$set': {'raccomandations': new_raccomandations}}, upsert=True)

    def update_user_history_raccomandations(self, user_id, history_news, history_weight, category):
        category = category.replace(" ", "")
        collection_name = "Raccomandations_"+category
        selected_collection = self.connection[collection_name]
        result = selected_collection.update({'_id': str(user_id)}, {'$set': {'history_raccomandations.'+str(history_news): history_weight}}, upsert=True)

    def get_all_categories(self):
        selected_collection = self.connection['CategoriesController']
        return selected_collection.find()

    def insert_category(self, id, name, enabled,status=None):
        selected_collection = self.connection['CategoriesController']
        selected_collection.update_one({"_id":int(id)}, {"$set": {"name":name, "enabled": int(enabled), "status":0}},upsert=True)

    def update_category(self, id, name, enabled, status=None):
        selected_collection = self.connection['CategoriesController']
        selected_collection.update_one({"_id":int(id)}, {"$set": {"name":name, "enabled": int(enabled), "status":1}},upsert=True)

    def get_new_categories(self):
        selected_collection = self.connection['CategoriesController']
        return selected_collection.find({"status":0})