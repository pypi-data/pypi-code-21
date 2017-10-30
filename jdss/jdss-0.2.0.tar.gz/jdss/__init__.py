import os


class SummaryReportLeafBase:
    def __init__(self):
        self._start = []
        self._end = []

    def _generate_start(self):
        report = ''
        for r in self._start:
            report += r
        return report

    def _generate_end(self):
        report = ''
        end = list(self._end)
        end.reverse()
        for r in end:
            report += r
        return report

    def generate(self):
        report = ''
        report += self._generate_start()
        report += self._generate_end()
        return report


class SummaryReportNodeBase(SummaryReportLeafBase):
    def __init__(self):
        super().__init__()
        self._children = []

    def generate(self):
        report = ''
        report += self._generate_start()
        for child in self._children:
            report += child.generate()
        report += self._generate_end()
        return report


class SummaryReportSection(SummaryReportNodeBase):
    def __init__(self):
        super().__init__()
        self._start.append('<section name="" fontcolor="">')
        self._end.append('</section>')

    def add_tabs(self):
        tabs = SummaryReportTabs()
        self._children.append(tabs)
        return tabs

    def add_table(self):
        table = SummaryReportTable()
        self._children.append(table)
        return table

    def add_accordion(self, name):
        accordion = SummaryReportAccordion(name)
        self._children.append(accordion)
        return accordion


class SummaryReportAccordion(SummaryReportNodeBase):
    def __init__(self, name):
        super().__init__()
        self._start.append('<accordion name="{}">'.format(name))
        self._end.append('</accordion>')

    def add_table(self):
        table = SummaryReportTable()
        self._children.append(table)
        return table


class SummaryReportTabs(SummaryReportNodeBase):
    def __init__(self):
        super().__init__()
        self._start.append('<tabs>')
        self._end.append('</tabs>')

    def add_tab(self, name):
        tab = SummaryReportTab(name)
        self._children.append(tab)
        return tab


class SummaryReportTab(SummaryReportNodeBase):
    def __init__(self, name):
        super().__init__()
        self._start.append('<tab name="{}">'.format(name))
        self._end.append('</tab>')

    def add_field(self, name, value):
        field = SummaryReportField(name, value)
        self._children.append(field)
        return field

    def add_table(self):
        table = SummaryReportTable()
        self._children.append(table)
        return table


class SummaryReportField(SummaryReportLeafBase):
    def __init__(self, name, value):
        super().__init__()
        self._start.append('<field name="{}">{}'.format(name, value))
        self._end.append('</field>')


class SummaryReportTable(SummaryReportNodeBase):
    def __init__(self):
        super().__init__()
        self._start.append('<table sorttable="yes">')
        self._end.append('</table>')

    def add_row(self):
        row = SummaryReportRow()
        self._children.append(row)
        return row


class SummaryReportRow(SummaryReportNodeBase):
    def __init__(self):
        super().__init__()
        self._start.append('<tr>')
        self._end.append('</tr>')

    def add_cell(self, text, link=None):
        cell = SummaryReportCell(text, link)
        self._children.append(cell)
        return cell


class SummaryReportCell(SummaryReportLeafBase):
    def __init__(self, text, link=None):
        super().__init__()
        if link is None:
            self._start.append('<td value="{}" align="center"/>'.format(text))
        else:
            self._start.append('<td value="{}" align="center" href="{}"/>'.format(text, link))


class SummaryReport(SummaryReportNodeBase):
    def __init__(self):
        super().__init__()

    def add_section(self):
        section = SummaryReportSection()
        self._children.append(section)
        return section

    def write(self, file_name, directory):
        with open(os.path.join(directory, file_name), 'w') as file:
            file.write(self.generate())
