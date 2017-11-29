MESSAGE_MODULE_MISSING = '{0}:{1}: Cannot find "module" element.'
MESSAGE_IMPORTS_CHILDREN = '{0}:{1}: "imports" element may have only "import" children.'
MESSAGE_IMPORT_ATTRIBUTES = '{0}:{1}: "import" element may have only "path" attribute.'
MESSAGE_PHASES_CHILDREN = '{0}:{1}: "phases" element may have only "phase" children.'
MESSAGE_PHASE_PRIORITY = '{0}:{1}: phase priority must be integer.'
MESSAGE_PHASE_IS_PARALLEL = '{0}:{1}: phase is_parallel must be 0 or 1.'
MESSAGE_PHASE_ATTRIBUTES = '{0}:{1}: "phase" element may have only "name", "priority" or "is-parallel" attributes.'
MESSAGE_PHASE_DUPLICATE = '{0}:{1}: phase "{2}" was already defined.'
MESSAGE_TEMPLATE_TYPE_UNKNOWN = '{0}:{1}: Cannot find type "{2}".'
MESSAGE_TEMPLATE_NAME_MISSING = '{0}:{1}: Template must have name specified.'
MESSAGE_TEMPLATE_PHASE_MISSING = '{0}:{1}: Cannot find phase "{2}".'
MESSAGE_TEMPLATE_PARENT_UNKNOWN = '{0}:{1}: Cannot find parent template "{2}".'
MESSAGE_RESOURCE_HANDLER_UNKNOWN = '{0}:{1}: Cannot find handler "{2}".'
MESSAGE_RESOURCE_NAME_MISSING = '{0}:{1}: Resource must have name specified.'
MESSAGE_RESOURCE_PHASE_MISSING = '{0}:{1}: Cannot find phase "{2}".'
MESSAGE_RESOURCE_PARENT_UNKNOWN = '{0}:{1}: Cannot find parent template "{2}".'


class ParsedTemplate(object):
    def __init__(self, module, type, name, phase, bases, properties, dependencies, source_file, source_line):
        self.module = module
        self.type = type
        self.name = name
        self.phase = phase
        self.bases = bases
        self.properties = properties
        self.dependencies = dependencies
        self.children = []
        self.derivatives = set()
        self.source_file = source_file
        self.source_line = source_line
        self.resolved_resource = None
        self.is_resource = False

    def __repr__(self):
        return '{0}:{1}'.format(self.type, self.name)


class ParsedResource(object):
    def __init__(self, module, type, name, phase, bases, properties, dependencies, source_file, source_line):
        self.module = module
        self.type = type
        self.name = name
        self.phase = phase
        self.bases = bases
        self.properties = properties
        self.dependencies = dependencies
        self.children = []
        self.source_file = source_file
        self.source_line = source_line
        self.resolved_resource = None
        self.is_resource = True

    def __repr__(self):
        return '{0}:{1}'.format(self.type, self.name)


class ParsedPhase(object):
    def __init__(self, name, path, priority, is_parallel, parent):
        self.name = name
        self.path = path
        self.priority = priority
        self.is_parallel = is_parallel
        self.parent = parent
        self.children = []
        self.reference_count = 0

    def __repr__(self):
        return '{0}'.format(self.path)


class ModuleParser(object):
    def __error_print(self, text, *args, **kwargs):
        from ..utility import error_print

        error_print(text, self.__path, *args, **kwargs)

    def __process_string(self, text):
        return self.__environment.from_string(text).render()

    def __get_phase_priority(self, text):
        try:
            return int(self.__process_string(text))
        except Exception as e:
            self.__error_print(MESSAGE_PHASE_PRIORITY, element.sourceline)

    def __get_phase_is_parallel(self, text):
        try:
            return int(self.__process_string(text)) > 0
        except Exception as e:
            self.__error_print(MESSAGE_PHASE_IS_PARALLEL, element.sourceline)

    def __load_import(self, element):
        from lxml.etree import Comment
        from os.path import dirname
        from os.path import join

        if element.tag is Comment:
            return

        if element.tag != 'import':
            self.__error_print(MESSAGE_IMPORTS_CHILDREN, element.sourceline)

        for attribute_name, attribute_value in element.items():
            if attribute_name == 'path':
                context = ModuleParser(self.__project, join(dirname(self.__path), self.__process_string(attribute_value)))
                context.load()
            else:
                self.__error_print(MESSAGE_IMPORT_ATTRIBUTES, element.sourceline)

    def __load_phase(self, element, parent_phase):
        from lxml.etree import Comment

        if element.tag is Comment:
            return

        if element.tag != 'phase':
            self.__error_print(MESSAGE_PHASES_CHILDREN, element.sourceline)

        phase_name = None
        phase_priority = parent_phase.priority if parent_phase else 0
        phase_is_parallel = False

        for attribute_name, attribute_value in element.items():
            if attribute_name == 'name':
                phase_name = self.__process_string(attribute_value)
            elif attribute_name == 'priority':
                phase_priority += self.__get_phase_priority(attribute_value)
            elif attribute_name == 'is-parallel':
                phase_is_parallel = self.__get_phase_is_parallel(attribute_value)
            else:
                self.__error_print(MESSAGE_PHASE_ATTRIBUTES, element.sourceline)

        phase_path = '{0}/{1}'.format(parent_phase.path, phase_name) if parent_phase else phase_name

        if phase_path in self.__project._phase_map:
            self.__error_print(MESSAGE_PHASE_DUPLICATE, element.sourceline, phase_name)

        phase = ParsedPhase(
            phase_name,
            phase_path,
            phase_priority,
            phase_is_parallel,
            parent_phase)

        if parent_phase:
            parent_phase.children.append(phase)
        else:
            self.__project._phases.append(phase)

        self.__project._phase_map[phase_path] = phase

        for child_element in element:
            if not child_element.tag is Comment:
                self.__load_phase(child_element, phase)

    def __load_template(self, element, parent_template):
        from collections import OrderedDict
        from lxml.etree import Comment
        from os.path import basename
        from os.path import splitext

        if element.tag is Comment:
            return

        if element.tag == 'template':
            template_type = None
        else:
            if element.tag not in self.__project._handlers:
                self.__error_print(MESSAGE_TEMPLATE_TYPE_UNKNOWN, element.sourceline, element.tag)

            template_type = element.tag

        template_name = None
        template_base_names = []
        template_bases = []
        template_properties = OrderedDict()
        template_dependency_names = []
        template_dependencies = set()
        phase_name = None

        for attribute_name, attribute_value in element.items():
            if attribute_name == 'name':
                template_name = self.__process_string(attribute_value)
            elif attribute_name == 'phase':
                phase_name = self.__process_string(attribute_value)
            elif attribute_name == 'inherits':
                template_base_names = self.__process_string(attribute_value).split(',')
            elif attribute_name == 'dependencies':
                template_dependency_names = self.__process_string(attribute_value).split(',')
            else:
                template_properties[attribute_name] = attribute_value

        if template_name is None:
            self.__error_print(MESSAGE_TEMPLATE_NAME_MISSING, element.sourceline)

        if phase_name and (phase_name not in self.__project._phase_map):
            self.__error_print(MESSAGE_TEMPLATE_PHASE_MISSING, element.sourceline, phase_name)

        template_phase = self.__project._phase_map.get(phase_name, None)

        if template_phase:
            template_phase.reference_count += 1

        for template_base_name in template_base_names:
            base_module_name, _, base_template_name = template_base_name.partition('/')

            if not base_template_name:
                base_template_name = base_module_name
                base_module_name = self.__module_name

            if base_template_name not in self.__project._templates[base_module_name]:
                self.__error_print(MESSAGE_TEMPLATE_PARENT_UNKNOWN, element.sourceline, template_base_name)

            template_bases.append(self.__project._templates[base_module_name][base_template_name])

        if parent_template is None:
            siblings = self.__project._templates[self.__module_name]

            for template_dependency_name in template_dependency_names:
                if template_dependency_name in siblings:
                    template_dependencies.add(siblings[template_dependency_name])
        else:
            siblings = parent_template.children

        for template_base in template_bases:
            template_dependencies.update(template_base.dependencies)

        template = ParsedTemplate(
            self.__module_name,
            template_type,
            template_name,
            template_phase,
            template_bases,
            template_properties,
            template_dependencies,
            self.__path,
            element.sourceline)

        if parent_template is None:
            self.__project._templates[self.__module_name][template_name] = template
        else:
            parent_template.children.append(template)

        for child_element in element:
            if not child_element.tag is Comment:
                self.__load_template(child_element, template)

    def __load_resource(self, element, parent_resource):
        from collections import OrderedDict
        from lxml.etree import Comment
        from os.path import basename
        from os.path import splitext

        if element.tag is Comment:
            return

        if element.tag == 'resource':
            resource_type = None
        else:
            if element.tag not in self.__handlers:
                self.__error_print(MESSAGE_RESOURCE_HANDLER_UNKNOWN, element.sourceline, element.tag)

            resource_type = element.tag

        resource_name = None
        resource_base_names = []
        resource_bases = []
        resource_properties = OrderedDict()
        resource_dependency_names = []
        resource_dependencies = set()
        phase_name = None

        for attribute_name, attribute_value in element.items():
            if attribute_name == 'name':
                resource_name = self.__process_string(attribute_value)
            elif attribute_name == 'phase':
                phase_name = self.__process_string(attribute_value)
            elif attribute_name == 'inherits':
                resource_base_names = self.__process_string(attribute_value).split(',')
            elif attribute_name == 'dependencies':
                resource_dependency_names = self.__process_string(attribute_value).split(',')
            else:
                resource_properties[attribute_name] = attribute_value

        if resource_name is None:
            self.__error_print(MESSAGE_RESOURCE_NAME_MISSING, element.sourceline)

        if phase_name and (phase_name not in self.__project._phase_map):
            self.__error_print(MESSAGE_RESOURCE_PHASE_MISSING, element.sourceline, phase_name)

        resource_phase = self.__project._phase_map.get(phase_name, None)

        if resource_phase:
            resource_phase.reference_count += 1

        for resource_base_name in resource_base_names:
            base_module_name, _, base_template_name = resource_base_name.partition('/')

            if not base_template_name:
                base_template_name = base_module_name
                base_module_name = self.__module_name

            if base_template_name not in self.__project._templates[base_module_name]:
                self.__error_print(MESSAGE_RESOURCE_PARENT_UNKNOWN, element.sourceline, base_template_name)

            resource_bases.append(self.__project._templates[base_module_name][base_template_name])

        if parent_resource is None:
            siblings = self.__project._resources[self.__module_name]

            for resource_dependency_name in resource_dependency_names:
                if resource_dependency_name in siblings:
                    resource_dependencies.add(siblings[resource_dependency_name])
        else:
            siblings = parent_resource.children

        resource = ParsedResource(
            self.__module_name,
            resource_type,
            resource_name,
            resource_phase,
            resource_bases,
            resource_properties,
            resource_dependencies,
            self.__path,
            element.sourceline)

        for resource_base in resource_bases:
            resource_base.derivatives.add(resource)

        if parent_resource is None:
            self.__project._resources[self.__module_name][resource_name] = resource
        else:
            parent_resource.children.append(resource)

        for child_element in element:
            if not child_element.tag is Comment:
                self.__load_resource(child_element, resource)

    def __init__(self, project, path):
        from jinja2 import FileSystemLoader
        from jinja2.sandbox import SandboxedEnvironment
        from os.path import basename
        from os.path import dirname
        from os.path import splitext
        from os.path import abspath
        from os.path import normpath
        from os.path import normcase
        from os.path import realpath
        from ..utility import PathDict

        path = realpath(normcase(normpath(abspath(path))))

        self.__project = project
        self.__module_name = splitext(basename(path))[0]
        self.__path = path
        self.__loader = FileSystemLoader(dirname(path))
        self.__environment = SandboxedEnvironment(
            trim_blocks=False,
            lstrip_blocks=False,
            keep_trailing_newline=True,
            autoescape=False,
            loader=self.__loader)
        self.__environment.globals.update(self.__project._variables)

    def load(self):
        from lxml.etree import Comment
        from lxml.etree import iterparse

        if self.__path in self.__project._modules:
           return

        self.__project._modules.add(self.__path)

        document = iterparse(self.__path)

        for _ in document:
            pass

        root_element = document.root

        if not root_element.tag == 'module':
            self.__error_print(MESSAGE_MODULE_MISSING, import_element.sourceline)

        for group_element in root_element:
            if group_element.tag is Comment:
                pass
            elif group_element.tag == 'imports':
                for import_element in group_element:
                    self.__load_import(import_element)
            elif group_element.tag == 'phases':
                for phase_element in group_element:
                    self.__load_phase(phase_element, None)
            elif group_element.tag == 'templates':
                for template_element in group_element:
                    self.__load_template(template_element, None)
            elif group_element.tag == 'resources':
                for resource_element in group_element:
                    self.__load_resource(resource_element, None)


class ProjectParser(object):
    def __fixup_phase_references(self, phase):
        for child in phase.children:
            self.__fixup_phase_references(child)
            phase.reference_count += child.reference_count

    def __fixup_phases(self):
        self._phases = sorted(self._phases, key=lambda phase: phase.priority)

        for phase in self._phases:
            self.__fixup_phase_references(phase)

    def __init__(self, handlers, variables):
        from ..utility import PathDict

        self._handlers = handlers
        self._variables = variables
        self._templates = PathDict()
        self._resources = PathDict()
        self._phases = []
        self._phase_map = {}
        self._modules = set()

    def load_root_module(self, path):
        context = ModuleParser(self, path)
        context.load()
        self.__fixup_phases()

    @property
    def resources(self):
        return self._resources.dump_flat()

    @property
    def phases(self):
        return self._phases


class OptionParser(object):
    def __init__(self):
        from ..utility import PathDict

        self.__values = PathDict()

    def add(self, text):
        if text.startswith('@'):
            from configparser import ConfigParser
            from configparser import ExtendedInterpolation
            from os.path import abspath
            from os.path import dirname

            path = text[1:]
            config = ConfigParser(interpolation=ExtendedInterpolation())
            config.add_section('liform')
            config.set('liform', 'base_path', dirname(abspath(path)))
            config.read(path)

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
