#!/usr/bin/python

from datetime import datetime
import json

from xconnectpy.lib.base import Entity
from xconnectpy.lib.sitecore import Contact, InteractionInitiator


class Interaction(Entity):

    EntityResource = "Interactions"

    def __init__(self, Contact: Contact, Initiator: InteractionInitiator, ChannelId, UserAgent):
        self.Contact = Contact
        self.Initiator = Initiator.value
        self.ChannelId = ChannelId
        self.UserAgent = UserAgent

        self.Events = []

    def serialize(self):
        obj = self.__dict__.copy()

        obj['StartDateTime'] = datetime.utcnow().isoformat()
        obj['EndDateTime'] = datetime.utcnow().isoformat()

        if self.Contact:
            obj['Contact'] = {
                "@odata.id": "https://skynetxconnect.coria.com/odata/Contacts({0})".format(self.Contact.Id)
            }

        if self.Events:
            events = []

            for event in self.Events:
                events.append(event.serialize())

            obj['Events'] = events

        return json.dumps(obj)
