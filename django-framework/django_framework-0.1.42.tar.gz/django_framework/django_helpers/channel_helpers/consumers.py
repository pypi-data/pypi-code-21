# In consumers.py
from channels import Group
from channels import Channel

from channels.sessions import channel_session
import time

import json
from django.contrib.auth.models import User



# Connected to websocket.connect
@channel_session
def ws_connect(message):
    # Accept connection
    message.reply_channel.send({"accept": True})
    # Work out room name from path (ignore slashes)
    room = message.content['path'].strip("/")
    # Save room in session and add us to the group
    message.channel_session['room'] = room + 'argagaf'
    
    
    Group("chat-%s" % message.channel_session['room']).add(message.reply_channel)
    

# Connected to websocket.receive
@channel_session
def ws_message(message):
    '''We have a couple of ways to move forward, we can have the 
    consumer deal with the message, or we write the logic for a URL
    # into here. :( '''
    payload = json.loads(message['text'])
    payload['reply_channel'] = message.content['reply_channel'] # required.
    
    Channel('http_request.json').send(payload)


# Connected to websocket.disconnect
@channel_session
def ws_disconnect(message):
    Group("chat-%s" % message.channel_session['room']).discard(message.reply_channel)
