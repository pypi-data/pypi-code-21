import os
from django.core.management import execute_from_command_line
import sys
from django.conf import settings as django_settings


class Session(object):
    def __init__(self, model, settings="default_settings"):
        self.settings = settings
        pre = sys.stdout.write
        sys.stdout.write = lambda *args: None
        self.call(settings=self.settings)
        sys.stdout.write = pre
        self.__db = __import__(django_settings.INSTALLED_APPS[0])
        self.__getmodel(model)
        #print(getattr(self.db.models,'mymodel'))
        #print(self.db.models)

    def __getmodel(self, model):
        try:
            self.__model = getattr(self.__db.models,model)
        except Exception as e:
            raise Exception("please build your model , and try makemigration and migrate")

    def makemigration(self):
        self.call(arg="makemigrations",settings=self.settings)

    def create(self,info):
        self.__model.objects.create(**info)
        print("Create Successful ,", "info is ", info)

    def deletes(self,info):
        query_set = self.query(info)
        for s in query_set:
            print(s," will be delete ")
            s.delete()

    def delete(self,info):
        s = self.get(info)
        print(s," will be delete ")
        s.delete()

    def query(self,info):
        return self.__model.objects.filter(**info)

    def update(self,info,attr):
        s = self.get(info)
        for key in attr.keys():
            setattr(s, key, attr[key])
        s.save()
        print(s," change infomation successful ")

    def migrate(self):
        self.call(arg="migrate", settings=self.settings)

    def all(self):
        return self.__model.objects.all()

    def get(self,info):
        return self.__model.objects.get(**info)

    def count(self):
        return self.__model.objects.count()

    def get_model(self):
        return self.__model

    def sql(self,sql_command):
        return self.__model.objects.raw(sql_command)

    @staticmethod
    def call(arg=None,settings="default_settings"):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)
        args = ['manage.py',]
        if arg:
            args.append(arg)
        execute_from_command_line(args)

