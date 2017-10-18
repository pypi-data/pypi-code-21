# -*- coding: utf-8 -*-

# Mathmaker creates automatically maths exercises sheets
# with their answers
# Copyright 2006-2017 Nicolas Hainaux <nh.techn@gmail.com>

# This file is part of Mathmaker.

# Mathmaker is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.

# Mathmaker is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Mathmaker; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

# This module will add a question about the sum of two numbers

from mathmaker.lib.core.root_calculus import Value
from mathmaker.lib.document.content import component
from mathmaker.lib.tools.wording import setup_wording_format_of


class structure(component.structure):

    def __init__(self, nbs_to_use, **kwargs):
        result_fct = kwargs.pop('result_fct', None)
        wording = kwargs.pop('wording', "")
        super().setup("minimal", **kwargs)
        super().setup("numbers", nb=nbs_to_use, **kwargs)
        super().setup("nb_variants", nb=nbs_to_use, **kwargs)
        resultv = Value(result_fct(self.nb1, self.nb2).evaluate())
        self.result = resultv.into_str()
        if ('permute_nb1_nb2_result' in kwargs
            and kwargs['permute_nb1_nb2_result']):
            # __
            self.nb1, self.nb2, self.result = self.result, self.nb1, self.nb2
        self.nb1 = Value(self.nb1)
        self.nb2 = Value(self.nb2)
        self.wording = wording
        setup_wording_format_of(self)
        self.transduration = 9
        if kwargs.get('answer') is None:
            self.js_answer = resultv.jsprinted
        else:
            self.js_answer = kwargs.get('answer')\
                .format(nb1=self.nb1.jsprinted,
                        nb2=self.nb2.jsprinted)
        self.answer_wording = kwargs.get('answer', self.result)
        if isinstance(self.answer_wording, str):
            setup_wording_format_of(self, w_prefix='answer_')
            self.answer_wording = self.answer_wording\
                .format(**self.answer_wording_format)

    def q(self, **kwargs):
        return self.wording.format(**self.wording_format)

    def a(self, **kwargs):
        # This is actually meant for self.preset == 'mental calculation'
        return str(self.answer_wording)

    def js_a(self, **kwargs):
        return [str(self.js_answer)]
