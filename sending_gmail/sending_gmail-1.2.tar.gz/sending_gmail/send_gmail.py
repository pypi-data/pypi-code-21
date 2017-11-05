#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 29 11:05:33 2017

@author: Pera
"""

import httplib2


from oauth2client import client
from oauth2client import file
from oauth2client import tools

from apiclient.discovery import build

import base64
from email.mime.text import MIMEText

import os
from os.path import expanduser


#%%

SCOPE='https://www.googleapis.com/auth/gmail.send'
       
def get_api_object():
    
    #Get home  directory
    home = expanduser("~")
    
    
    directory_of_client_secrets=home+ '/.client_secret'
    file_path=directory_of_client_secrets + '/client_secret.json'
    #Check to see if there is such a directory and coresponding file in it
    
    if not os.path.exists(directory_of_client_secrets):
        print("There is not {0} directory, please make it, and" '\n'
              "place the file client_secret.json in it".format(directory_of_client_secrets))
        return 1
    else:    
        if not os.path.exists(file_path):
            print("There is not {0} file, please create it in GOOGLE API CONSOLE, and" '\n'
                  "place it in {1}".format(file_path,directory_of_client_secrets))
            return 1
       

    flow = client.flow_from_clientsecrets(filename=file_path,scope=SCOPE)
#    print(flow)

  # Prepare credentials, and authorize HTTP object with them.
  # If the credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # credentials will get written back to a file.
    storage = file.Storage('credentials.dat')
    credentials = storage.locked_get()
    
    
    
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(flow, storage)     
        

      
    http = credentials.authorize(http=httplib2.Http())

  # Build the service object.
    client_object = build(serviceName='gmail',version='v1', http=http)
   
    return client_object





def CreateMessage(sender, to, subject, message_text):
  """Create a message for an email.
 
 Args:
   sender: Email address of the sender.
   to: Email address of the receiver.
   subject: The subject of the email message.
   message_text: The text of the email message.
 
 Returns:
   An object containing a base64url encoded email object.
 """
  message = MIMEText(message_text)
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject

  return {'raw': base64.urlsafe_b64encode(message.as_string().encode('UTF-8')).decode('ascii')}
 

def SendMessage(service, user_id, message):
    
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
  try:
      message = (service.users().messages().send(userId=user_id, body=message).execute())
     
      print ('Message Id: %s' % message['id'])
      return message

  except:
      print("Error occured")
      
      
      
      
      
      
      
#SendMessage,get_api_object,create_message    
      #sender,recipient,subject,msg_txt)

def send_gmail(sender,recipient,subject,message_text):
    
    try:
        service=get_api_object()
    
    except:
             
        return
 
       
    message=CreateMessage(sender=sender,to=recipient,subject=subject,message_text=message_text)
    
      
    SendMessage(service=service,user_id=sender,message=message)
    
   


