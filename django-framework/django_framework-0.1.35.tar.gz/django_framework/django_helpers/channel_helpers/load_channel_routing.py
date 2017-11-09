import importlib
from channels import route

from django.conf import settings

from consumers import ws_connect, ws_message, ws_disconnect

def load_channel_routing(exclude = None, include = None, fail_silently = True, **kwargs):
    # variable checking.  Make sure things are either None or a List
    if exclude != None and include != None:
        raise ValueError('Conflicting commands on loading routing from applications.  Only exclude OR include can be set')
    
    if exclude != None and type(exclude) is not list:
        raise ValueError('The input variable exclude must be of type list')
    
    if include != None and type(include) is not list:
        raise ValueError('The input variable include must be of type list')

    # default routing, deal with initial connections, disconnects etc.
    channel_routing = [
            # determines what to do when a websocket initially connects
            route("websocket.connect", ws_connect),
            # determine what to do when we receive a message.  All websockets will be sending messages
            route("websocket.receive", ws_message),
            
            # when a websocket closes.
            route("websocket.disconnect", ws_disconnect),
        ]

     # dynamically get the routes! we will enforce that the routes must exist for ALL apps
    for app_name in settings.SERVER_APPS:
        # skip over everyone explicitly told to skip over
        if exclude is not None and app_name in exclude:
            continue

        # only include the things explicitly set to include
        if include is not None and app_name in include:
            pass  
        else:
            continue
        
        # import the routes from the specific files!
        try:
            
            module = importlib.import_module(app_name + '.routes', package=None)
            for channel_name,method_callback, filters in module.routes:
                channel_routing.append(route(channel_name, method_callback, **filters))
        
        except Exception as e:
            print('Problem loading {app_name} routing.'.format(app_name = app_name))
            print('Check to make sure the App has a routes.py file.')
            print('Check to make sure routes.py has list variable routes')
            print('Error:', e)
            
        return channel_routing