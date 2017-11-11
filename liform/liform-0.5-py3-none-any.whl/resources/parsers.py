class ParsedTemplate(object):
    def __init__(self, type, name, phase, bases, properties, source_file, source_line):
        self.type = type
        self.name = name
        self.phase = phase
        self.bases = bases
        self.properties = properties
        self.children = []
        self.source_file = source_file
        self.source_line = source_line


class ParsedResource(object):
    def __init__(self, type, name, phase, bases, properties, source_file, source_line):
        self.type = type
        self.name = name
        self.phase = phase
        self.bases = bases
        self.properties = properties
        self.children = []
        self.source_file = source_file
        self.source_line = source_line


class ParsedPhase(object):
    def __init__(self, name, path, priority, is_parallel, on_complete, parent):
        self.name = name
        self.path = path
        self.priority = priority
        self.is_parallel = is_parallel
        self.on_complete = on_complete
        self.parent = parent
        self.children = []
        self.reference_count = 0


class ModuleParser(object):
    def __process_string(self, text):
        return self.__environment.from_string(text).render()

    def __load_phase(self, path, element, parent_phase):
        from sys import exit
        from sys import stderr

        if element.tag != 'phase':
            print(
                '{0}:{1}: "phases" element may have only "phase" children.'.format(
                    path,
                    element.sourceline),
                file=stderr)
            exit(1)

        phase_name = None
        phase_priority = parent_phase.priority if parent_phase else 0
        phase_is_parallel = False
        phase_on_complete = None

        for attribute_name, attribute_value in element.items():
            if attribute_name == 'name':
                phase_name = self.__process_string(attribute_value)
            elif attribute_name == 'priority':
                try:
                    phase_priority += int(self.__process_string(attribute_value))
                except:
                    print(
                        '{0}:{1}: phase priority must be integer.'.format(
                            path,
                            element.sourceline),
                        file=stderr)
                    exit(1)
            elif attribute_name == 'is-parallel':
                try:
                    phase_is_parallel = int(self.__process_string(attribute_value)) > 0
                except:
                    print(
                        '{0}:{1}: phase is_parallel must be 0 or 1.'.format(
                            path,
                            element.sourceline),
                        file=stderr)
                    exit(1)
            elif attribute_name == 'on-complete':
                phase_on_complete = self.__process_string(attribute_value)
            else:
                print(
                    '{0}:{1}: "phase" element may have only "name", "priority", "is-parallel" attributes.'.format(
                        path,
                        element.sourceline),
                    file=stderr)
                exit(1)

        phase_path = '{0}/{1}'.format(parent_phase.name, phase_name) if parent_phase else phase_name

        if phase_path in self.__phases:
            print(
                '{0}:{1}: phase "{2}" was already defined.'.format(
                    path,
                    element.sourceline,
                    phase_name),
                file=stderr)
            exit(1)

        phase = ParsedPhase(
            phase_name,
            phase_path,
            phase_priority,
            phase_is_parallel,
            phase_on_complete,
            parent_phase)

        if parent_phase:
            parent_phase.children.append(phase)
        else:
            self.__phases.append(phase)

        self.__phase_map[phase_path] = phase

        for child_element in element:
            self.__load_phase(path, child_element, phase)

    def __load_template(self, path, element, parent_template):
        from os.path import basename
        from os.path import splitext
        from sys import exit
        from sys import stderr

        module_name = splitext(basename(path))[0]

        if element.tag == 'template':
            template_type = None
        else:
            if element.tag not in self.__handlers:
                print(
                    '{0}:{1}: Cannot find type "{2}".'.format(
                        path,
                        element.sourceline,
                        element.tag),
                    file=stderr)
                exit(1)

            template_type = element.tag

        template_name = None
        template_base_names = []
        template_bases = []
        template_properties = {}
        phase_name = None

        for attribute_name, attribute_value in element.items():
            if attribute_name == 'name':
                template_name = self.__process_string(attribute_value)
            elif attribute_name == 'phase':
                phase_name = self.__process_string(attribute_value)
            elif attribute_name == 'inherits':
                template_base_names = self.__process_string(attribute_value).split(',')
            else:
                template_properties[attribute_name] = self.__process_string(attribute_value)

        if template_name is None:
            print(
                '{0}:{1}: Template must have name specified.'.format(
                    path,
                    element.sourceline),
                file=stderr)
            exit(1)

        if phase_name and (phase_name not in self.__phase_map):
            print(
                '{0}:{1}: Cannot find phase "{2}".'.format(
                    path,
                    element.sourceline,
                    phase_name),
                file=stderr)
            exit(1)

        template_phase = self.__phase_map.get(phase_name, None)

        if template_phase:
            template_phase.reference_count += 1

        for template_base_name in template_base_names:
            base_module_name, _, base_template_name = template_base_name.partition('/')

            if not base_template_name:
                base_template_name = base_module_name
                base_module_name = module_name

            if base_template_name not in self.__templates[base_module_name]:
                print(
                    '{0}:{1}: Cannot find parent template "{2}".'.format(
                        path,
                        element.sourceline,
                        template_base_name),
                    file=stderr)
                exit(1)
            template_bases.append(self.__templates[base_module_name][base_template_name])

        template = ParsedTemplate(
            template_type,
            template_name,
            template_phase,
            template_bases,
            template_properties,
            path,
            element.sourceline)

        if parent_template is None:
            self.__templates[module_name][template_name] = template
        else:
            parent_template.children.append(template)

        for child_element in element:
            self.__load_template(path, child_element, template)

    def __load_resource(self, path, element, parent_resource):
        from os.path import basename
        from os.path import splitext
        from sys import stderr

        module_name = splitext(basename(path))[0]

        if element.tag == 'resource':
            resource_type = None
        else:
            if element.tag not in self.__handlers:
                print(
                    '{0}:{1}: Cannot find handler "{2}".'.format(
                        path,
                        element.sourceline,
                        element.tag),
                    file=stderr)
                exit(1)

            resource_type = element.tag

        resource_name = None
        resource_base_names = []
        resource_bases = []
        resource_properties = {}
        phase_name = None

        for attribute_name, attribute_value in element.items():
            if attribute_name == 'name':
                resource_name = self.__process_string(attribute_value)
            elif attribute_name == 'phase':
                phase_name = self.__process_string(attribute_value)
            elif attribute_name == 'inherits':
                resource_base_names = self.__process_string(attribute_value).split(',')
            else:
                resource_properties[attribute_name] = self.__process_string(attribute_value)

        if resource_name is None:
            print(
                '{0}:{1}: Resource must have name specified.'.format(
                    path,
                    element.sourceline),
                file=stderr)
            exit(1)

        if phase_name and (phase_name not in self.__phase_map):
            print(
                '{0}:{1}: Cannot find phase "{2}".'.format(
                    path,
                    element.sourceline,
                    phase_name),
                file=stderr)
            exit(1)

        resource_phase = self.__phase_map.get(phase_name, None)

        if resource_phase:
            resource_phase.reference_count += 1

        for resource_base_name in resource_base_names:
            base_module_name, _, base_template_name = resource_base_name.partition('/')

            if not base_template_name:
                base_template_name = base_module_name
                base_module_name = module_name

            if base_template_name not in self.__templates[base_module_name]:
                print(
                    '{0}:{1}: Cannot find parent template "{2}".'.format(
                        path,
                        element.sourceline,
                        base_template_name),
                    file=stderr)
                exit(1)
            resource_bases.append(self.__templates[base_module_name][base_template_name])

        resource = ParsedResource(
            resource_type,
            resource_name,
            resource_phase,
            resource_bases,
            resource_properties,
            path,
            element.sourceline)

        if parent_resource is None:
            self.__resources[module_name][resource_name] = resource
        else:
            parent_resource.children.append(resource)

        for child_element in element:
            self.__load_resource(path, child_element, resource)

    def __fixup_phase_references(self, phase):
        for child in phase.children:
            self.__fixup_phase_references(child)
            phase.reference_count += child.reference_count

    def __fixup_phases(self):
        self.__phases = sorted(self.__phases, key=lambda phases: phases.priority)

        for phase in self.__phases:
            self.__fixup_phase_references(phase)

    def __load_module(self, path):
        from lxml.etree import iterparse
        from os.path import dirname
        from os.path import join
        from sys import exit
        from sys import stderr

        document = iterparse(path)

        for _ in document:
            pass

        root_element = document.root

        if root_element.tag == 'module':
            for group_element in root_element:
                if group_element.tag == 'imports':
                    for import_element in group_element:
                        if import_element.tag != 'import':
                            print(
                                '{0}:{1}: "imports" element may have only "import" children.'.format(
                                    path,
                                    import_element.sourceline),
                                file=stderr)
                            exit(1)

                        for attribute_name, attribute_value in import_element.items():
                            if attribute_name == 'path':
                                self.__load_module(join(dirname(path), self.__process_string(attribute_value)))
                            else:
                                print(
                                    '{0}:{1}: "import" element may have only "path" attribute.'.format(
                                        path,
                                        import_element.sourceline),
                                    file=stderr)
                                exit(1)
                elif group_element.tag == 'phases':
                    for phase_element in group_element:
                        self.__load_phase(path, phase_element, None)
                elif group_element.tag == 'templates':
                    for template_element in group_element:
                        self.__load_template(path, template_element, None)
                elif group_element.tag == 'resources':
                    for resource_element in group_element:
                        self.__load_resource(path, resource_element, None)

        self.__fixup_phases()

    def __init__(self, handlers, variables):
        from ..utility import PathDict

        self.__handlers = handlers
        self.__variables = variables
        self.__templates = PathDict()
        self.__resources = PathDict()
        self.__phases = []
        self.__phase_map = {}
        self.__loader = None
        self.__environment = None

    def load_root_module(self, path):
        from jinja2 import FileSystemLoader
        from jinja2.sandbox import SandboxedEnvironment
        from os.path import dirname

        self.__loader = FileSystemLoader(dirname(path))
        self.__environment = SandboxedEnvironment(
            trim_blocks=False,
            lstrip_blocks=False,
            keep_trailing_newline=True,
            autoescape=False,
            loader=self.__loader)
        self.__environment.globals.update(self.__variables)
        self.__load_module(path)

    @property
    def resources(self):
        return self.__resources.dump_flat()

    @property
    def phases(self):
        return self.__phases


class OptionParser(object):
    def __init__(self):
        from ..utility import PathDict

        self.__values = PathDict()

    def add(self, text):
        if text.startswith('@'):
            from configparser import ConfigParser
            from configparser import ExtendedInterpolation

            config = ConfigParser(interpolation=ExtendedInterpolation())
            config.read(text[1:])

            for section_name in config.sections():
                for option_name in config.options(section_name):
                    self.__values[section_name][option_name] = config.get(section_name, option_name)
        else:
            name, _, value = text.partition('=')
            name = name.strip(' \t')
            value = value.strip(' \t')

            self.__values[name] = value

    @property
    def values(self):
        return self.__values.dump()
