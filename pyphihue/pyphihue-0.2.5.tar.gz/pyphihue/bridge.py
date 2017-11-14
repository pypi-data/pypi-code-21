import requests


class Bridge(object):
    """This class creates objects of the hue bridge type. If a username
    is not provided the only thing to do is to use the createuser
    method.

    Keyword arguments:
    ipadress - ipaddress of the Philips Hue Bridge
    username - valid Philips Hue Bridge username
    """
    def __init__(self, ipaddress, username=None):
        """Constructor. """
        self.ipaddress = ipaddress
        self.username = username

    def __repr__(self):
        """Representation of the Bridge object."""
        return "Bridge('{}', '{}')".format(self.ipaddress, self.username)

    def __str__(self):
        """Representation of the Bridge object."""
        return 'Bridge with ip-address: {}'.format(self.ipaddress)

    def url(self):
        """Constucts and returns the url of the bridges REST-API."""
        if (self.username is None):
            url = 'http://' + self.ipaddress + '/api/'
        else:
            url = 'http://' + self.ipaddress + '/api/' + self.username
        return url

    def createuser(self, devtype):
        """Creates a new username on the bridge.

        Keyword argument:
        devtype - device type that will use this username.
        """
        url = self.url()
        body = {}
        body['devicetype'] = devtype
        response = requests.post(url, json=body).json()
        return response

    def deleteuser(self, user2bedeleted):
        """Deletes a user from the bridge.

        Keyword argument:
        user2bedeleted - the username that should be deleted.
        """
        url = self.url() + '/config/whitelist/' + user2bedeleted
        response = requests.delete(url).json()
        return response

    def listusers(self):
        """Get the username's from the bridge and returns a list. """
        users = []
        url = self.url() + '/config'
        response = requests.get(url).json()
        whitelist = response['whitelist']
        for key in whitelist:
            users.append(whitelist[key]['name'])
        return users

    def getgroupids(self):
        """Get all defined group id's and return a list of group id's"""
        url = self.url() + '/groups'
        gids = list(requests.get(url).json().keys())
        return gids

    def getlightids(self):
        """Get all light id's and return a list of light id's"""
        url = self.url() + '/lights'
        lightids = list(requests.get(url).json().keys())
        return lightids
