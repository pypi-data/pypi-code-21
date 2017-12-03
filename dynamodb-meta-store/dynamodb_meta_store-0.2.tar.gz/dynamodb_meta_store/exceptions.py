class TableNotReadyException(Exception):
    """ Exception thrown if the table is not in ACTIVE or UPDATING state """
    pass


class MisconfiguredSchemaException(Exception):
    """ Exception thrown if the table does not match the configuration """
    pass


class ItemNotFound(Exception):
    """ Exception thrown if the item does not exist in table """
    pass
