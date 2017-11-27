from ftw.builder import builder_registry
from ftw.builder.dexterity import DexterityBuilder


class AddressBlockBuilder(DexterityBuilder):
    portal_type = 'ftw.addressblock.AddressBlock'

builder_registry.register('sl addressblock', AddressBlockBuilder)
