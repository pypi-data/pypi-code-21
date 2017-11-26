##TBWW, based on python-telegram-bot

import os
from telegram.ext import Updater, CommandHandler

class immutableDict(dict):
    def __delattr__(self,*args,**kwargs):
        return None
    def __delitem__(self,*args,**kwargs):
        return None
    def __setattr__(self,*args,**kwargs):
        return None
    def __setitem__(self,*args,**kwargs):
        return None
    def update(self,*args,**kwargs):
        return None
    def pop(self,*args,**kwargs):
        return None
    def popitem(self,*args,**kwargs):
        return None
    def clear(self,*args,**kwargs):
        return None

class Bot(object):
    def __init__(self,TOKEN,IP="0.0.0.0",PORT=None,default_perms=float("inf")):
        """Leave PORT as None to autodetect for Heroku"""
        #set up basics and webserver config
        self.TOKEN = TOKEN
        self.IP = IP
        if PORT == None:
            PORT = int(os.environ.get("PORT","5000"))
        self.PORT = PORT

        #Most important bit!
        self.updater = Updater(token=TOKEN)
        self.dispatcher = self.updater.dispatcher # Shortcut

        #Set up permissions
        self.permissions = {}
        self.default_perms = default_perms

    def start_webhook(self,host):
        """Host should be heroku app domain if on heroku"""
        self.updater.start_webhook(listen=self.IP,
                                   port=self.PORT,
                                   url_path=self.TOKEN)
        self.updater.bot.set_webhook(host+self.TOKEN)
        self.updater.idle()

    def get_remote_permissions(self): # Define this yourself with inheritence
        return {}

    def get_user_perms(self,user):
        if self.permissions.has_key(user):
            return self.permissions[user]
        remote = self.get_remote_permissions()
        if remote.has_key(user):
            return remote[user]
        return self.default_perms

    def command(self,name,pass_args=False,permissions=None):
        def decorator(function):
            def top(function):
                def wrapper(*args,**kwargs):
                    if permissions != None:
                        if (self.permissions.has_key(args[1].message.from_user.id) and permissions >= self.permissions[args[1].message.from_user.id]):
                            function(*args,**kwargs)
                            return None
                        remote_perms = self.get_remote_permissions()
                        if (remote_perms.has_key(args[1].message.from_user.id) and permissions >= remote_perms[args[1].message.from_user.id]):
                            function(*args,**kwargs)
                            return None
                        if permissions >= self.default_perms:
                            function(*args,**kwargs)
                            return None
                        args[0].send_message(chat_id=args[1].message.chat_id,
                                                 text="You do not have permission to use this command!")
                        return None
                    else:
                        function(*args,**kwargs)
                
                return wrapper
            self.dispatcher.add_handler(CommandHandler(name,top(function),pass_args=pass_args))
        return decorator

