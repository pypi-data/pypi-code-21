import os
import sys as sys
os.system("python bot/bot.py engage")
import bot_response as bot
import bot_learn as learner
import logger as log
import urllib
import writer as w
import reader as r
import urllib
from importlib import reload
from urllib.request import urlopen
#Allow the user to communicate with the bot
#Also allow the bot to learn about the person

def replace(file_path, pattern, subst):
        read = open(file_path, 'r')
        write = open(file_path, 'w')
        lines = read.read()
        print(read.read().replace(pattern, subst))

def toBot():
        reload(bot)
        reload(learner)
        if(os.path.isfile(".bot_engage")):
                print("You can only run one instance of Clarissa.")
        else:
                swearNum = 1
                setup_ext = open(".setup_ext",'r')
                for line in setup_ext.readlines():
                        if "install=" in line:
                                os.environ['CLARISSA_PATH'] = line.replace("install=", "")
                os.environ['USER_NAME'] = r.getClarissaSetting("user.name").replace("\n","")
                messageToBot = input(os.environ['USER_NAME'].replace("\n","")+": ")
                if(messageToBot == "--add-command"):
                        writeCommand(command=input("Command: "), response=input("Responses: "))
                        reload(bot)
                elif(messageToBot == "kill-bot"):
                        bot.getResponse("kill-bot")
                        exit()
                elif(messageToBot == "--clear-commands"):
                	#os.remove("commands.bot")
                	#os.remove("responses.bot")]
                        print("Cleared commands")
                        exit()
                elif(messageToBot == "learn"):
                        learner.learn(db_support=False)
                elif(messageToBot == "--get-commands"):
                        commandsList = open("commands.list","r")
                        print(commandsList.read())
                elif(messageToBot == "--get-logs"):
                        logs = open('chat.log', 'r')
                        print(logs.read())
                elif(messageToBot == "--update-clarissa"):
                        urllib.urlopen("https://softy.xyz/apps/sites/clarissa/get.php")
                        response = urllib.request.urlopen("https://softy.xyz/apps/sites/clarissa/clarissa.json")
                        import json
                        file = json.loads(response.read())
                        print(file['command'])
                elif("Call me " in messageToBot):
                        w.setClarissaSetting("user.name", messageToBot.replace("Call me ", ""))
                elif("call me " in messageToBot):
                        w.setClarissaSetting("user.name", messageToBot.replace("call me ", ""))
                log.log("chat.log", messageToBot)
                if(r.getClarissaSetting("ro.Clarissa.FROM_SERVER") is "true"):
                        print("Get the response from a server")
                else:
                        bot.getResponse(messageToBot)
                toBot()


def writeCommand(command, response):
        log.log("chat.log", "Clarissa: "+response)
        file = open("bot_response.py", "a")
        file.write("\n\telif(\""+command+"\" in messageToBot):")
        file.write("\n\t\tprint(\"Clarissa: "+response+"\")")
        file.flush()
        file.close()

        commandList = open("commands.list", "w")
        commandList.write(command)
        commandList.flush()
        commandList.close()
        if "Y" in input("Do you wish to upload commands to our server? (Y/N) ") or ("bremo" in os.environ['USERPROFILE'].short()):
                import requests as r
                url = 'https://softy.000webhostapp.com/apps/sites/clarissa/update.php'
                query = {'c': command,
                        'r': response}
                res = r.post(url, data=query)
                print(res.text)

def getIf(message, command, response):
	if(message == command):
		print("Clarissa: "+response)
	else:
		print("I do not understand "+message)

def getCommands():
	return open("commands.bot", "r").read()

def getResponses():
	return open("responses.bot", "r").read()


swearNum = 0

try:
        if("--add-command" in sys.argv):
                writeCommand(command=sys.argv[2], response=sys.argv[3])
                reload(bot)
        elif ("--clear-commands" in sys.argv):
                #os.remove("commands.bot")
                #os.remove("responses.bot")
                os.remove("bot_response.py")
                writeCommand("Hello", "Hi")
                print("Cleared commands")
        elif ("learn" in sys.argv):
                learner.learn(db_support=False)
        elif ("--get-commands" in sys.argv):
                commandsList = open("commands.list","r")
                print(commandsList.read())
        elif ("--update-clarissa" in sys.argv):
                os.system("python update.py")
        elif ("--get-logs" in sys.argv):
                logs = open('chat.log','r')
                print(logs.read())
        elif ( sys.argv[1] == "set.name"):
                w.setClarissaSetting("user.name", sys.argv[2])
        elif ( sys.argv[1] == "--get-setting"):
                print(getClarissaSetting(sys.argv[2]))
        elif ( sys.argv[1] == "--update-from-url" ):
                os.system("python update.py --from-url "+sys.argv[2])
        elif ( "--enable-auto-update" in sys.argv):
                w.setClarissaSettingWithPath("Settings/update.settings","Clarissa.AUTO_UPDATE", "true")
        elif ("--update-bot" in sys.argv):
                os.system("python update.py")
        elif("--help" in sys.argv or "--h" in sys.argv):
                print("Commands:")
                print("\t--add-command : Adds command to Clarissa")
                print("\t--clear-commands : Clears all added custom commands")
                print("\t--get-commands : Prints a list of Clarissa commands")
                print("\t--update-clarissa : Adds messages")
                print("\t--get-logs : Gets all the chat logs")
                print("\tset.name : Gives you a custom username")
                print("\t--get-setting: Gets settings stored")
                print("\t--enable-auto-update : Turns on auto update feature for commands")
                print("\t--update-bot : Updates the list of existing commands (Will be used to update the bot later on)")
                print("\t--update-from-url: Get a custom messages update from your own site")
                print("\t--h / --help : Prints this list")
        else:
                toBot()

except IndexError:
        if(r.getClarissaSettingWithPath("Settings/update.settings","Clarissa.AUTO_UPDATE") is "true"):
                os.system("java -jar libs/Updater.jar --write-to bot_response.py")
        toBot()