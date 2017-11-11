def _get_attr(resource, attr):
    value = getattr(resource, attr)

    if value is None:
        return ''

    return str(value)


class DisplayCommandBase(object):
    def __init__(self, resources, columns):
        self._resources = resources
        self._columns = columns


class DisplayTextCommandBase(DisplayCommandBase):
    def __init__(self, resources, columns, indent):
        super().__init__(resources, columns)
        self._indent = indent
        self._counter = 0

    def _measure_item(self, resource, offset):
        pass

    def _process_length(self):
        pass

    def _process_header(self):
        pass

    def _process_footer(self):
        pass

    def _process_element(self, resource, offset):
        for child in resource.children:
            if child._opted_in:
                self._process_element(child, offset + self._indent)

    def _process_separator(self):
        pass

    def run(self):
        for resource in self._resources:
            self._measure_item(resource, 0)

        self._process_length()
        self._process_header()

        is_first = True

        for resource in self._resources:
            if not is_first and (self._counter > 0):
                self._process_separator()
                self._counter = 0

            is_first = False
            self._process_element(resource, 0)

            if resource._opted_in:
                self._counter += 1

        self._process_footer()


class DisplayTextCommand(DisplayTextCommandBase):
    def __init__(self, resources, columns):
        from collections import defaultdict

        super().__init__(resources, columns, 2 if 'name' in columns else 0)
        self._max_column_len = defaultdict(int)

        for attr, name in self._columns.items():
            self._max_column_len[attr] = len(name)

        self._header_format = ''
        self._separator_format = ''
        self._element_format = ''
        self._footer_format = ''

    def _measure_item(self, resource, offset):
        if resource._opted_in:
            for attr, name in self._columns.items():
                if attr in ('name', 'type',):
                    self._max_column_len[attr] = max(
                        self._max_column_len[attr],
                        offset + len(_get_attr(resource, attr)))
                    self._max_column_len[attr] = max(
                        self._max_column_len[attr],
                        offset + len(name))
                else:
                    self._max_column_len[attr] = max(
                        self._max_column_len[attr],
                        len(_get_attr(resource, attr)))
                    self._max_column_len[attr] = max(
                        self._max_column_len[attr],
                        len(name))

        for child in resource.children:
            self._measure_item(child, offset + self._indent)

    def _process_length(self):
        self._header_format = ''

        for attr, name in self._columns.items():
            self._header_format += '╦' if self._header_format else '  ╔'
            self._header_format += '═{:═<' + str(self._max_column_len[attr]) + '}═'

        self._header_format += '╗'
        self._separator_format = ''

        for attr, name in self._columns.items():
            self._separator_format += '╬' if self._separator_format else '  ╠'
            self._separator_format += '═{:═<' + str(self._max_column_len[attr]) + '}═'

        self._separator_format += '╣'
        self._footer_format = ''

        for attr, name in self._columns.items():
            self._footer_format += '╩' if self._footer_format else '  ╚'
            self._footer_format += '═' + '═' * self._max_column_len[attr] + '═'

        self._footer_format += '╝'
        self._element_format = ''

        for attr, name in self._columns.items():
            self._element_format += '║' if self._element_format else '  ║'
            self._element_format += ' {:<' + str(self._max_column_len[attr]) + '} '

        self._element_format += '║'

    def _process_header(self):
        from ..utility import sync_print

        sync_print(self._header_format.format(*list(self._columns.values())))

    def _process_footer(self):
        from ..utility import sync_print

        sync_print(self._footer_format)

    def _process_element(self, resource, offset):
        from ..utility import sync_print

        if resource._opted_in:
            values = [
                (' ' * offset if attr in ('name', 'type') else '') + _get_attr(resource, attr)
                for attr, name in self._columns.items()]

            sync_print(self._element_format.format(*values))

        super()._process_element(resource, offset)

    def _process_separator(self):
        from ..utility import sync_print

        sync_print(self._separator_format.format(*list(self._columns.values())))


class DisplayCsvCommand(DisplayTextCommandBase):
    def __init__(self, resources, columns):
        from collections import defaultdict

        super().__init__(resources, columns, 0)
        self._max_column_len = defaultdict(int)

        for attr, name in self._columns.items():
            self._max_column_len[attr] = len(name)

        self._element_format = ''

    def _measure_item(self, resource, offset):
        pass

    def _process_length(self):
        self._element_format = ''

        for attr, name in self._columns.items():
            self._element_format += ',' if self._element_format else ''
            self._element_format += '{}'

    def _process_element(self, resource, offset):
        from ..utility import sync_print

        if resource._opted_in:
            columns = [_get_attr(resource, attr) for attr, name in self._columns.items()]
            sync_print(self._element_format.format(*columns))

        super()._process_element(resource, offset)


class DisplayJsonCommand(DisplayCommandBase):
    def _walk(self, resource):
        if not (resource._opted_in or resource._child_opted_in):
            return None

        if resource._opted_in:
            this_object = {name: _get_attr(resource, attr) for attr, name in self._columns.items()}
        else:
            this_object = {'Path': resource.path}

        children_objects = []

        for child in resource.children:
            child_object = self._walk(child)

            if child_object:
                children_objects.append(child_object)

        if children_objects:
            this_object['Children'] = children_objects

        return this_object

    def run(self):
        from json import dumps
        from ..utility import sync_print

        result = []

        for resource in self._resources:
            resource_object = self._walk(resource)

            if resource_object:
                result.append(resource_object)

        sync_print(dumps(result, indent=2))
