#!/usr/bin/env python3
# encoding: UTF-8

# This file is part of turberfield.
#
# Turberfield is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Turberfield is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with turberfield.  If not, see <http://www.gnu.org/licenses/>.


import argparse
from collections import defaultdict
from collections import namedtuple
from collections import OrderedDict
import logging
import operator
import os.path
import re
import sys

from turberfield.dialogue.directives import Entity as EntityDirective
from turberfield.dialogue.directives import FX as FXDirective
from turberfield.dialogue.directives import Pathfinder
from turberfield.dialogue.directives import Property as PropertyDirective
from turberfield.dialogue.directives import Memory as MemoryDirective
from turberfield.utils.assembly import Assembly
from turberfield.utils.misc import group_by_type

import pkg_resources
import docutils


class Model(docutils.nodes.GenericNodeVisitor):
    """This class registers the necessary extensions to the docutils document model.

    It also defines the types which are returned on iterating over a scene script file.

    """

    Shot = namedtuple("Shot", ["name", "scene", "items"])
    Property = namedtuple("Property", ["entity", "object", "attr", "val"])
    Audio = namedtuple("Audio", ["package", "resource", "offset", "duration", "loop"])
    Memory = namedtuple("Memory", ["subject", "object", "state", "text", "html"])
    Line = namedtuple("Line", ["persona", "text", "html"])

    def __init__(self, fP, document):
        super().__init__(document)
        self.fP = fP
        self.optional = tuple(
            i.__name__ for i in (
                EntityDirective.Declaration, MemoryDirective.Definition,
                PropertyDirective.Getter, PropertyDirective.Setter,
                FXDirective.Cue
            )
        )
        self.log = logging.getLogger(
            "turberfield.dialogue.{0}".format(os.path.basename(self.fP))
        )
        self.section_level = 0
        self.scenes = []
        self.shots = []
        self.speaker = None
        self.memory = None
        self.metadata = []

    def __iter__(self):
        for shot in self.shots:
            for item in shot.items:
                yield shot, item


    def get_entity(self, ref):
        return next((
            entity
            for entity in self.document.citations
            if ref and ref.lower() in entity.attributes["names"]),
            None)

    def substitute_property(self, matchObj):
        try:
            defn = self.document.substitution_defs[matchObj.group(1)]
            getter = next(
                i for i in defn.children
                if isinstance(i, PropertyDirective.Getter)
            )
            ref, dot, attr = getter["arguments"][0].partition(".")
            entity = self.get_entity(ref)
            rv = str(operator.attrgetter(attr)(entity.persona))
        except (AttributeError, KeyError, IndexError, StopIteration) as e:
            self.log.warning("Argument has bad substitution ref {0}".format(matchObj.group(1)))
            rv = ""
        return rv

    def default_visit(self, node):
        self.log.debug(node)

    def default_departure(self, node):
        pass

    def visit_section(self, node):
        self.section_level += 1

    def depart_field(self, node):
        if self.section_level == 0:
            data = tuple(
                ("\n".join([" ".join(getattr(p, "text", [p.rawsource])) for p in f.children])
                 if f.tagname == "field_body" else f.rawsource).strip()
                for f in node.children
            )
            if data not in self.metadata:
                self.log.debug(data)
                self.metadata.append(data)

    def depart_section(self, node):
        self.section_level -= 1

    def visit_Setter(self, node):
        ref, attr = node["arguments"][0].split(".")
        entity = self.get_entity(ref)
        s = re.compile("\|(\w+)\|").sub(self.substitute_property, node["arguments"][1])
        val = int(s) if s.isdigit() else node.string_import(s)
        self.shots[-1].items.append(Model.Property(self.speaker, entity.persona, attr, val))

    def visit_Definition(self, node):
        state = node.string_import(node["arguments"][0])
        subj = self.get_entity(node["options"].get("subject"))
        obj = self.get_entity(node["options"].get("object"))
        self.memory = Model.Memory(
            subj and subj.persona, obj and obj.persona, state, None, None
        )

    def visit_Cue(self, node):
        pkg = node["arguments"][0]
        rsrc = re.compile("\|(\w+)\|").sub(self.substitute_property, node["arguments"][1])
        offset = node["options"].get("offset")
        duration = node["options"].get("duration")
        loop = node["options"].get("loop")
        item = Model.Audio(pkg, rsrc, offset, duration, loop)
        self.shots[-1].items.append(item)

    def visit_title(self, node):
        self.log.debug(self.section_level)
        if isinstance(node.parent, docutils.nodes.section):
            if self.section_level == 1:
                self.scenes.append(node.parent.attributes["names"][0])
            elif self.section_level == 2:
                self.shots.append(Model.Shot(
                    node.parent.attributes["names"][0],
                    self.scenes[-1],
                    []))

    def visit_paragraph(self, node):
        text = []
        html = []
        for c in node.children:
            if isinstance(c, docutils.nodes.substitution_reference):
                try:
                    defn = self.document.substitution_defs[c.attributes["refname"]]
                except KeyError:
                    self.log.warning(
                        "Bad substitution ref before line {0}: {1.rawsource}".format(
                            node.line, c
                        )
                    )
                    raise
                for tgt in defn.children:
                    if isinstance(tgt, PropertyDirective.Getter):
                        ref, dot, attr = tgt["arguments"][0].partition(".")
                        entity = self.get_entity(ref)
                        if entity is None:
                            obj = Pathfinder.string_import(
                                tgt["arguments"][0], relative=False, sep="."
                            )
                            text.append(str(obj))
                            html.append(str(obj))
                        elif getattr(entity, "persona", None) is not None:
                            val = operator.attrgetter(attr)(entity.persona)
                            text.append(val)
                            html.append('<span class="ref">{0}</span>'.format(val))
            elif isinstance(c, docutils.nodes.strong):
                text.append(c.rawsource)
                html.append(
                    '<strong class="text">{0}</strong>'.format(c.rawsource.replace("*", ""))
                )
            elif isinstance(c, docutils.nodes.Text):
                text.append(c.rawsource)
                html.append('<span class="text">{0}</span>'.format(c.rawsource))

        if self.memory:
            self.shots[-1].items.append(
                self.memory._replace(text=" ".join(text), html="\n".join(html))
            )
            self.memory = None
        elif self.section_level == 0:
            node.text = text
            node.html = html
        elif (text or html) and self.section_level == 2:
            self.shots[-1].items.append(
                Model.Line(self.speaker, " ".join(text), "\n".join(html))
            )

    def visit_citation_reference(self, node):
        entity = self.get_entity(node.attributes["refname"])
        self.speaker = entity.persona

class SceneScript:
    """Gives access to a Turberfield scene script (.rst) file.

    This class allows discovery and classification of scene files prior to loading
    them in memory.

    Once loaded, it allows entity selection based on the role definitions in the file.
    Casting a selection permits the script to be iterated as a sequence of dialogue items.

    """

    Folder = namedtuple("Folder", ["pkg", "description", "metadata", "paths", "interludes"])

    log = logging.getLogger("turberfield.dialogue.model.scenescript")

    settings = argparse.Namespace(
        character_level_inline_markup=False,
        debug=False, error_encoding="utf-8",
        error_encoding_error_handler="backslashreplace", halt_level=4,
        auto_id_prefix="", id_prefix="", language_code="en",
        pep_references=1,
        report_level=2, rfc_references=1,
        strict_visitor=False, tab_width=4,
        warning_stream=sys.stderr
    )

    docutils.parsers.rst.directives.register_directive(
        "entity", EntityDirective
    )

    docutils.parsers.rst.directives.register_directive(
        "property", PropertyDirective
    )

    docutils.parsers.rst.directives.register_directive(
        "fx", FXDirective
    )

    docutils.parsers.rst.directives.register_directive(
        "memory", MemoryDirective
    )

    @classmethod
    def scripts(cls, pkg, metadata, paths=[], **kwargs):
        """This class method is the preferred way to create SceneScript objects.

        :param str pkg: The dotted name of the package containing the scripts.
        :param metadata: A mapping or data object. This parameter permits searching among
            scripts against particular criteria. Its use is application specific.
        :param list(str) paths: A sequence of file paths to the scripts relative to the package.

        You can satisfy all parameter requirements by passing in a
        :py:class:`~turberfield.dialogue.model.SceneScript.Folder` object
        like this::

            SceneScript.scripts(**folder._asdict())

        The method generates a sequence of
        :py:class:`~turberfield.dialogue.model.SceneScript` objects.
        """
        for path in paths:
            try:
                fP = pkg_resources.resource_filename(pkg, path)
            except ImportError:
                cls.log.warning(
                    "No package called {}".format(pkg)
                )
            else:
                if not os.path.isfile(fP):
                    cls.log.warning(
                        "No script file at {}".format(os.path.join(*pkg.split(".") + [path]))
                    )
                else:
                    yield cls(fP, metadata)


    @staticmethod
    def read(text, name=None):
        """Read a block of text as a docutils document.

        :param str text: Scene script text.
        :param str name: An optional name for the document.
        :return: A document object.

        """
        doc = docutils.utils.new_document(name, SceneScript.settings)
        parser = docutils.parsers.rst.Parser()
        parser.parse(text, doc)
        return doc

    def __init__(self, fP, metadata=None, doc=None):
        self.fP = fP
        self.metadata = metadata
        self.doc = doc

    def __enter__(self):
        with open(self.fP, "r") as script:
            self.doc = self.read(script.read())
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def select(self, personae, relative=False, roles=1):
        """Select a persona for each entity declared in the scene.

        :param personae: A sequence of Personae.
        :param bool relative: Affects imports from namespace packages.
            Used for testing only.
        :param int roles: The maximum number of roles allocated to each persona.
        :return: An OrderedDict of {Entity: Persona}.

        """

        def constrained(entity):
            return (
                len(entity["options"].get("types", [])) +
                len(entity["options"].get("states", []))
            )

        rv = OrderedDict()
        performing = defaultdict(set)
        pool = list(personae)
        self.log.debug(pool)
        entities = OrderedDict([
            ("".join(entity.attributes["names"]), entity)
            for entity in sorted(
                group_by_type(self.doc)[EntityDirective.Declaration],
                key=constrained,
                reverse=True
            )
        ])
        for e in entities.values():
            types = tuple(filter(
                None,
                (e.string_import(t, relative)
                 for t in e["options"].get("types", []))
            ))
            states = tuple(filter(
                None,
                (int(t) if t.isdigit() else e.string_import(t, relative)
                 for t in e["options"].get("states", []))
            ))
            otherRoles = {i.lower() for i in e["options"].get("roles", [])}
            typ = types or object
            persona = next(
                (i for i in pool
                 if isinstance(i, typ) and
                 all(str(i.get_state(type(s))).startswith(str(s)) for s in states) and
                 (performing[i].issubset(otherRoles) or not otherRoles)),
                None
            )
            rv[e] = persona
            performing[persona].update(set(e.attributes["names"]))

            if not otherRoles or list(rv.values()).count(persona) == roles:
                try:
                    pool.remove(persona)
                except ValueError:
                    self.log.debug(
                        "No persona for type {0} and states {1} with {2} {3}.".format(
                            typ, states, roles, "role" if roles == 1 else "roles"
                        )
                    )
        return rv

    def cast(self, mapping):
        """Allocate the scene script a cast of personae for each of its entities.

        :param mapping: A dictionary of {Entity, Persona}
        :return: The SceneScript object.

        """
        # See 'citation' method in
        # http://docutils.sourceforge.net/docutils/parsers/rst/states.py
        for c, p in mapping.items():
            self.doc.note_citation(c)
            self.doc.note_explicit_target(c, c)
            c.persona = p
            self.log.debug("{0} to be played by {1}".format(
                c["names"][0].capitalize(), p)
            )
        return self

    def run(self):
        """Parse the script file.

        :rtype: :py:class:`~turberfield.dialogue.model.Model`
        """
        model = Model(self.fP, self.doc)
        self.doc.walkabout(model)
        return model

Assembly.register(Model.Audio, Model.Line, Model.Memory, Model.Property)
