class ResolvedResource(object):
    def __init__(self, type, name, phase, properties, children, source_file, source_line):
        self.type = type
        self.name = name
        self.phase = phase
        self.properties = properties
        self.parent = None
        self.children = children
        self.source_file = source_file
        self.source_line = source_line
        self.handler = None
        self.id = None
        self.ipv4 = None
        self.ipv6 = None
        self.state = 0

    def get_ancestor(self, type_pattern):
        from re import compile as re_compile

        pattern = re_compile(type_pattern)
        parent = self

        while parent and not pattern.search(parent.type):
            parent = parent.parent

        return parent

    @property
    def state_text(self):
        return 'Valid' if self.state else 'Error'


class ProjectProcessor(object):
    def __init__(self, handlers, variables):
        self.__handlers = handlers
        self.__variables = variables
        self.resources = []

    def __flatten_resource(self, parsed_resource):
        from collections import OrderedDict
        from ..utility import error_print
        from ..utility import warning_print

        type = parsed_resource.type
        phase = parsed_resource.phase
        properties = OrderedDict()
        children = []

        for base in parsed_resource.bases:
            base_template = self.__flatten_resource(base)

            if base_template.type is not None:
                if type is not None:
                    warning_print(
                        '{0}:{1}: "{2}"''s type is overriden.',
                        parsed_resource.source_file,
                        parsed_resource.source_line,
                        parsed_resource.name)
                type = base_template.type

                if phase is not None:
                    warning_print(
                        '{0}:{1}: "{2}"''s phase is overriden.',
                        parsed_resource.source_file,
                        parsed_resource.source_line,
                        parsed_resource.name)
                phase = base_template.phase

            properties.update(base_template.properties)

            for child in base_template.children:
                children.append(child)

        properties.update(parsed_resource.properties)

        if type is None:
            error_print(
                '{0}:{1}: "{2}" does not inherit any typed resource.',
                parsed_resource.source_file,
                parsed_resource.source_line,
                parsed_resource.name)

        resolved_resource = ResolvedResource(
            type,
            parsed_resource.name,
            phase,
            properties,
            children,
            parsed_resource.source_file,
            parsed_resource.source_line)

        resolved_resource.handler = self.__handlers[resolved_resource.type](resolved_resource)

        for child in parsed_resource.children:
            children.append(self.__flatten_resource(child))

        return resolved_resource

    def __flatten_resources(self, parsed_resources):
        for name, parsed_resource in parsed_resources.items():
            resource = self.__flatten_resource(parsed_resource)

            self.resources.append(resource)

    def __resolve_resource(self, resolved_resource, resolved_parent):
        from collections import OrderedDict
        from jinja2 import FileSystemLoader
        from jinja2.sandbox import SandboxedEnvironment
        from os.path import dirname
        from ..utility import warning_print

        base_path = dirname(resolved_resource.source_file)
        loader = FileSystemLoader(base_path)
        environment = SandboxedEnvironment(
            trim_blocks=False,
            lstrip_blocks=False,
            keep_trailing_newline=True,
            autoescape=False,
            loader=loader)
        environment.globals.update(self.__variables)
        parent_properties = resolved_parent.properties if resolved_parent else {}
        this_properties = OrderedDict()

        for name, value in resolved_resource.properties.items():
            this_properties[name] = environment.from_string(value).render({
                'this': this_properties,
                'parent': parent_properties})

        resolved_resource.properties = this_properties
        resolved_resource.parent = resolved_parent

        if resolved_parent:
            resolved_resource.path = '{0}/{1}/{2}'.format(resolved_parent.path, resolved_resource.type, resolved_resource.name)
        else:
            resolved_resource.path = '{0}/{1}'.format(resolved_resource.type, resolved_resource.name)

        for child in resolved_resource.children:
            self.__resolve_resource(child, resolved_resource)

    def __resolve_resources(self):
        from ..utility import error_print

        for resource in self.resources:
            self.__resolve_resource(resource, None)

    def resolve_resources(self, parsed_resources):
        self.__flatten_resources(parsed_resources)
        self.__resolve_resources()

    def __select_state(self, state_database, resource):
        state = state_database.get(resource.path)

        resource.id = state.id
        resource.code = state.code
        resource.ipv4 = state.ipv4
        resource.ipv6 = state.ipv6
        resource.state = state.state

        for child in resource.children:
            self.__select_state(state_database, child)

    def select_state(self, state_database):
        for resource in self.resources:
            self.__select_state(state_database, resource)

    def __update_state(self, state_database, resource):
        state_database.set(
            resource.path,
            resource.type,
            resource.name,
            resource.id,
            resource.name,
            resource.ipv4,
            resource.ipv6,
            resource.state)

        for child in resource.children:
            self.__update_state(state_database, child)

    def update_state(self, state_database):
        for resource in self.resources:
            self.__update_state(state_database, resource)
