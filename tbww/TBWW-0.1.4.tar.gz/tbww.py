##TBWW, based on python-telegram-bot

import os
from telegram.ext import Updater, CommandHandler

class Bot(object):
    def __init__(self,TOKEN,IP="0.0.0.0",PORT=None):
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

    def start_webhook(self,host):
        """Host should be heroku app domain if on heroku"""
        self.updater.start_webhook(listen=self.IP,
                                   port=self.PORT,
                                   url_path=self.TOKEN)
        self.updater.bot.set_webhook(host+self.TOKEN)
        self.updater.idle()

    def command(self,name):
        def decorator(function):
            def wrapper():
                return function
            self.dispatcher.add_handler(CommandHandler(name,function))
            
            return wrapper()
        return decorator
