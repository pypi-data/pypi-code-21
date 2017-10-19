# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

from itertools import count

from six import text_type

from cubicweb import _
from cubicweb.dataimport import ucsvreader

from cubes.skos import rdfio
from cubes.skos.rdfio import unicode_with_language as ul


class InvalidLCSVFile(RuntimeError):
    """LCSV input is malformed."""

    def __init__(self, msg, column=None):
        super(InvalidLCSVFile, self).__init__(msg)
        self.column = column


class LCSV2RDF(object):
    """Create RDF triples expressing the data contained in the LCSV stream
    reference : W3C unofficial draft, http://jenit.github.io/linked-csv/
    """

    def __init__(self, stream, delimiter, encoding,
                 uri_generator=None, uri_cls=text_type, default_lang=None):
        """ check stream validity and init attribute"""
        self.source_file = ucsvreader(stream, encoding=encoding, delimiter=delimiter)
        # raise an error value if the line doesn't contains a #
        if uri_generator is None:
            counter = count()

            def uri_generator(val):
                return text_type(next(counter)) + val

        self.uri_gen = uri_generator
        self.prefixes = {'skos': 'http://www.w3.org/2004/02/skos/core#',
                         'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'}
        self.uri_func = lambda string: uri_cls(rdfio.normalize_uri(string, self.prefixes))
        self.uris = {}
        self.no_information_missing = None
        self.prolog = {}
        self.default_lang = default_lang
        header = self.source_file.next()
        try:
            self.prolog_column = header.index('#')
        except ValueError:
            raise InvalidLCSVFile(_("missing prolog column (#)"))
        try:
            self.id_column = header.index('$id')
        except ValueError:
            raise InvalidLCSVFile(_("missing $id column"))

    def triples(self):
        """Yield triples from the lcsv stream"""
        for line in self.source_file:
            # prolog lines must all be at the start of a linked CSV file (dixit draft W3C)
            end_of_prolog = False
            if line[self.prolog_column] and not end_of_prolog:
                self.parse_prolog_line(line)
            else:
                end_of_prolog = True
                self.check_no_information_missing()
                for triple in self.parse_data_line(line):
                    yield triple

    def check_no_information_missing(self):
        """ raise an InvalidLCSVFile error if necessary information are missing"""
        if not self.no_information_missing:
            for column, info in self.prolog.items():
                if not info.get('url', None):
                    raise InvalidLCSVFile(_("missing url info for column %s"), column=str(column))
            self.no_information_missing = True

    def parse_prolog_line(self, line):
        """analyse and store the prolog informations (url, type) described in this line"""
        prolog_type = line[self.prolog_column]
        for index, value in enumerate(line):
            if index != self.prolog_column and value:
                self.prolog.setdefault(index, {})[prolog_type] = value

    def parse_data_line(self, line):
        """analyse the lcsv line and yield the resulting triples"""
        rdftype = self.uri_func(self.prolog[self.id_column]['url'])
        subj = self.uri_func(self.uri_gen(line[self.id_column]))
        yield (subj, self.uri_func('rdf:type'), rdftype)
        self.uris[line[self.id_column]] = subj
        for column_index, column_info in self.prolog.items():
            if column_index != self.id_column and line[column_index]:
                predicate = self.uri_func(column_info['url'])
                content = line[column_index].strip()
                obj = self.type_object(content, column_info)
                yield (subj, predicate, obj)

    def type_object(self, obj, column_info):
        """return the object of the triple considering the value and the prolog infos given"""
        obj_type = column_info.get('type', 'string')
        if obj_type == 'url':
            try:
                obj = self.uris[obj]
            except KeyError:
                obj = self.uri_func(obj)
        elif obj_type == 'string':
            lang = column_info.get('lang', self.default_lang)
            obj = ul(obj, lang) if lang else obj
        elif obj_type == 'integer':
            obj = int(obj)
        return obj
