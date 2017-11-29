#!/usr/bin/python

from xconnectpy.lib.base import Entity


class EntityReference(Entity):

    def __init__(self, entity: Entity, facetKey: str):
        self.entity = entity
        self.facetKey = facetKey
