from ..views import Blueprint, ActionsView, View
from ..actions import load_grouped_actions, create_action_from_dict
from ..features import FeaturesLoader
from ..services import Service, ServiceActionsView
from ..utils import import_string, find_classes_in_module, RequirementMissingError, deep_update_dict
from .views import create_blueprint_from_file, create_view_from_file, DeclarativeViewError
from collections import OrderedDict
import os
import yaml
import inspect
import re


class FileLoader(object):
    """Generic file loader. Will iterate over directories, load files and
    python modules
    """
    # Filter file by extensions (must be prefixed with a dot).
    # Set to None to not filter
    allowed_extensions = None
    # Whether to exclude files starting with an underscore
    exclude_file_starting_with_dash = True
    # Base python path
    pypath = ""
    # Whether to load dirs recursively
    recursive = False

    def __init__(self, path, pypath=None, recursive=None, exclude_file_starting_with_dash=None):
        self.path = path
        if pypath is not None:
            self.pypath = pypath
        if recursive is not None:
            self.recursive = recursive
        if exclude_file_starting_with_dash:
            self.exclude_file_starting_with_dash = exclude_file_starting_with_dash

    def load(self, app):
        return self.load_dir(app, self.path, "", self.pypath)

    def load_dir(self, app, path, relpath, pypath):
        objects = []
        if not os.path.exists(path):
            return objects
        for filename in os.listdir(path):
            if self.exclude_file_starting_with_dash and filename.startswith("_"):
                continue

            pathname = os.path.join(path, filename)
            (pyname, ext) = os.path.splitext(filename)
            filepypath = (pypath + "." + pyname).lstrip(".")
            filerelpath = os.path.join(relpath, filename)

            if os.path.isdir(pathname) and self.recursive:
                objects.extend(self.load_dir(app, pathname, filerelpath, filepypath))
            elif self.allowed_extensions is None or ext in self.allowed_extensions:
                objects.append(self.load_file(app, pathname, filerelpath, filepypath))

        return filter(lambda c: c is not None, objects)

    def load_file(self, app, filename, relpath, pypath):
        """Loads a file from a directory. If returns None, it will be ignored
        """
        return None


class ActionsLoader(FileLoader):
    """Loads Action classes from the given path.
    Actions can be loaded from python modules or from YAML files.
    In the latter case, a sublass of ActionsAction will be created using
    create_action_from_dict() to create the list of actions
    """
    allowed_extensions = (".yml",)

    def load_file(self, app, pathname, relpath, pypath):
        with open(pathname) as f:
            spec = yaml.load(f.read())
        return create_action_from_dict(pypath.split(".")[-1], spec)


class ViewsLoader(FileLoader):
    """Loads blueprints from python modules found in path and from features.
    Creates views out of yml and html files if they start with a YAML front-matter
    and creates blueprints out of directories
    """
    allowed_extensions = set([".yml", ".html"])
    recursive = True
    default_pkg_name = None
    default_view_class = ActionsView
    extend_feature_blueprints = True

    def __init__(self, path, default_pkg_name=None, default_view_class=None, extend_feature_blueprints=None, **kwargs):
        super(ViewsLoader, self).__init__(path, **kwargs)
        if default_pkg_name is not None:
            self.default_pkg_name = default_pkg_name
        if default_view_class is not None:
            self.default_view_class = default_view_class
        if extend_feature_blueprints is not None:
            self.extend_feature_blueprints = extend_feature_blueprints

    def load(self, app):
        # Features can define a "view_files" property which must
        # be a list where items are tuple or a file extension
        # and a view class. The view class will be used for files
        # matching the extension
        self.view_class_files_map = []
        for f in app.features:
            if hasattr(f, 'view_files') and f.view_files is not None:
                for pattern, cls in f.view_files:
                    self.add_view_file_mapping(pattern, cls)

        return super(ViewsLoader, self).load(app)

    def add_view_file_mapping(self, pattern, cls):
        """Adds a mapping between a file and a view class.
        Pattern can be an extension in the form .EXT or a filename.
        """
        if isinstance(pattern, str):
            if not pattern.endswith("*"):
                _, ext = os.path.splitext(pattern)
                self.allowed_extensions.add(ext)
            pattern = re.compile("^" + re.escape(pattern).replace("\\*", ".+") + "$", re.I)
        self.view_class_files_map.append((pattern, cls))

    def load_dir(self, app, path, relpath, pypath):
        bpname = pypath[len(self.pypath):].lstrip(".").replace(".", "_")
        if not bpname:
            bpname = self.default_pkg_name

        bp = None
        blueprints = []
        # An __init__.yml file can be used to define
        # options of a blueprint
        init_file = os.path.join(path, '__init__.yml')
        if not os.path.exists(init_file):
            init_file = None
        if not bpname and init_file:
            raise DeclarativeViewError('__init__.yml cannot be used in the root of the views folder')
        if bpname and not init_file and self.extend_feature_blueprints:
            # If a feature-provided blueprint of the same name exists,
            # views found in this dir will be added to the existing
            # blueprint
            bp = self.find_feature_blueprint(app, bpname)

        if not bp and bpname:
            # If we are not using an existing blueprint, creates
            # a new blueprint instance
            if init_file:
                bp = create_blueprint_from_file(init_file, name=bpname)
            else:
                bp = Blueprint(bpname, "__main__")
            blueprints.append(bp)

        objects = super(ViewsLoader, self).load_dir(app, path, relpath, pypath)
        for obj in objects:
            if isinstance(obj, Blueprint) or not bp:
                blueprints.append(obj)
            elif isinstance(obj, View):
                bp.add_view(obj)

        return blueprints

    def find_feature_blueprint(self, app, name):
        for feature in app.features:
            if feature.blueprints:
                for bp in feature.blueprints:
                    if isinstance(bp, Blueprint) and bp.name == name:
                        return bp

    def load_file(self, app, pathname, relpath, pypath):
        """Loads a file and creates a View from it. Files are split
        between a YAML front-matter and the content (unless it is a .yml file).
        """
        try:
            view_class = self.get_file_view_cls(relpath)
            return create_view_from_file(pathname, source_template=relpath, view_class=view_class)
        except DeclarativeViewError:
            pass

    def get_file_view_cls(self, filename):
        """Returns the view class associated to a filename
        """
        if filename is None:
            return self.default_view_class
        for pattern, cls in self.view_class_files_map:
            if pattern.match(filename):
                return cls
        return self.default_view_class


class ServicesLoader(FileLoader):
    allowed_extensions = (".yml",)

    def load_file(self, app, pathname, relpath, pypath):
        with open(pathname) as f:
            config = yaml.load(f.read())

        name, _ = os.path.splitext(os.path.basename(pathname))
        service = Service()
        service.name = config.pop('name', name)
        service.url_prefix = config.pop("url_prefix", None)
        service.subdomain = config.pop("subdomain", None)

        for name, spec in config.iteritems():
            service.actions.append(self.create_action_from_spec(name, spec))
            service.views.append(self.create_view_from_spec(name, spec))

        return service

    def create_action_from_spec(self, name, spec):
        return create_action_from_dict(name, spec)

    def create_view_from_spec(self, name, spec):
        actions = load_grouped_actions(spec, pop_keys=True)
        for k in ("as", "requires", "defaults", "default_option"):
            spec.pop(k, None)
        return ServiceActionsView(name, actions=actions, **spec)