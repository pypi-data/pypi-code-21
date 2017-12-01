from ..mongo import Mongo
from pymongo import ReturnDocument

class MongoTeacher(Mongo):
    def __init__(self,host, port, db):
        super(MongoTeacher,self).__init__(host, port, db)


    def insert_vote(self, collection, news_id, user_id, vote):
        #controllare se esiste un doc per la news
        selected_collection = self.connection[collection]
        result = selected_collection.find_one({"_id":news_id})
        tot = 1
        if result:
            #aggiorna il voto per l'utente
            #aggiungi +1 a tot
            tot = result["tot"] + 1
            updated = selected_collection.update_one({'_id':int(news_id)}, {"$set":{"tot":int(tot), "register." + str(user_id): int(vote)}}, upsert=False)
        else:
            #inserisci
            tmp = {
                "_id": int(news_id),
                "tot": tot,
                "register":{str(user_id):vote}
            }
            insert = selected_collection.insert_one(tmp)

        return tot

    def insert_stage(self, collection, category_name, news_id):
        selected_collection = self.connection[collection]
        result = selected_collection.find_one({})
        if result:
            if category_name in result:
                selected_collection.update_one({}, {"$addToSet":{category_name: int(news_id)}})
            else:
                selected_collection.update_one({}, {"$set": {category_name: [int(news_id)]}})
        else:
            tmp = {
                category_name: [int(news_id)]
            }
            selected_collection.insert_one(tmp)

    def create_increment_stage(self):
        categories = self.get_all_categories()
        selected_collection = self.connection["CheckModels"]
        result = selected_collection.find({})
        if result.count() == 0:
            data = {}
        else:
            data = result[0]

        for cat in categories:
            if cat["name"] not in data:
                name = cat["name"]
                selected_collection.update_one({},{"$set":{name:0}},upsert=True)

        # result = selected_collection.find_one({})
        # if result is None:
        #
        #     tmp = {
        #         "Arte e Cultura": 0,
        #         "Attualità": 0,
        #         "Benessere": 0,
        #         "Intrattenimento": 0,
        #         "Motori": 0,
        #         "Musica": 0,
        #         "Scienze": 0,
        #         "Spettacoli": 0,
        #         "Sport": 0,
        #         "Tecnologia": 0,
        #         "Viaggi": 0
        #     }
        #
        #     selected_collection.insert_one(tmp)
        # else:
        #     pass

    def increment_stage(self, category_name):
        selected_collection = self.connection["CheckModels"]
        #inc = selected_collection.update_one({}, {"$inc":{category_name: 1}})
        inc = selected_collection.find_one_and_update({},{"$inc": {category_name: 1}},return_document=ReturnDocument.AFTER)
        return inc[category_name]

    def set_increment_stage(self, category_name, value):
        selected_collection = self.connection["CheckModels"]
        selected_collection.update_one({}, {"$set": {category_name: int(value)}})

    def clear_increment_stage(self, category_name):
        selected_collection = self.connection["CheckModels"]
        selected_collection.update_one({}, {"$set": {category_name: 0}})

    def clear_all_increment_stage(self):
        selected_collection = self.connection["CheckModels"]
        selected_collection.drop()

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


    def set_bias_models(self, category_name, value):
        selected_collection = self.connection["BiasModels"]
        selected_collection.update_one({}, {"$set": {category_name: int(value)}})

    def create_bias_models(self):
        categories = self.get_all_categories()
        selected_collection = self.connection["BiasModels"]
        result = selected_collection.find({})
        if result.count() == 0:
            data = {}
        else:
            data = result[0]

        for cat in categories:
            if cat["name"] not in data:
                name = cat["name"]
                selected_collection.update_one({},{"$set":{name:1}},upsert=True)
        # result = selected_collection.find_one({})
        # if result is None:
        #
        #     tmp = {
        #         "Arte e Cultura": 3,
        #         "Attualità": 3,
        #         "Benessere": 3,
        #         "Intrattenimento": 3,
        #         "Motori": 3,
        #         "Musica": 3,
        #         "Scienze": 3,
        #         "Spettacoli": 3,
        #         "Sport": 3,
        #         "Tecnologia": 3,
        #         "Viaggi": 3
        #     }
        #
        #     selected_collection.insert_one(tmp)
        # else:
        #     pass

    def set_bias_stage(self, category_name, value):
        selected_collection = self.connection["BiasStage"]
        selected_collection.update_one({}, {"$set": {category_name: int(value)}})

    def create_bias_stage(self):
        categories = self.get_all_categories()
        selected_collection = self.connection["BiasStage"]

        result  = selected_collection.find({})
        if result.count() == 0:
            data = {}
        else:
            data = result[0]

        for cat in categories:
            if cat["name"] not in data:
                name = cat["name"]
                selected_collection.update_one({},{"$set":{name:10}},upsert=True)

        # result = selected_collection.find_one({})
        # if result is None:
        #
        #     tmp = {
        #         "Arte e Cultura": 10,
        #         "Attualità": 3,
        #         "Benessere": 3,
        #         "Intrattenimento": 3,
        #         "Motori": 3,
        #         "Musica": 3,
        #         "Scienze": 3,
        #         "Spettacoli": 3,
        #         "Sport": 3,
        #         "Tecnologia": 3,
        #         "Viaggi": 3
        #     }
        #
        #     selected_collection.insert_one(tmp)
        # else:
        #     pass


    def get_bias_models(self):
        selected_collection = self.connection["BiasModels"]
        result = selected_collection.find_one({})
        return result


    def get_bias_stage(self):
        selected_collection = self.connection["BiasStage"]
        result = selected_collection.find_one({})
        return result

    def create_consumer_teacher_modes(self):

        categories = self.get_all_categories()
        selected_collection = self.connection["ConsumerTeacherModes"]
        result = selected_collection.find({})
        if result.count() == 0:
            data = {}
        else:
            data = result[0]
        for cat in categories:
            if cat["name"] not in data:
                name = cat["name"]
                selected_collection.update_one({}, {"$set":{name:1}}, upsert=True)

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

    def get_consumer_teacher_modes(self,category_name):
        selected_collection = self.connection["ConsumerTeacherModes"]
        result = selected_collection.find_one({}, {category_name:1})
        category_name = category_name.decode('utf-8')
        return result[category_name]

    def set_consumer_teacher_modes(self, category_name, mode):
        selected_collection = self.connection["ConsumerTeacherModes"]
        if mode == 1 or mode == 0:
            result = selected_collection.update_one({}, {"$set": {category_name: mode}})

    def get_all_categories(self):
        selected_collection = self.connection['CategoriesTeacher']
        return selected_collection.find()

    def insert_category(self, id, name, enabled,status=None):
        selected_collection = self.connection['CategoriesTeacher']
        selected_collection.update_one({"_id":int(id)}, {"$set": {"name":name, "enabled": int(enabled), "status":0}},upsert=True)

    def update_category(self, id, name, enabled, status=None):
        selected_collection = self.connection['CategoriesTeacher']
        selected_collection.update_one({"_id":int(id)}, {"$set": {"name":name, "enabled": int(enabled), "status":1}},upsert=True)

    def get_new_categories(self):
        selected_collection = self.connection['CategoriesTeacher']
        return selected_collection.find({"status":0})
