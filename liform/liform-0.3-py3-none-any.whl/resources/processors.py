class ResolvedResource(object):
    def __init__(self, type, name, phase, properties, children):
        self.type = type
        self.name = name
        self.phase = phase
        self.properties = properties
        self.parent = None
        self.children = children
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


class ModuleProcessor(object):
    def __init__(self, handlers):
        self.__handlers = handlers
        self.resources = []

    def __resolve_resource(self, resource):
        from sys import stderr

        type = resource.type
        phase = resource.phase
        properties = {}
        children = []

        for base in resource.bases:
            base_resource = self.__resolve_resource(base)

            if base_resource.type is not None:
                if type is not None:
                    print(
                        '{0}:{1}: "{2}"''s type is overriden.'.format(
                            resource.source_file,
                            resource.source_line,
                            resource.name),
                        file=stderr)
                type = base_resource.type

                if phase is not None:
                    print(
                        '{0}:{1}: "{2}"''s phase is overriden.'.format(
                            resource.source_file,
                            resource.source_line,
                            resource.name),
                        file=stderr)
                phase = base_resource.phase

            properties.update(base_resource.properties)

            for child in base_resource.children:
                children.append(child)

        properties.update(resource.properties)

        for child in resource.children:
            children.append(self.__resolve_resource(child))

        resolved_resource = ResolvedResource(
            type,
            resource.name,
            phase,
            properties,
            children)

        for child in resolved_resource.children:
            child.parent = resolved_resource

        return resolved_resource

    def __update_resource_path(self, parent, resource):
        resource.path = '{0}/{1}/{2}'.format(parent.path, resource.type, resource.name)

        for child in resource.children:
            self.__update_resource_path(resource, child)

    def __update_resource_handler(self, resource):
        resource.handler = self.__handlers[resource.type](resource)

        for child in resource.children:
            self.__update_resource_handler(child)

    def resolve_resources(self, parsed_resources):
        from sys import exit
        from sys import stderr

        for name, parsed_resource in parsed_resources.items():
            resource = self.__resolve_resource(parsed_resource)

            if resource.type is None:
                print(
                    '{0}:{1}: "{2}" does not inherit any typed resource.'.format(
                        parsed_resource.source_file,
                        parsed_resource.source_line,
                        parsed_resource.name),
                    file=stderr)
                exit(1)

            self.resources.append(resource)

        for resource in self.resources:
            resource.path = '{0}/{1}'.format(resource.type, resource.name)

            for child in resource.children:
                self.__update_resource_path(resource, child)

        for resource in self.resources:
            self.__update_resource_handler(resource)

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
