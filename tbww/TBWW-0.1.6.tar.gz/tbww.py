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
        self.permissions = None # This should be an immutableDict. It can still be overwritten but it should be fairly safe.
        self.default_perms = defaukt_perms

    def start_webhook(self,host):
        """Host should be heroku app domain if on heroku"""
        self.updater.start_webhook(listen=self.IP,
                                   port=self.PORT,
                                   url_path=self.TOKEN)
        self.updater.bot.set_webhook(host+self.TOKEN)
        self.updater.idle()

    def command(self,name,pass_args=False,permissions=None):
        def decorator(function):
            def wrapper(*args,**kwargs):
                if permissions != None:
                    if permissions < self.permissions[args[1].message.from_user.id]:
                        args[0].send_message(chat_id=args[1].message.chat_id,
                                             text="You do not have permission to use this command!")
                        return None
                    else:
                        return function()
                return function()
            
            self.dispatcher.add_handler(CommandHandler(name,wrapper,pass_args=pass_args))
            
            return wrapper()
        return decorator

    def set_permissions(self,D):
        """Set an immutableDict of permissions"""
        self.permissions = immutableDict(D)
