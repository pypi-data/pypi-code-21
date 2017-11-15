import os

from html.parser import HTMLParser

from . import config


class InlineStyleSheetsParser (HTMLParser):
    def inline (self, lines):
        self.stylesheet_line = False
        for line in lines:
            self.feed(line)
            if not self.stylesheet_line:
                yield line
            elif self.replacement_data:
                yield '<style>\n'
                for replacement_line in self.replacement_data:
                    yield replacement_line
                yield '</style>\n'
                self.replacement_data = None
                
    def handle_starttag (self, tag, attrs):
        if tag == 'link' and ('rel', 'stylesheet') in attrs:
            self.stylesheet_line = True
            for attr in attrs:
                if attr[0] == 'href':
                    self.replacement_data = open(os.path.join(config.template_path, attr[1])).readlines()
        else:
            self.stylesheet_line = False


def parse_html_template (template_file):
    with open(
        os.path.join(config.template_path, template_file), encoding='utf-8'
        ) as template:
        template_lines = template.readlines()

    parser = InlineStyleSheetsParser()
    sections = []
    current_section_lines = []
    for line in parser.inline(template_lines):
        if line == '<!-- BREAK -->\n':
            # ignore the line break just before the BREAK line
            if current_section_lines[-1][-2:] == '\r\n':
                current_section_lines[-1] = current_section_lines[-1][:-2]
            else:
                current_section_lines[-1] = current_section_lines[-1][:-1]
            sections.append(''.join(current_section_lines))
            current_section_lines = []
        else:
            current_section_lines.append(line)
    sections.append(''.join(current_section_lines))
    return sections
