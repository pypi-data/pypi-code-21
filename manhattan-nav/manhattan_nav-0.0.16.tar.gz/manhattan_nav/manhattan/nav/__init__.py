from collections import namedtuple
from urllib.parse import urlsplit

import flask

__all__ = [
    # Classes
    'LazyNavItem',
    'Nav',
    'NavItem',

    # Exceptions
    'MenuNotFound'
    ]


# A named tuple structure used to store the results of `Nav` queries.
QueryResult = namedtuple(
    'QueryResult',
    ['exists', 'allowed', 'active', 'active_sub', 'url']
    )


class MenuNotFound(Exception):
    """
    Raised when a request to `Nav.menu` fails to find or generate a menu.
    """


class Nav:
    """
    The Nav class is a static class that allows;

    - access rules to be defined and assigned to endpoints,
    - querying of endpoints to see;
        - if an endpoint exists,
        - if access to it is allowed by the caller,
        - if it is the currently active link.

    For example to define a rule and assign it to an endpoint:

        @Nav.rule
        def admin_only(**kwargs):
            return g.backend_user.role == 'admin'

        Nav.apply('some.endpoint', 'admin_only')

    The Nav.query class is typically passed to templates to templates as a
    function named nav:

        {% set link = nav('some.endpoint', some=arg) %}

        {% if link.exists %}
            {% if link.allowed %}
                <a href="{{ link.url }}" class="{% 'active' if link.active %}">Link</a>
            {% else %}
                <span>Disabled</span>
            {% endif %}
        {% endif %}
    """

    # A dictionary of nav menus
    _menus = {}

    # A dictionary that holds the defined rules for navigation
    _rules = {}

    # A dictionary that holds the rules for endpoints
    _endpoint_rules = {}

    # Endpoint cache (per app)
    _endpoints = {}

    @classmethod
    def allowed(cls, endpoint, **view_args):
        """
        Return True if the specified endpoint (plus `view_args`) is allowed.
        """
        if endpoint in cls._endpoint_rules:
            for rule_name in cls._endpoint_rules[endpoint]:
                if not cls._rules[rule_name](**view_args):
                    return False
        return True

    @classmethod
    def apply(cls, endpoint, rules):
        """Apply one or more rules to the given endpoint"""
        cls._endpoint_rules[endpoint] = list(rules)

    @classmethod
    def exists(cls, endpoint):
        """Return True if the specified endpoint exists"""
        app = flask.current_app

        # On the first query we need to build a map of endpoints to make
        # querying quicker.
        if app not in cls._endpoints:
            cls._endpoints[app] = set(
                [r.endpoint for r in app.url_map.iter_rules()]
                )

        return endpoint in cls._endpoints[app]

    @classmethod
    def local_menu(cls):
        """
        Return a new `NavItem` that can be used as a local menu, no reference is
        kept to the `NavItem` instance hence its scope is local in terms of
        usage.
        """
        return NavItem()

    @classmethod
    def menu(cls, name, raise_unless_exists=False):
        """
        The `menu` method provides a simple way to define and share nav menus
        (a `NavItem`) between modules/files. If the named menu exists it's
        returned, if not it's generated, stored and returned, or if the
        `raise_unless_exists` flag is `True` an Exists exception will be raised.
        """
        if name not in cls._menus:
            if raise_unless_exists:
                raise MenuNotFound(name)
            else:
                cls._menus[name] = NavItem()

        return cls._menus[name]

    @classmethod
    def query(cls, endpoint, **view_args):
        """
        Query a given endpoint and set of view arguments returning a
        `QueryResult` named tuple. The `QueryResult` holds the following
        information;

        - `exists` if the endpoint exists,
        - `allowed` if the caller is allowed to call the endpoint with view
          arguments,
        - `active` if the endpoint (exluding any query) is the sames as the
          current request path,
        - `active_sub` if the endpoint (excluding any query) includes the
          current request path,
        - `url` the URL for the endpoint with view arguments.
        """
        exists = cls.exists(endpoint)

        # Build the URLs for the endpoint
        url = None
        base_url = None
        if exists:
            url = flask.url_for(endpoint, **view_args)
            base_url = url

            # Strip the script root from the base URL to support dispatcher
            # configuration.
            if base_url.startswith(flask.request.script_root + '/'):
                base_url = url[len(flask.request.script_root):]

        # Normalize the URL and path
        path = urlsplit(flask.request.path).geturl()
        if url:
            url = urlsplit(url).geturl()

        # Remove query string from `base_url` for matching
        base_url = (base_url or '--no-url--').split('?', 1)[0]

        return QueryResult(
            exists=exists,
            allowed=exists and cls.allowed(endpoint, **view_args),
            active=path == base_url,
            active_sub=path.startswith(base_url + '/'),
            url=url
            )

    @classmethod
    def rule(cls, *args, **kw_args):
        """
        Decorate a function with this method to define it as a rule:

            @Nav.rule
            def admin_only(**kwargs):
                return g.backend_user.role == 'admin'

        Optionally a name can be specified to set the rule for but by default
        the `func`s name will be used.
        """
        def wrap(func):
            cls.set_rule(func, **kw_args)
            return func

        if len(args) == 1 and callable(args[0]):
            return wrap(args[0])
        else:
            return wrap

    @classmethod
    def set_rule(cls, func, name=None):
        """
        Set a rule. Optionally a name can be specified to set the rule for but
        by default the `func`s name will be used.
        """

        assert callable(func), '`func` must be callable'

        cls._rules[name or func.__name__] = func


class NavItem:
    """
    The NavItem class provides a way to define structured navigation, better
    described as menus, e.g:

        menu = Nav.menu('some_menu')
        menu.add(NavItem('Some link', 'some.endpoint'))
        sub_menu = menu.add('Sub menu')
        sub_menu.add(NavItem('Sub link', 'sub.endpoint'))
        ...
    """

    def __init__(self, label=None, endpoint=None, view_args=None,
            fixed_url=None, id=None, badge=None, data=None, after=None):

        # The label that will be displayed in the interface for the item
        self.label = label

        # The endpoint and view_arguments that will be used to generate the
        # item's URL. Optionally `view_args` can be a callable that returns a
        # dictionary of arguments.
        self.endpoint = endpoint
        self._view_args = view_args or {}

        # A fixed URL can be specified instead of an endpoint and view arguments
        self.fixed_url = fixed_url

        # An Id for the item, this is not the HTML Id for the item, the Id is
        # used to make it simple to determine where an item sits within its
        # parent using the `after` argument. By default the Id is set to the
        # endpoint.
        self.id = id or endpoint

        # A badge should be either a boolean (True means the item should display
        # a badge), an integer (representing the badge count), or a callable
        # that returns either a boolean or integer.
        #
        # NOTE: A badge is a small UI component that typically indicates a
        # change and/or count.
        self._badge = badge

        # A dictionary or callable that returns a dictionary that will be
        # available within the HTML template.
        self._data = data or {}

        # If specified, the `after` argument indicates the Id of the sibling to
        # place the item after.
        self.after = after

        # The item's children
        self._children = []

        # This item's parent
        self._parent = None

    # Properties

    @property
    def badge(self):
        """
        Return either a boolean (True means the item should display a badge),
        an integer (representing the badge count) or a callable that returns
        either a boolean or integer.

        If badge is a callable the property will return the result of calling
        it.
        """
        if callable(self._badge):
            return self._badge()
        return self._badge

    @badge.setter
    def badge(self, value):
        """
        Set the badge value for the item, badge values should be either a
        boolean (True, False), an integer (indicating a count) or a callable
        that returns either a boolean or integer.
        """
        self._badge = value

    @property
    def children(self):
        """
        The list of children for the `NavItem`. The `children` property is
        generated on call so that `LazyNavItem`s can be expanded and to allow
        the order to be set based on the `after` attribute of each child.

        NOTE: The list of children returned will contain only NavItems and the
        order will be set based on the the order each item was added in and the
        `after` attribute.
        """

        # Initially we build a first come ordered list of all the items
        ids = set({})
        unordered = []

        i = 0
        child_stack = list(self._children)
        while len(child_stack):
            child = child_stack.pop(0)
            if isinstance(child, LazyNavItem):
                # Expand lazy items
                child_stack = child.items + child_stack

            else:
                i += 1
                unordered.append(child)

                if child.id:
                    ids.add(child.id)

        # Re-order the list based on each items after anchor
        ordered = []
        ordered_ids = []
        while unordered:
            child = unordered.pop(0)
            if child.after and child.after in ids:
                if child.after in ordered_ids:
                    index = ordered_ids.index(child.after) + 1
                    ordered.insert(index, child)
                    ordered_ids.insert(index, child.id)
                    continue
            else:
                ordered.append(child)
                ordered_ids.append(child.id)
                continue
            unordered.append(child)

        return ordered

    @property
    def data(self):
        """
        Return the data for item, if the `data` value is callable then the
        result of calling `data` will be returned.
        """
        if callable(self._data):
            return self._data()
        return self._data

    @data.setter
    def data(self, value):
        """
        Set the data for the item. Data is typically used in the HTML template
        and can be set as a dictionary or a callable that returns a dictionary
        """
        self._data = value

    @property
    def is_active(self):
        """Return True if the nav item is active"""
        link = self.query
        return link.active or link.active_sub

    @property
    def is_open(self):
        """
        Return True if the nav item is active or has an active child and
        therefore should be open.
        """
        if self.is_active:
            return True
        for child in self.children:
            if child.is_active:
                return True
        return False

    @property
    def is_parent(self):
        """
        Return True if the item has children.

        Note: Technically if the only child/children for the item are
        `LazyNavItems` then the item could return True for is_parent but not
        actually have any children (due to the dynamic nature of
        `LazyNavItems`), if this possibility needs to be catered for test by
        calling `len(self.children)` and store the result as this is a
        potentially expensive operation.
        """
        return len(self._children) > 0

    @property
    def query(self):
        """Return the `Nav.query(...)` result for the item"""
        return Nav.query(self.endpoint, **self.view_args)

    @property
    def parent(self):
        """Return the parent for the item"""
        return self._parent

    @property
    def view_args(self):
        """
        Return the view arguments for item, if the `view_args` value is callable
        then the result of calling `view_args` will be returned.
        """
        if callable(self._view_args):
            return self._view_args()
        return self._view_args

    @view_args.setter
    def view_args(self, value):
        """
        Set the view arguments that will accompany the endpoint for the item.
        """
        self._view_args = value

    @property
    def visible_child_count(self):
        """
        Return the number of visible children within a nav item, this differs
        from the number of children in that it includes the number of children
        in parent item that are flagged as groups.
        """
        visible_child_count = 0
        for child in self.children:
            visible_child_count += 1
            if 'group' in child.data:
                visible_child_count += len(child.children)
        return visible_child_count

    # Methods

    def add(self, item, index=None):
        """
        Add a child (an instance of a NavItem or LazyNavItem) to the item. The
        item added will be returned by the method making it easier to define and
        add an item at the same time, e.g:

            my_item = some_menu.add(NavItem('My item', 'my.item'))
        """

        # Add the item as a child
        if index is None:
            self._children.append(item)
        else:
            self._children.insert(index, item)

        # Set the items parent as this item
        item._parent = self

        return item


class LazyNavItem:
    """
    `LazyNavItems` allow one or more NavItems to be generated dynamically, this
    is useful in a variety of situations but most commonly when a set of
    navigation links is based on a database collection, for example a list of
    product categories:

        def categories(creator):
            return [NavItem(c.name, 'category', {'category': c}) for c in Category.many()]

        item = LazyNavItem(categories)
    """

    def __init__(self, func, after=None):

        # The callable/function that will generate nav items in place of the
        # lazy nav item.
        self.func = func

        # The callable/function that will generate `NavItems` in place of this
        # item.
        self.after = after

        # This item's parent
        self._parent = None

    @property
    def items(self):
        """Generate the `NavItem`s for this item"""
        items = self.func(self)

        # Ensure each item is assigned a default `after`
        if self.after:
            for item in items:
                item.after = item.after or self.after

        return items

    @property
    def parent(self):
        """Return the items parent"""
        return self._parent
