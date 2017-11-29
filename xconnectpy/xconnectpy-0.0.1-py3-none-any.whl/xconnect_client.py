#!/usr/bin/python

from overloading import overload
from typing import List
import json

from xconnectpy.lib.base import *
from xconnectpy.lib.sitecore import *


class XConnectClient(Client):

    RequestQueue = []

    @overload
    def set_facet(self, facetReference: FacetReference, data: Facet):
        pass

    @overload
    def set_facet(self, entity: EntityReference, data: Facet):
        pass

    @overload
    def set_facet(self, entity: Entity, facetKey: str, data: Facet) -> None:
        """

        :param entity:
        :param facetKey:
        :param data:
        :return:
        """
        resource = "{0}({1})/{2}".format(entity.EntityResource, entity.Id, facetKey)
        request = Request(resource, data.serialize())
        self.RequestQueue.append(request)

    def get(self, reference: IdentifiedContactReference, expand_options: ExpandOptions = {}):
        resource = "{0}?%24filter=Identifiers%2fany(id%3aid%2fIdentifier+eq+%27{1}%27+and+id%" \
                   "2fSource+eq+%27{2}%27)&%24expand=Identifiers,MergeInfo,ConsentInformation"\
            .format(Contact.EntityResource, reference.Identifier, reference.Source)

        response = self.get_generic(resource)

        string = response.read().decode('utf-8')
        json_obj = json.loads(string)

        return Contact(Id=json_obj['value'][0]['Id'])

    async def get_async(self, resource, expand_options: ExpandOptions = {}):
        """
        Gets the entities from their references if they exist.
        :param resource:
        :return:
        """
        pass

    @overload
    async def get_contact_async(self: object, reference: Contact, expand_options: ExpandOptions):
        """
        Gets a single contact.
        :param reference:
        :param expand_options:
        :return:
        """
        pass

    @overload
    async def get_contact_async(self: object, id: str, expand_options: ExpandOptions):
        """
        Gets a single contact.
        :param id:
        :param expand_options:
        :return:
        """
        pass

    @overload
    async def get_contacts_async(self: object, references: List[Contact], expand_options: ExpandOptions):
        """
        Gets the contacts for specified references.
        :param references:
        :param expand_options:
        :return:
        """
        pass

    @overload
    async def get_contacts_async(self: object, ids: List[str], expand_options: ExpandOptions):
        """
        Gets the contacts for specified IDs.
        :param ids:
        :param expand_options:
        :return:
        """
        pass

    async def get_device_profile_async(self: object, reference: DeviceProfile, expand_options: ExpandOptions):
        """
        Gets a single device profile.
        :param reference:
        :param expand_options:
        :return:
        """
        pass

    async def get_device_profiles_async(self: object, references: List[DeviceProfile], expand_options: ExpandOptions):
        """
        Gets the device profiles for the specified references.
        :param references:
        :param expand_options:
        :return:
        """
        pass

    async def get_interaction_async(self: object, reference: Interaction, expand_options: ExpandOptions):
        """
        Gets a single interaction.
        :param reference:
        :param expand_options:
        :return:
        """
        pass

    async def get_interactions_async(self: object, references: List[Interaction], expand_options: ExpandOptions):
        """
        Gets the interactions for the specified references.
        :param references:
        :param expand_options:
        :return:
        """

    def add_contact(self, contact: Contact):
        """
        Registers that the specified contact will be added when the Client's SubmitAsync() method is called.
        :param contact:
        :return:
        """
        request = Request(Contact.EntityResource, contact.serialize(), contact)
        self.RequestQueue.append(request)

    def add_contact_identifier(self, contact: Contact, identifier: ContactIdentifier):
        """
        Registers an operation in the specified Client that adds the specified identifier to the contact.
        :param contact:
        :param identifier:
        :return:
        """
        pass

    def add_device_profile(self, device_profile: DeviceProfile):
        """
        Registers that the specified device profile will be added when the Client's SubmitAsync() method is called.
        :param device_profile:
        :return:
        """
        pass

    def add_interaction(self, interaction: Interaction):
        """
        Registers that the specified interaction will be added when the Client's SubmitAsync() method is called.
        :param interaction:
        :return:
        """
        resource = "{0}({1})/{2}".format(Contact.EntityResource, interaction.Contact.Id, Interaction.EntityResource)
        request = Request(resource, interaction.serialize())
        self.RequestQueue.append(request)

    def submit(self):
        """
        Submits operations added to this Client
        :return:
        """
        for request in self.RequestQueue:
            try:
                self.post_generic(request.resource, request.payload)
                print("Successfully executed request.")
            except Exception:
                print("error")

    async def submit_async(self):
        """
        Submits operations added to this Client
        :return:
        """
        pass
