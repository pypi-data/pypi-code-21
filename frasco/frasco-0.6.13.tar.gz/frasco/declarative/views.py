import yaml
import os
import inspect
from ..views import Blueprint, View, ActionsView
from ..actions import load_grouped_actions
from ..utils import import_string, parse_yaml_frontmatter


def create_blueprint_from_dict(name, spec, import_name="__main__", blueprint_class=Blueprint, **kwargs):
    spec = dict(spec)
    actions = []
    if "actions" in spec:
        actions = load_grouped_actions(spec, pop_keys=True)

    views = []
    if "views" in spec:
        for name, viewspec in spec.pop("views").iteritems():
            views.append(create_view_from_dict(name, viewspec))
    
    bp = blueprint_class(name, import_name, **dict(spec, **kwargs))
    for a in actions:
        bp.add_request_action(a)
    for v in views:
        bp.add_view(v)
    return bp


def create_blueprint_from_file(filename, import_name='__main__', name=None, blueprint_class=Blueprint, **kwargs):
    with open(filename) as f:
        spec = yaml.load(f.read())
    if "name" in spec:
        name = spec.pop("name")
    elif not name:
        name, _ = os.path.splitext(os.path.basename(path))
    if "extends" in spec:
        blueprint_class = import_string(spec.pop("extends"))
    kwargs.setdefault('root_path', os.path.dirname(filename))
    return create_blueprint_from_dict(name, spec, import_name, blueprint_class, **kwargs)


def create_blueprint_views_from_path(bp, path):
    for f in os.listdir(path):
        filename = os.path.join(path, f)
        if f.startswith("_") or os.path.isdir(filename):
            continue
        view_name = os.path.splitext(f)[0]
        template = os.path.join(bp.name, f)
        try:
            view = create_view_from_file(filename, name=view_name, source_template=template)
            bp.add_view(view)
        except DeclarativeViewError:
            pass


def create_blueprint_from_path(path, import_name='__main__', name=None, blueprint_class=Blueprint):
    if not name:
        name, _ = os.path.splitext(os.path.basename(os.path.realpath(path)))
    init_file = os.path.join(path, "__init__.yml")
    kwargs = dict(root_path=path, template_folder='.', template_prefix=name)
    if os.path.exists(init_file):
        bp = create_blueprint_from_file(init_file, import_name, name,
            blueprint_class, **kwargs)
    else:
        bp = blueprint_class(name, import_name, **kwargs)
    create_blueprint_views_from_path(bp, path)
    return bp


def create_view_from_dict(name, spec, template=None, cls=ActionsView):
    """Creates a view from an spec dict (typically, the YAML front-matter).
    """
    kwargs = dict(spec)
    if template is not None:
        kwargs.setdefault("template", template)
    actions = load_grouped_actions(kwargs, pop_keys=True)
    view = cls(name=name, **kwargs)
    if isinstance(view, ActionsView):
        view.actions.extend(actions)
    return view


def create_view_from_file(filename, template=None, name=None, source_template=None, view_class=ActionsView):
    with open(filename) as f:
        source = f.read()

    if not source.startswith("---\n"):
        raise DeclarativeViewError("Declarative views must start with a YAML front-matter")

    basename = os.path.basename(filename)
    spec, source = parse_yaml_frontmatter(source)
    if source is not None and not template:
        template = source_template or basename

    if "name" in spec:
        name = spec.pop("name")
    elif not name:
        name = basename.split(".")[0]
    if "extends" in spec:
        view_class = import_string(spec.pop("extends"))

    return create_view_from_dict(name, spec, template, view_class)


class DeclarativeBlueprint(Blueprint):
    def __new__(cls, path_or_filename, import_name='__main__', name=None):
        if os.path.isdir(path_or_filename):
            return create_blueprint_from_path(path_or_filename, import_name, name)
        return create_blueprint_from_file(path_or_filename, import_name, name)


class DeclarativeView(ActionsView):
    def __new__(cls, filename, template=None, name=None, source_template=None):
        return create_view_from_file(filename, template, name, source_template)


class DeclarativeViewError(Exception):
    pass