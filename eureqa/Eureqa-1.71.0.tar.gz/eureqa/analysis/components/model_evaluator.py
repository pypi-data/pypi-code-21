# Copyright (c) 2017, Nutonian Inc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the Nutonian Inc nor the
#     names of its contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NUTONIAN INC BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from eureqa.analysis.components.base import _Component
from eureqa.data_source import DataSource
import warnings

class ModelEvaluator(_Component):
    """This component evaluates models against different datasources and
    compares their performance.

    Additional models can be added to this model by calling
    :meth:`add_solution_info`

    For example::

        c = ModelEvaluator(solutions=s.get_solutions(), datasource=d, search=s, solution=s.get_best_solution())
        analysis.create_card(c)



    :param list[Solution] solutions: Solutions to evaluate against the data
    :param Solution solution: Solution to fetch results from for the primary model evaluator

    """

    _component_type_str = 'EVALUATE_MODEL'

    def __init__(self, solutions=None, solution=None,
                 _analysis=None, _component_id=None, _component_type=None,
                 **kwargs): #**kwargs - for backward compatibility
        if isinstance(solution, DataSource):
            # This is backward compatibility hack to support the
            # (self, solutions, datasource, search, solution) calling signature.
            solution = _component_id

            # Only support backwared compatible signature for public params
            # because the internal calls were ported to new signature.
            _analysis = None
            _component_id = None
            _component_type = None

        # Field is required by the backend model
        self._evaluationInfo = []

        if solution is not None:
            self.solution = solution

        if solutions:
            for soln in solutions:
                self.add_solution_info(soln)

        super(ModelEvaluator, self).__init__(_analysis=_analysis, _component_id=_component_id, _component_type=_component_type)


    class SolutionInfo(object):
        """**Do not instantiate directly**. Use :meth:`ModelEvaluator.add_solution_info`
        instead. The solution information for a single model
        evaluation ("tab") on ModelEvaluatorCard.

        :param str body: internal
        :param _Component component: internal

        :var str ~eureqa.analysis_cards.ModelEvaluatorCard.SolutionInfo.datasource_id: ID of the DataSource referenced by this solution-tab
        :var str ~eureqa.analysis_cards.ModelEvaluatorCard.SolutionInfo.search_id: ID of the Search referenced by this solution-tab
        :var str ~eureqa.analysis_cards.ModelEvaluatorCard.SolutionInfo.solution_id: ID of the Solution referenced by this solution-tab
        :var bool ~eureqa.analysis_cards.ModelEvaluatorCard.SolutionInfo.has_target_variable: Whether the datasource contains the target variable

        """

        def __init__(self, component, body):
            """ SolutionInfo init """
            if hasattr(component, "_analysis"):
                self._eureqa = component._analysis._eureqa
            elif hasattr(component, "_eureqa"):
                self._eureqa = component._eureqa
            self._component = component
            self._from_json(body)

        @classmethod
        def _from_solution(cls, component, solution):
            instance = cls(
                component=component,
                body={
                    "datasource_id": solution._datasource_id,
                    "search_id": solution._search_id,
                    "solution_id": solution._id
                })
            return instance

        def _to_json(self):
            self._ensure_target_variable()
            return self._body

        def _from_json(self, body):
            self._body = body

            # Value is computed in Python
            if "hasTargetVariable" in self._body:
                del body["hasTargetVariable"]

        @property
        def solution(self):
            """The Solution that is being explained

            :rtype: Solution
            """
            datasource_id = self._body.get("datasource_id")
            search_id = self._body.get("search_id")
            solution_id = self._body.get("solution_id")
            if datasource_id and search_id and solution_id:
                return self._eureqa._get_solution_by_id(datasource_id, search_id, solution_id)

        @solution.setter
        def solution(self, val):
            self._body["solution_id"] = val._id
            self._body["datasource_id"] = val._datasource_id
            self._body["search_id"] = val._datasource_id
            self._eureqa = val._eureqa
            self._update()

        def _ensure_target_variable(self):
            # If we don't have a cached computed value for this variable,
            # and we have enough fields to compute it,
            # then go compute it.
            if "hasTargetVariable" not in self._body:
                solution = self.solution
                datasource = solution.search.get_data_source()
                target_variable = datasource.get_variable_details(solution.target)
                self._body['hasTargetVariable'] = target_variable is not None and target_variable.distinct_values > 0

        @property
        def has_target_variable(self):
            """Whether the datasource contains the solution's target variable.

            If the datasource contains the target variable, the standard plot of this
            Component may include the raw target-variable data for comparison alongside
            the computed value.

            :return: Whether the datasource contains the target variable
            """
            self._ensure_target_variable()
            return self._body.get('hasTargetVariable')

        @has_target_variable.setter
        def has_target_variable(self, val):
            self._body['hasTargetVariable'] = val
            self._update()

        @property
        def accuracy(self):
            """
            Accuracy of this Solution.  Rendered as a human-readable pretty-printed string.

            :rtype: str
            """
            return self._body.get("accuracy")

        @accuracy.setter
        def accuracy(self, val):
            self._body["accuracy"] = val
            self._update()

        @property
        def is_fetching(self):
            return self._body.get("isFetching")

        @is_fetching.setter
        def is_fetching(self, val):
            self._body["isFetching"] = val
            self._update()

        def _update(self):
            self._component._update()
            self._from_json(self._body)

    def add_solution_info(self, solution, *args):
        """Add a new (non-default) solution and tab to this card.
        Once added, this object will show up in the list returned by `solution_infos`.

        :param Solution solution: Solution associated with the model evaluation.
        """

        if isinstance(solution, DataSource):
            # This is backward compatibility hack to support the
            # (self, datasource, solution) calling signature.
            solution = args[0]

        self._eureqa = solution._eureqa

        solution_info = self.SolutionInfo._from_solution(self, solution)

        if not hasattr(self, "_originalSolutionInfo"):
            # First submission gets added as the original solution info
            self._originalSolutionInfo = solution_info._to_json()
            return

        self._evaluationInfo.append(solution_info._to_json())

        self._eureqa = solution._eureqa
        self._update()

    def clear_solution_infos(self):
        """
        Remove all existing solution infos from the current Component
        """
        del self._originalSolutionInfo
        self._evaluationInfo = []

    @property
    def solution_infos(self):
        """The set of all SolutionInfo objects associated with this card.
        One per solution tab displayed in the UI.
        Note that `solution_infos[0]` is the default card; it may be treated specially by the UI.

        To add a solution, use the "add_solution_info()" method.

        :return: List or tuple of :class:`SolutionInfo` objects
        """
        # Pass in our datasource/search/solution in case they are the same as that of the new SolutionInfo.
        # Saves an RPC round-trip for each if so.
        # SolutionInfo is responsible for figuring out that we passed in the wrong objects and silently ignoring them.
        return tuple(self.SolutionInfo(self, x) for x in
                     (([self._originalSolutionInfo] if hasattr(self, "_originalSolutionInfo") else []) +
                      self._evaluationInfo))
    # No setter.  Mutate the returned SolutionInfo objects or use the "add_solution_info" method.


    @property
    def solution(self):
        """The Solution that is being explained

        :rtype: Solution
        """
        if hasattr(self, "_eureqa"):
            return self._eureqa._get_solution_by_id(self._datasource_id, self._search_id, self._solution_id)

    @solution.setter
    def solution(self, val):
        self._solution_id = val._id
        self._search_id = val._search_id
        self._datasource_id = val._datasource_id
        self._eureqa = val._eureqa
        self._update()

    def _fields(self):
        return super(ModelEvaluator, self)._fields() + [ 'evaluationInfo', 'originalSolutionInfo', 'datasource_id', 'search_id', 'solution_id' ]
