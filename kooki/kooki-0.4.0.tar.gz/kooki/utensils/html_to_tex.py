from markdown.extensions import Extension
from markdown.inlinepatterns import LinkPattern, handleAttributes
from markdown import util
from kooki import DocumentException

import markdown
from html.parser import HTMLParser
from kooki.tools import write_file
from . import Utensil

class HTMLToTeX(Utensil):

    def __init__(self):
        self._parser = HTMLTeXParser()

    def __call__(self, **kwargs):

        if 'content' in kwargs:
            content = kwargs['content']
        else:
            raise DocumentException('HTMLToTeX: argument error in step')

        return {'content': self._parser.convert(content)}


class HTMLTableTeXParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self._content = ''
        self._last_tag = ''

    def convert(self, content):
        self._table = []
        self._line = []
        self.feed(content)

        col_formatting = ''
        if len(self._table) > 0:
            nb_col = len(self._table[0])
            for i in range(0, nb_col-1):
                col_formatting += 'l '
            col_formatting += 'l'

        core = ''
        if len(self._table) > 0:

            for element in self._table[0][:-1]:
                core += '\\textbf{' + element + '} & '
            core += '\\textbf{' + self._table[0][-1] + '}'
            core += ' \\\\  \n'
            core += '\hline \n'

            for line in self._table[1:-1]:
                if len(line) > 0:
                    for element in line[:-1]:
                        core += element + ' & '
                    core += line[-1]
                core += ' \\\\ \n'

            for element in self._table[-1][:-1]:
                core += element + ' & '
            core += self._table[-1][-1]
            core += ' \\\\'

        content = '''
\\def\\arraystretch{1.5}
\\begin{center}
{
\\begin{tabular}{%s}
\hline
%s
\hline
\\end{tabular}
}
\\end{center}
''' % (col_formatting, core)

        return content

    def handle_starttag(self, tag, attrs):
        self._last_tag = tag

    def handle_endtag(self, tag):

        if tag == 'tr':
            self._table.append(self._line)
            self._line = []

    def handle_data(self, data):

        if data != '\n':

            if self._last_tag == 'td':
                self._line.append(data)

            elif self._last_tag == 'th':
                self._line.append(data)

class HTMLTeXParser(HTMLParser):

    start_tag = {
        'h1': '\\section{',
        'h2': '\\subsection{',
        'h3': '\\subsubsection{',
        'h4': '\\paragraph{',
        'h5': '\\paragraph{',
        'h6': '\\subparagraph{',
        'p': '',
        'ul': '\\begin{itemize}',
        'ol': '\\begin{enumerate}',
        'pre': '\\begin{verbatim}\n',
        'li': '\item ',
        'span': '',
        'div': '',
        'code': '\\texttt{',
        'em': '\\emph{',
        'strong': '\\textbf{',
        'dl': '\\begin{description}',
        'dt': '\item [',
        'dd': '',
        'hr': '{\noindent}\hrulefill',
    }

    end_tag = {
        'h1': '}',
        'h2': '}',
        'h3': '}',
        'h4': '}',
        'h5': '}',
        'h6': '}',
        'p': '\n',
        'ul': '\\end{itemize}',
        'ol': '\\end{enumerate}',
        'pre': '\\end{verbatim}\n',
        'li': '',
        'span': '',
        'div': '',
        'code': '}',
        'em': '}',
        'strong': '}',
        'dl': '\\end{description}',
        'dt': ']',
        'dd': '',
        'hr': '',
    }

    def __init__(self):

        HTMLParser.__init__(self)
        self._content = ''
        self._last_opened = []
        self._pre_opened = False
        self._table = ''
        self._table_opened = False
        self._table_parser = HTMLTableTeXParser()

    def convert(self, content):
        self.feed(content)
        return self._content

    def handle_starttag(self, tag, attrs):

        self._last_opened.append(tag)

        if tag == 'pre':
            self._pre_opened = True

        if tag == 'code' and len(self._last_opened) >= 2 and self._last_opened[-2] == 'pre':
            pass

        elif tag == 'table':
            self._table_opened = True
            attrs_formatted = ' '
            for attr in attrs:
                attrs_formatted += '{0}="{1}"'.format(attr[0], attr[1])

            self._table += '<{0}{1}>'.format(tag, attrs_formatted)

        elif tag in HTMLTeXParser.start_tag:
            self._content += HTMLTeXParser.start_tag[tag]

        else:
            attrs_formatted = ' '
            for attr in attrs:
                attrs_formatted += '{0}="{1}"'.format(attr[0], attr[1])

            if self._table_opened:
                self._table += '<{0}{1}>'.format(tag, attrs_formatted)
            else:
                self._content += '<{0}{1}>'.format(tag, attrs_formatted)

    def handle_endtag(self, tag):

        if tag == 'pre':
            self._pre_opened = False

        if tag == 'code' and len(self._last_opened) >= 2 and self._last_opened[-2] == 'pre':
            pass

        elif tag == 'table':
            self._table_opened = False
            self._table += '</{0}>'.format(tag)

            self._content += self._table_parser.convert(self._table)

            self._table = ''

        elif tag in HTMLTeXParser.end_tag:
            self._content += HTMLTeXParser.end_tag[tag]

        else:

            if self._table_opened:
                self._table += '</{0}>'.format(tag)
            else:
                self._content += '</{0}>'.format(tag)

        self._last_opened.pop()

    def handle_data(self, data):

        if not self._pre_opened:
            data = data.replace('_', '\_')

            data = data.replace('É', "\\'E")
            data = data.replace('é', "\\'e")
            data = data.replace('È', '\`e')
            data = data.replace('è', '\`e')
            data = data.replace('Ê', '\^e')
            data = data.replace('ê', '\^e')

            data = data.replace('À', '\`A')
            data = data.replace('à', '\`a')
            data = data.replace('Â', '\^A')
            data = data.replace('â', '\^a')

        if self._table_opened:
            self._table += data
        else:
            self._content += data
