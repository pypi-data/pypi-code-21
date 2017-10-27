"""
Classes for prototyping and storing content snippets.
"""

import copy
import inspect
import os
import uuid

import flask
import inflection
from manhattan import comparable
from manhattan import manage
from mongoframes import ASC, Frame, IndexModel, Q, SubFrame

__all__ = [
    'GlobalRegion',
    'GlobalSnippet',
    'Snippet',
    'SnippetType'
]


class GlobalRegion(comparable.ComparableFrame):
    """
    Global regions provide support for named regions of editable content that
    can be included in HTML content.
    """

    _fields = {
        'name',
        'content',
        'assets'
    }

    _indexes = [
        IndexModel([('name', ASC)], unique=True)
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.assets is None:
            self.assets = {}

    @classmethod
    def get_content(cls, name):
        """Return the content for the named global region"""
        global_region = cls.one(Q.name == name)
        if global_region:
            return global_region.content


class GlobalSnippet(comparable.ComparableFrame):
    """
    A snippet that is typically shared across multiple content locations
    allowing updates to be applied globally to all instances of the snippet.
    """

    _fields = {
        'type',
        'visible',

        # Fields only assigned to local snippets
        'settings',
        'contents',

        # Fields only assigned to global snippets
        'label'
    }

    @property
    def snippet_type_cls(self):
        return SnippetType.get_snippet_types().get(self.type)

    def to_snippet(self):
        """Return a `Snippet` instance representing the global snippet"""
        snippet = Snippet(
            id=None,
            type=self.type,
            scope='global',
            global_id=self._id
        )

        # To improve performance we manually set the value of the global snippet
        # cache against the snippet to prevent an unnecessary look up.
        snippet._global_snippet_cache = self

        return snippet


class Snippet(SubFrame):
    """
    A snippet within a content flow.
    """

    _fields = {
        'id',
        'type',
        'scope',

        # Fields only assigned to local snippets
        'local_settings',
        'local_contents',

        # Fields only assigned to global snippets
        'global_id'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Defaults
        if self.id is None:
            self.id = str(uuid.uuid4())

        if self.local_settings is None:
            self.local_settings = {}

        if self.local_contents is None:
            self.local_contents = {}

        # A cached version of the associated global snippet (if any)
        self._global_snippet_cache = None

    # Read-only

    @property
    def contents(self):
        if self.scope == 'global':
            return self.global_snippet.contents
        return self.local_contents

    @property
    def global_label(self):
        if self.scope == 'global':
            return self.global_snippet.label

    @property
    def global_snippet(self):
        # Make sure the snippet is global
        if self.scope != 'global':
            return None

        # Ensure we cache the global snippet the first time we request it
        if self._global_snippet_cache is None:
            self._global_snippet_cache = GlobalSnippet.by_id(self.global_id)

        return self._global_snippet_cache

    @property
    def settings(self):
        if self.scope == 'global':
            return self.global_snippet.settings
        return self.local_settings

    @property
    def type_cls(self):
        return SnippetType.get_snippet_types().get(self.type)

    # Methods

    def copy(self):
        """Return a copy of the snippet"""
        return self.__class__(
            id=str(uuid.uuid4()),
            type=self.type,
            scope=self.scope,
            local_settings=copy.deepcopy(self.local_settings),
            local_contents=copy.deepcopy(self.local_contents),
            global_id=self.global_id
        )

    def render(self, template_args=None):
        """Render and return a HTML string for the snippet"""
        return self.type_cls.render(self, template_args)

    def to_json_type(self):
        """Return a JSON safe dictionary representing the snippet"""
        json_data = {
            'id': self.id,
            'type': self.type_cls.to_json_type(),
            'scope': self.scope,
            'settings': self.settings,
            'contents': self.contents
        }

        if self.scope == 'global':
            json_data.update({
                'global_id': str(self.global_id),
                'global_label': self.global_label
            })

        return json_data


class SnippetTypeMeta(type):
    """
    Meta class for snippet types to provide base class attribute defaults and
    automate registration.
    """

    def __new__(meta, name, bases, dct):

        # Defaults
        if 'available' not in dct:
            dct['available'] = True

        if 'flows' not in dct:
            dct['flows'] = set(['*'])

        if 'id' not in dct:
            dct['id'] = inflection.underscore(name)

        if 'label' not in dct:
            label = inflection.underscore(name).replace('_', ' ').capitalize()
            dct['label'] = label

        cls = super().__new__(meta, name, bases, dct)

        if 'template_path' not in dct:
            filepath = os.path.relpath(inspect.getfile(cls))
            parts = os.path.split(filepath)[0].split('/')
            template_name = inflection.underscore(name)
            cls.template_path = os.path.join(
                '/'.join([parts[-1], 'snippet_types']),
                template_name + '.html'
            )

        # Register the class
        if len(bases):
            bases[0]._snippet_types[cls.id] = cls

        return cls


class SnippetType(metaclass=SnippetTypeMeta):
    """
    Snippets are created based on a snippet type, the type determines the
    template used to render the snippet, the settings that can be set against
    the snippet and the behaviour when rendering the template.

    All snippet types must inherit from this class but it should not be used
    directly.

    Snippet types should be static classes, they should not be initialized.
    """

    # A table of all registered snippets
    _snippet_types = {}

    # Flag indicating if the snippet type is currently available, e.g if a
    # snippet type is used only as a base class or if the type has been achived.
    available = False

    # A list of flows the snippet type is available in
    flows = None

    # A unique Id for the snippet type
    id = ''

    # A verbose label for the snippet type (used to help make the snippet type
    # easy to identify).
    label = None

    # URL to a preview image for the snippet type
    image_url = None

    # Path to the template that will be used when rendering the snippet
    template_path = None

    @classmethod
    def get_default_settings(cls):
        """Return the default settings for a snippet of this type"""
        return {}

    @classmethod
    def get_image_url(cls):
        """Return an image URL for the snippet"""

        if not cls.image_url:
            return ''

        # Get the manage app
        manage_app = manage.utils.get_app(flask.current_app._dispatcher)
        if not manage_app:
            return cls.image_url

        # Get the static asset loader from the Jinja env
        get_static_asset = manage_app.jinja_env.globals.get('get_static_asset')
        if not get_static_asset:
            return cls.image_url

        return get_static_asset(cls.image_url)

    @classmethod
    def get_jinja_env(cls):
        """
        Return an environment to render templates with (this method should
        be overridden if you want to provide a custom environment).
        """
        return flask.current_app._dispatcher.app.jinja_env

    @classmethod
    def get_settings_form(cls):
        """Return the form used to set settings a snippet of this type"""
        return None

    @classmethod
    def get_snippet_types(cls, flows=None, only_available=True):
        """
        Return a table of snippet type clases, by default only available snippet
        types are returned (table structure is `{id: cls}). Optionally you can
        specify a list/set of flow Ids to filter by.
        """
        snippet_types = {}
        for id, cls in SnippetType._snippet_types.items():
            if only_available and not cls.available:
                continue
            if flows:
                if ('*' not in cls.flows) and set(flows).isdisjoint(cls.flows):
                    continue
            snippet_types[id] = cls
        return snippet_types

    @classmethod
    def render(cls, snippet, template_args=None):
        """Render and return a HTML string for the given snippet"""
        template = cls.get_jinja_env().get_template(cls.template_path)
        template_args = template_args or {}
        template_args.update({'snippet': snippet})
        return template.render(**template_args)

    @classmethod
    def to_json_type(cls):
        """Return a JSON safe dictionary representing the snippet type"""
        return {
            'id': cls.id,
            'label': cls.label,
            'image_url': cls.get_image_url()
        }
