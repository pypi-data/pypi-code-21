import time
import json
from functools import wraps

from fake_request import FakeRequest, FakeResponse

def message_formatter(func):
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        
        try:
            starttime = time.time()
            
            message = kwargs.pop('message', args[0]) # its gotta always be first argument!
            
            fake_request = FakeRequest(message = message)

            response = func(request = fake_request, **kwargs)
            
            fr = FakeResponse(original_request=fake_request, response = response)
            response = fr.get_response()
            
            endtime = time.time() - starttime
            reply(message = message, response = response, endtime = endtime)

            
        except Exception as e:
            raise
            message.reply_channel.send({
                "text": json.dumps(str(e))})
        
        
        return None

    return wrapper


def reply(message, **kwargs):
    
    message.reply_channel.send({
        "text": json.dumps(kwargs['response'])})

    message.reply_channel.send({
        "text": json.dumps(str(kwargs['endtime'] * 1000) + ' ms')})