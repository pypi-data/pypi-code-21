import time
import logging
import logging.handlers

import pickle

from Queue import Queue
from threading import Thread
from threading import Event
from threading import RLock

import StringIO

import telegram
from telegram import TelegramError

# import pprint


class BotChat(object):
    def __init__(self, server, cid):
        self._lock=RLock()
        self._server=server
        self._cid=cid
        # self._slots={'broadcast': True, 'debug': True}
        self._slots={}
        self._users={}
        self._data={}
        self._commands={}
        self._stampUnlockTimeout=0

    @property
    def server(self):
        return self._server

    @property
    def cid(self):
        return self._cid

    @property
    def logger(self):
        return self.server.logger

    def save(self):
        with self._lock:
            return {'version': 2, 'cid': self.cid, 'slots': self._slots, 'data': self._data, 'users': self._users, 'commands': self._commands}

    def restore(self, data):
        try:
            with self._lock:
                if data and data['cid']==self.cid:
                    version=data['version']
                    if version>=1:
                        self.logger.debug('restoring chat %d', self.cid)
                        self._slots=data['slots']
                        self._data=data['data']
                        self._users=data['users']
                    if version>=2:
                        self._commands=data['commands']

        except:
            pass

    def getData(self, name, defaultValue=None):
        try:
            with self._lock:
                return self._data[name]
        except:
            return defaultValue

    def setData(self, name, value):
        try:
            with self._lock:
                old=self.getData(name)
                self._data[name]=value
                return old
        except:
            pass

    def protect(self, state=True):
        self.setData('protected', bool(state))

    def isProtected(self):
        if self.getData('protected', False):
            return True

    def unlock(self, delay=60):
        with self._lock:
            if delay>0:
                self._stampUnlockTimeout=time.time()+delay

    def lock(self):
        with self._lock:
            self._stampUnlockTimeout=0

    def isUnlocked(self):
        with self._lock:
            return self._stampUnlockTimeout>time.time()

    def slot(self, name):
        try:
            return self._slots[name.lower()]
        except:
            pass

    def isConnected(self, slot):
        try:
            with self._lock:
                if self.slot(slot) is not None:
                    return True
        except:
            pass

    def connect(self, slot):
        try:
            with self._lock:
                if slot and not self.isConnected(slot):
                    self.logger.info('ChatSlot(%d)->connect(%s)' % (self.cid, slot))
                    self._slots[slot.lower()]=True
                    self.server.sendTextToChatSlot('admin', '%d->connect(%s)' % (self.cid, slot))
                    return slot
        except:
            self.logger.exception('connect()')

    def disconnect(self, slot):
        try:
            with self._lock:
                if self.isConnected(slot):
                    del self._slots[slot]
                    self.logger.info('ChatSlot(%d)->disconnect(%s)' % (self.cid, slot))
                    return slot
        except:
            self.logger.exception('disconnect()')

    def slots(self):
        try:
            with self._lock:
                return self._slots.keys()
        except:
            pass

    def sendText(self, text, markup=None):
        self.server.sendText(self._cid, text, markup)

    def sendImage(self, image, caption=None, markup=None, format="png"):
        self.server.sendImage(self._cid, image, caption, markup, format)

    def user(self, uid):
        try:
            with self._lock:
                return self._users[uid]
        except:
            pass

    def users(self):
        try:
            with self._lock:
                return self._users.values()
        except:
            pass

    def registerUser(self, uid, uname, fname=None, lname=None):
        with self._lock:
            user=self.user(uid)
            if not user:
                self.logger.debug('register user %d with chat %d' % (uid, self.cid))
                user={'id': uid}
                self._users[uid]=user
            user['uname']=uname
            user['fname']=fname
            user['lname']=lname
            return user

    def unregisterUser(self, uid):
        try:
            with self._lock:
                if self.user(uid):
                    self.logger.debug('unregister user %d from chat %d' % (uid, self.cid))
                    del self._users[uid]
        except:
            pass

    def registerUserCommand(self, name, cargs):
        if name:
            name=name.lower()
            if name[0]=='/':
                name=name[1:]
            try:
                if cargs:
                    self._commands[name]=cargs
                    self.logger.debug('registering user command [%s]' % name)
                else:
                    del self._commands[name]
            except:
                pass

    def getUserCommand(self, name):
        try:
            return self._commands[name.lower()]
        except:
            pass

    def userCommands(self):
        return self._commands


class BotServer(object):
    def __init__(self, token, fpathConfig, logServer='localhost', logLevel=logging.DEBUG):
        logger=logging.getLogger("TBOTSERVER")
        logger.setLevel(logLevel)
        socketHandler = logging.handlers.SocketHandler(logServer,
            logging.handlers.DEFAULT_TCP_LOGGING_PORT)
        logger.addHandler(socketHandler)
        self._logger=logger

        self._lock=RLock()
        self._eventStop=Event()
        self._eventPrune=Event()
        self._token=token
        self._bot=None
        self._botuser=None
        self._botid=0
        self._botOffset=0
        self._botPendingOffsetAck=False
        self._botQueueInput=Queue()
        self._chats={}
        self._fpathConfig=fpathConfig

        self.restore()
        self.onInit()

    @property
    def logger(self):
        return self._logger

    @property
    def token(self):
        return self._token

    def onInit(self):
        pass

    def onStart(self):
        pass

    def onStop(self):
        pass

    def onPrune(self):
        pass

    def save(self):
        try:
            if self._fpathConfig:
                data={'version': 1, 'chats': []}
                chats=self.chats()
                if chats:
                    for chat in chats:
                        data['chats'].append(chat.save())

                with open(self._fpathConfig, 'wb') as f:
                    pickle.dump(data, f)
        except:
            self.logger.exception('save()')

    def restore(self):
        try:
            with open(self._fpathConfig, 'rb') as f:
                data=pickle.load(f)

            if data and data['version']==1:
                for c in data['chats']:
                    chat=BotChat(self, c['cid'])
                    chat.restore(c)
                    self._chats[chat.cid]=chat
        except:
            self.logger.exception('restore()')

    def start(self):
        with self._lock:
            if self._bot:
                return self._bot

            self._bot=None
            try:
                if self._token:
                    self.logger.info('start(%s)' % self._token)
                    bot=telegram.Bot(token=self._token)
                    if bot:
                        r=bot.getMe()
                        self._botuser=r['username']
                        self._botid=r['id']
                        self._bot=bot
                        self._botOffset=0
                        self._botPendingOffsetAck=False
                        self._eventStop.clear()
                        self._threadPoll=Thread(target=self._threadPollManager)
                        self._threadPoll.start()
                        self.logger.info('bot @%s/%d started' % (self._botuser, self._botid))
                        self.onStart()
                        return self._bot
            except:
                self.logger.exception('start()')

    def isRunning(self):
        return not self._eventStop.isSet()

    def stop(self):
        if self.isRunning():
            self.logger.debug('stop()')
            self._eventStop.set()
            with self._lock:
                self.save()
                if self._bot:
                    try:
                        self.logger.debug('waiting for poll thread...')
                        self._threadPoll.join()
                    except:
                        pass
                    self._threadPoll=None
                    self.onStop()
                    self.logger.info('bot @%s halted' % self._botuser)
                    self._bot=None

    def sleep(self, delay):
        return self._eventStop.wait(delay)

    def prune(self):
        if not self._eventPrune.isSet():
            self.logger.warning('telegram event queue prune request!')
            self._eventPrune.set()
            try:
                self.onPrune()
            except:
                self.logger.exception('onPrune')

    def _threadPollManager(self):
        self.logger.info('poll thread started.')
        while not self._eventStop.isSet():
            try:
                if self.start():
                    if not self._botQueueInput.empty():
                        self.sleep(1.0)
                        continue

                    pid=self._botOffset+1
                    self.logger.debug('poll(%d)' % pid)
                    r=self._bot.getUpdates(pid, 128, 5.0)
                    self._botPendingOffsetAck=False
                    for update in r:
                        if self._eventPrune.isSet():
                            self.logger.warning('pruning telegram update  %s' % update)
                        else:
                            self._botQueueInput.put(update)

                    self._eventPrune.clear()
                self.sleep(0.5)
            except:
                self.logger.exception('poll()')
                self.sleep(10.0)

            self.sleep(2.0)

        if self._botPendingOffsetAck:
            try:
                self.logger.debug('ack pending offset %s' % self._botOffset)
                self._bot.getUpdates(self._botOffset+1, 1, 0)
            except:
                pass

        self.logger.info('poll thread halted.')

    def getNextPendingMessage(self):
        try:
            update=self._botQueueInput.get(False)
            if update:
                self.logger.debug('processing pending update #%d' % update.update_id)
                self._botOffset=update.update_id
                self._botPendingOffsetAck=True
                return update.message
        except:
            pass

    def removeAllPendingMessages(self):
        while self.getNextPendingMessage():
            pass

    def getChatFromId(self, cid):
        try:
            return self._chats[int(cid)]
        except:
            pass

    def getChatFromMessage(self, message):
        try:
            return self.getChatFromId(message.chat.id)
        except:
            pass

    def registerChat(self, message):
        try:
            cid=message.chat.id
            chat=self.getChatFromMessage(message)
            if not chat:
                self.logger.info('creating chat %d' % cid)
                chat=BotChat(self, cid)
                self._chats[chat.cid]=chat

            try:
                user=message.from_user
                chat.registerUser(user.id, user.username, user.first_name, user.last_name)
            except:
                pass

            if message.left_chat_member:
                chat.unregisterUser(message.left_chat_member.id)

            return chat
        except:
            self.logger.exception('registerMessageSource()')

    def unregisterChat(self, cid):
        try:
            chat=self.getChatFromId(cid)
            if chat:
                self.logger.warning('removing chat %d' % cid)
                del self._chats[cid]
        except:
            self.logger.exception('unregisterChat()')

    def chats(self):
        try:
            return self._chats.values()
        except:
            pass

    def getChatsConnectedToSlot(self, slot):
        chats=[]
        try:
            for chat in self.chats():
                if chat.isConnected(slot):
                    chats.append(chat)
        except:
            self.logger.exception('getChatsConnectedToSlot()')
        return chats

    def sendText(self, chatid, text, markup=None):
        try:
            if text:
                try:
                    text=text.encode('utf8')
                except:
                    pass
                self._bot.sendMessage(chat_id=chatid, text=text, reply_markup=markup)
        except TelegramError, e:
            self.logger.exception('sendText(%d)' % chatid)
            if str(e).find('403: Forbidden')>=0:
                self.unregisterChat(chatid)
        except:
            self.logger.exception('sendText(%d)' % chatid)

    def sendImage(self, chatid, image, caption=None, markup=None, format="png"):
        try:
            if image:
                buf = StringIO.StringIO()
                image.save(buf, format)
                buf.seek(0)

                try:
                    if caption:
                        caption=caption.encode('utf8')
                except:
                    self.logger.exception('utf8')

                self._bot.sendChatAction(chat_id=chatid, action=telegram.ChatAction.TYPING)
                self._bot.sendPhoto(chat_id=chatid, photo=buf, caption=caption, reply_markup=markup)
                buf.close()

        except TelegramError, e:
            self.logger.exception('sendImage(%d)' % chatid)
            if str(e).find('403: Forbidden')>=0:
                self.unregisterChat(chatid)
        except:
            self.logger.exception('sendText(%d)' % chatid)

    def sendTextToChatSlot(self, slot, text, markup=None):
        try:
            chats=self.getChatsConnectedToSlot(slot)
            for chat in chats:
                chat.sendText(text, markup)
        except:
            self.logger.exception('sendTextToChatSlot()')

    def sendImageToChatSlot(self, slot, image, caption=None, markup=None, format="png"):
        try:
            chats=self.getChatsConnectedToSlot(slot)
            for chat in chats:
                chat.sendImage(image, caption, markup, format)
        except:
            self.logger.exception('sendImageToChatSlot()')

    def storeDataToChatSlots(self, slot, dname, dvalue):
        try:
            chats=self.getChatsConnectedToSlot(slot)
            for chat in chats:
                chat.setData(dname, dvalue)
        except:
            self.logger.exception('storeDataToChatSlot()')

    def notifyProcessing(self, message):
        try:
            self._bot.sendChatAction(chat_id=message.chat_id, action=telegram.ChatAction.TYPING)
        except:
            self.logger.exception('notifyProcessing()')

    def replyText(self, message, text, markup=None):
        try:
            self.sendText(message.chat_id, text, markup)
        except:
            self.logger.exception('replyText()')

    def replyImage(self, message, image, caption=None, markup=None, format="png"):
        try:
            self.sendImage(message.chat_id, image, caption, markup, format)
        except:
            self.logger.exception('replyImage()')

    def forceReplyText(self, message, text, selective=False):
        markup=telegram.ForceReply(selective=selective)
        return self.replyText(message, text, markup)

    def replyHelp(self, message):
        # self.replyText(message, "Command not implemented!")
        pass

    def onMessageText(self, message):
        pass

    def onMessage(self, message):
        pass

    def onCommand_start(self, message, params):
        pass

    def onCommand_commands(self, message, params):
        chat=self.getChatFromMessage(message)
        if chat:
            commands=chat.userCommands()
            if commands:
                for c in commands.keys():
                    self.replyText(message, '/%s %s' % (c, ' '.join(commands[c])))

    def onCommand_command(self, message, params):
        try:
            name=params[0].lower()
            cargs=params[1:]
            chat=self.getChatFromMessage(message)
            if name and chat:
                chat.registerUserCommand(name, cargs)
        except:
            self.logger.exception('command')

    def dispatchCommand(self, message):
        try:
            cargs=message.text.split(' ')
            command=cargs[0][1:].lower()
            params=cargs[1:]
            if command=='set':
                return self.dispatchSetValue(message)

            self.logger.debug('@%s:command(%s)' % (message.from_user.username, command))
            handler='onCommand_'+command
            try:
                # check builtin command
                try:
                    h=getattr(self, handler)
                    if callable(h):
                        try:
                            return h(message, params)
                        except:
                            self.logger.exception('%s()' % handler)
                except:
                    pass

                # check user defined chat command
                chat=self.getChatFromMessage(message)
                if chat:
                    try:
                        cargs=chat.getUserCommand(command)
                        command=cargs[0]
                        if command[0]=='/':
                            command=command[1:]
                        paramsCommand=cargs[1:]

                        # append user params to the registered command
                        paramsCommand.extend(params)

                        if command:
                            handler='onCommand_'+command
                            h=getattr(self, handler)
                            if callable(h):
                                try:
                                    return h(message, paramsCommand)
                                except:
                                    self.logger.exception('%s()' % handler)
                    except:
                        pass
            except:
                pass

            self.logger.warning('unhandled command %s' % str(message))
            self.replyHelp(message)
        except:
            self.logger.exception('dispatchCommand()')

    def dispatchSetValue(self, message):
        try:
            cargs=message.text.split(' ')
            name=cargs[1].lower()
            params=cargs[2:]
            if name and params:
                value=' '.join(params)
                self.logger.debug('@%s:setValue(%s:%s)' % (message.from_user.username, name, value))
                handler='onSetValue_'+name
                try:
                    h=getattr(self, handler)
                    if callable(h):
                        try:
                            return h(message, value)
                        except:
                            self.logger.exception('%s()' % handler)
                except:
                    pass

                self.logger.warning('unhandled setValue() %s' % str(message))
                self.replyHelp(message)
        except:
            self.logger.exception('dispatchSetValue()')

    def dispatchText(self, message):
        try:
            self.logger.debug('@%s:text(%s)' % (message.from_user.username, message.text))

            self.replyText(message, "Digimatbot vous remercie pour votre message ;)")
        except:
            self.logger.exception('dispatchText()')

    def dispatch(self):
        message=self.getNextPendingMessage()
        if message:
            self.logger.debug('%s' % message)
            self.registerChat(message)
            try:
                if message.text:
                    if message.text[0]=='/':
                        self.dispatchCommand(message)
                    else:
                        self.onMessageText(message)
                else:
                    self.onMessage(message)
                return True
            except:
                self.logger.exception('dispatch()')

    # return True if some more job to do
    def onIdle(self):
        return False

    def run(self):
        self.start()
        while self.isRunning():
            try:
                if not self.dispatch():
                    if not self.onIdle():
                        self.sleep(0.5)
            except KeyboardInterrupt:
                break
            except:
                self.logger.exception('run()')
        self.stop()


if __name__ == "__main__":
    pass
