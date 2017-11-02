#!/usr/bin/python3.5

"""
.. module:: mongo_shelve_class
    :platform: Windows
    :synopsis: module for class :class:`Mongo_shelve`.

.. moduleauthor:: Miguel Garcia <zeycus@gmail.com>

"""


class Mongo_shelve(object):
    """Wrapper to use a mongoDB collection as a permanent dict.

    The idea is to handle a collection with typical dict operations. Very
    much like module :mod:`shelve` does, but taking advantage of mongoDB
    for performance reasons.

    The look-up takes place along a specified field name, which should be present
    in all the documents of the collection. There should be an index
    for that field in the collection, with ``unique=True``.

    The result of the look-up for a key is a dict containing all
    the fields in the mongoDB collection where keyField=key, without the
    keyField, nor the internal '_id' that mongoDB creates.
    
    """
    def __init__(self, col, keyField):
        """Constructor
        
        :param col: the collection that stores the information
        :type col: mongoDB.Collection
        :param keyField: the name of the field used for look-up
        :type keyField: str
        """
        self.col = col
        self.keyField = keyField

    def __getitem__(self, key):
        """Look-up method.

        Returns a dict with the information in the associated document.

        :param key: value to be searched in the self.keyField.
        :rtype: dict

        """
        output = self.col.find_one({self.keyField: key})
        if output is None:
            raise KeyError("Key '%s' not found in mongoDB database." % key)
        else:
            del output[self.keyField]
            del output['_id']
            return output

    def __setitem__(self, key, value):
        """Associating information to a key.

        :param key: value to which the information will be associated.
        :param value: dict {field:val} with all the information associated to key
        :type value: dict

        """
        value = value.copy()
        value[self.keyField] = key
        self.col.update_one(
            {self.keyField: key},
            {"$set": value},
            upsert=True,
        )

    def __delitem__(self, key):
        """Removal of information associated to a particular key.

        Fails if it was not present.
        """
        result = self.col.delete_one({self.keyField: key})
        if result.deleted_count != 1:
            raise KeyError("No document with key '%s' could be deleted." % key)

    def __contains__(self, key):
        """Check whether there is information associated to a particular key.

        :rtype: bool
        """
        try:
            self[key]
            return True
        except KeyError:
            return False

    def __len__(self):
        """Returns the number of keys in the permanent dict.

        :rtype: int
        """
        return self.col.count()

    def __iter__(self):
        """Iterator over the values of the look-up field."""
        yield from self.keys()

    def __repr__(self):
        return "<%s.%s (%s)>" % (self.col.database.name, self.col.name, self.keyField)

    def keys(self):
        """Iterator over keys of the look-up field."""
        for data in self.col.find():
            yield data[self.keyField]

    def items(self):
        """Iterator on pairs (look-up value, associated content)."""
        for data in self.col.find():
            key = data[self.keyField]
            del data[self.keyField]
            del data['_id']
            yield (key, data)

    def values(self):
        """Iterator on the content of each entry."""
        for _, data in self.items():
            yield data

    def clear(self):
        """Deletes all entries."""
        self.col.delete_many({})

    def delete_many(self, *args, **kwargs):
        """Wrapper for the mongoDB.Collection delete_many method.
        
        Useful if we would need to remove using filtering conditions.
        """
        return self.col.delete_many(*args, **kwargs)

    def insert(self, *args, **kwargs):
        """Wrapper for the mongoDB.Collection insert method."""
        return self.col.insert(*args, **kwargs)

    def find(self, *args, **kwargs):
        """Wrapper for the mongoDB.Collection find method."""
        return self.col.find(*args, **kwargs)


if __name__ == "__main__":
    import pymongo
    client = pymongo.MongoClient("127.0.0.1:27017")
    db = client['tvs761_hashes']
    col = db['hashes']
    ms = Mongo_shelve(col, 'filename')
    print("There are %s entries." % len(ms))

    # Insertion of new information
    ms['myFic.txt'] = dict(size=14461)
    print("Info stored: %s" % ms['myFic.txt'])
    print("There are %s entries." % len(ms))

    # Updating information
    ms['myFic.txt'] = dict(size=14732)
    print("Info stored: %s" % ms['myFic.txt'])

    # Deletion
    del ms['myFic.txt']
    print("There are %s entries." % len(ms))

    # Traversing is easy
    for key, data in ms.items():
       print("For key '%s' the information stored is %s" % (key, data))

    # Remove information for files smaller than 1 KB.
    ms.delete_many({'size': {"$lt": 1024}})
