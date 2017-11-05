""" My kervi application """
from kervi.application import Application
import kervi.utility.nethelper as nethelper

if __name__ == '__main__':
    APP = Application({{
        "info":{{
            "id":"{id}",
            "name":"{name}",
            "appKey":"",
        }},
        "modules":["sensors", "controllers", "cams"],
        "network":{{
            "IPAddress": nethelper.get_ip_address(),
            "IPCRootPort":{base_port},
            "WebSocketPort":{websocket_port},
            "WebPort": {ui_port},
            "IPCSecret":b"{secret}"
        }},
    }})

    APP.run()
