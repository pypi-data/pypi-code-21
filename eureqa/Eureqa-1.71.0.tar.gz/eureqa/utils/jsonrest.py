
from pprint import pformat
from itertools import izip
from copy import deepcopy


class _JsonREST(object):
    """
    Internal helper class.
    For objects that represent server-side state.

    Each subclass of '_JsonREST' represents a RESTful object on the backend server.

    Say you have a RESTful object that's accessible from:
    /users/:username/favorite_puppies/:puppy_id
    And whose JSON structure looks like:
    {
        "name": (...),
        "fur_color": (...),
        "height": (...)
    }

    Then, to use _JsonREST, you would create a subclass as follows:

    class FavoritePuppy(_JsonREST):
        def __init__(self, eureqa, username, _id=None):
            super(FavoritePuppy, self).__init__(eureqa)  # JsonREST needs a valid Eureqa connection
            self._username = username
            self._puppy_name = puppy_name
            if _id:
                self._id = _id
        def _directory_endpoint(self):
            return "/users/%s/favorite_puppies" % (self._username)
        def _object_endpoint(self):
            return "/users/%s/favorite_puppies/%s" % (self._username, self._id)
        def _fields(self):
            return ["id", "name", "fur_color", "height"]

    Then you can do:
    puppy = FavoritePuppy(eureqa, "jlpicard")
    print puppy._name           # "Poodles"
    print puppy._fur_color      # white
    print puppy._height         # 3
    puppy._create()             # Puppy is now saved on the server

    puppy._height = 4
    puppy._update()             # Server now stores a height of 4

    puppy_copy = FavoritePuppy.get(eureqa, "jlpicard", puppy._id)
    assert puppy == puppy_copy  # Should be the same

    puppy._delete()             # Puppy is no longer stored on the server

    And so on; see the docstrings on the functions below for details.

    Fields are preceded with underscores.  The expectation is that, for any public API,
    accessor properties will be written that control access and that provide autocomplete and docstrings.

    For a guide on how to convert existing classes to use this class, see README_JSONREST.txt
    """

    def __init__(self, eureqa):
        self._eureqa = eureqa

    ##########
    # All subclasses must implement the following methods
    ##########
    def _object_endpoint(self):
        """
        Compute and return a URL-path representing the current object.
        For example, '"/analyses/%s" % self._analysis_id'.
        """
        raise NotImplementedError

    def _directory_endpoint(self):
        """
        Return a URL-path representing the path containing these objects.
        (For POST'ing new object or GET'ing a list of all objects.)
        For example, '"/analyses"'.
        """
        raise NotImplementedError

    def _fields(self):
        """
        List (or other iterable) of field names to expect from the backend JSON,
        that map 1:1 to private properties on the current object.
        If this object has any fields that need special handling, they should
        be handled by overriding '_to_json()' and '_from_json()'.
        For example, '[ "id", "title", "description", "variables", "stuff", "more_things" ]'
        """
        raise NotImplementedError

    ##########
    # Default implementations (can optionally be overridden)
    ##########

    def _to_json(self):
        """ Convert this object into a tree of primitive JSON-compatible Python types """
        ret = {}
        for field, private_field in izip(self._fields(),
                                         self._private_fields()):
            if hasattr(self, private_field):
                ret[field] = getattr(self, private_field)
        return ret

    def _from_json(self, body):
        """
        Load the output of '_to_json()' into this object
        :param dict body: The output of '_to_json()'
        """
        for field, private_field in izip(self._fields(),
                                         self._private_fields()):
            if field in body:
                setattr(self, private_field, body.get(field))

    def _allow_request_object(self):
        """
        Returns True if it's currently ok to hit the REST endpoint.
        Should return False for partially-constructed objects.
        Note that HTTP requests will be IGNORED when this returns False!
        """
        try:
            self._object_endpoint()
            return True
        except:
            return False

    def _allow_request_directory(self):
        """
        Returns True if it's currently ok to hit the REST endpoint.
        Should return False for partially-constructed objects.
        Note that HTTP requests will be IGNORED when this returns False!
        """
        try:
            self._directory_endpoint()
            return True
        except:
            return False

    ##########
    # Provided helper methods (not intended to be overridden)
    ##########

    @classmethod
    def _construct_from_json(cls, body, *args, **kwargs):
        """
        Construct a new instance of this class.  Populate it with the contents of 'body'.
        :param dict body: The output of '_to_json()', to be used to populate the data in the new instance
        :return: Constructed instance of this class
        """
        ret = cls(*args, **kwargs)
        ret._from_json(body)
        return ret

    def _create(self):
        """ Construct the current object on the server """
        if not self._allow_request_directory():
            return

        endpoint = self._directory_endpoint()
        new_body = self._eureqa._session.execute(endpoint, 'POST', self._to_json())
        self._from_json(new_body)

    def _update(self):
        """ Update the current object on the server """
        if not self._allow_request_object():
            return

        endpoint = self._object_endpoint()
        new_body = self._eureqa._session.execute(endpoint, 'PUT', self._to_json())
        self._from_json(new_body)

    def _delete(self):
        """ Delete the current object on the server """
        if not self._allow_request_object():
            return

        endpoint = self._object_endpoint()
        self._eureqa._session.execute(endpoint, 'DELETE')

    def _get_self_json(self):
        """
        Fetch the JSON representation of the current object from the server
        :return: dict representing the JSON-serializable form of the current object
        """
        endpoint = self._object_endpoint()
        new_body = self._eureqa._session.execute(endpoint, 'GET')
        return new_body

    def _get_self(self):
        """
        Re-fetch the current object from the server.
        Mutates this object in place.
        :return: self
        """
        self._from_json(self._get_self_json())
        return self

    @classmethod
    def _get(cls, *args, **kwargs):
        """
        Fetch the specified object from the server.
        Keyword arguments should specify all fields used by '_object_endpoint()',
        as well as any arguments that this class's constructor requires
        in order to connect to the Eureqa server.
        :return: Instance of the current class describing the specified object
        """
        self = cls(*args, **kwargs)
        return cls._construct_from_json(self._get_self_json(), *args, **kwargs)

    def _get_all_json_from_self(self):
        """
        Fetch a JSON representation of all objects in the same directory as this object.
        :return: list() of dicts
        """
        endpoint = self._directory_endpoint()
        new_body_list = self._eureqa._session.execute(endpoint, 'GET')
        return new_body_list

    def _get_all_from_self(self):
        """
        Fetch a list of all objects in the same directory as this object.
        :return: list() of objects of the current type
        """
        new_body_list = self._get_all_json_from_self()

        new_obj_list = []
        for new_body in new_body_list:
            new_obj = self._construct_from_json(new_body)
            new_obj_list.append(new_obj)
        return new_obj_list

    @classmethod
    def _get_all(cls, *args, **kwargs):
        """
        Get all objects in the specified directory.
        Keyword arguments should specify all fields used by '_directory_endpoint()',
        as well as any arguments that this class's constructor requires
        in order to connect to the Eureqa server.
        :return: list() of instances of the current class
        """
        self = cls(*args, **kwargs)
        return [cls._construct_from_json(x, *args, **kwargs)
                for x in self._get_all_json_from_self()]

    def __eq__(self, other):
        return self._to_json() == other._to_json()

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(repr(self._to_json()))

    def __repr__(self):
        kwargs_list = ["%s=%s" % (key, repr(val))
                       for key, val in sorted(self._to_json().items())]
        return "%s(%s)" % (self.__class__.__name__, ", ".join(kwargs_list))

    def __str__(self):
        return pformat(self._to_json(), indent=4)

    ##########
    # Utility methods (for us, not for child classes)
    ##########

    def _private_fields(self):
        # Carefully use iterators to represent
        return ('_' + f for f in self._fields())
