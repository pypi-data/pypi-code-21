from pandas import DataFrame  # type: ignore
from typing import Any, Dict, List, Tuple  # NOQA
import copy

# This is imported from `future` so its type checking is wonky
import itertools
import matplotlib.pyplot as plt  # type: ignore
import numpy as np  # type: ignore
import pandas as pd  # type: ignore
import six

DEFAULT_LIMIT = 10


class PopulationModelExperimental(object):
    """A collection of less nailed-down APIs on PopulationModels.

    You should generally not create one of these yourself. Instead, get one via
    a PopulationModel's `.experimental` property.
    """

    def __init__(self, population_model):
        self._popmod = population_model

    def unlikely_values(
            self,
            target_column,  # type: str
            given_columns=None,  # type: List[str]
            num_outliers=10,  # type: int
            num_relevant=0,  # type: int
            rowids=None,  # type: List[int]
            select=None,  # type: List[str]
            probability_column='p'  # type: str
    ):  # type: (...) -> DataFrame
        """
        Find the `num_outliers` rows whose value in `target_column` is least
        likely given the values in the rest of its columns.

        Args:
            target_column: The column in which to find outliers.
            given_columns: The columns on which to condition the logpdf call
                when computing probability. Defaults to all modeled columns
                other than target_column. It is an error to include
                `target_column` in this list.
            num_outliers: The number of outliers to return.
            select: A list of additional columns to select and return in the
                data frame.
            num_relevant: A number of columns to include in addition to the
                select columns, chosen by their column_relevance to target.
            rowids: The rowids to restrict the search to. If not specified
                looks for outliers across all rows.
            probability_column: The name of the column in which to return the
                probability.
        """
        if num_relevant > 0:
            # relevant_columns will return the target, so +1.
            relevant = self._popmod.relevant_columns(target_column,
                                                     num_relevant + 1)
            relevant = list(relevant.column)
            relevant.remove(target_column)
            select = (select or []) + relevant
        df = self._popmod.row_probability(
            targets=[target_column], given_columns=given_columns,
            rowids=rowids, probability_column=probability_column,
            select=select)
        df.sort_values(by=probability_column, ascending=True, inplace=True)
        df = df[0:num_outliers]
        return df

    def column_value_probabilities(
            self,
            target_column,  # type: str
            given=None,  # type: Dict[str, Any]
            probability_column='p'  # type: str
    ):  # type: (...) -> DataFrame
        """Return the probability of the possible values in a column.

        Returns a data frame containing two columns: `target_column` whose
        values correspond to the possible values of that column, and
        `probability_column`. The `probability_column` column's value
        represents the probability that `target_column` takes on the value
        in that row under the given conditions.

        Currently only works on categorical columns.
        """
        col_def = self._popmod.schema[target_column]
        if col_def.stat_type != 'categorical':
            raise ValueError('Column must be categorical')

        vals = [v.value for v in col_def.values]
        targets = {target_column: vals}
        df = self._popmod.joint_probability(
            targets=targets, given=given,
            probability_column=probability_column)
        return df.sort_values(probability_column, ascending=False)

    def _display_value_map(
            self,
            col  # type: str
    ):  # type: (...) -> Dict[str, str]
        """Return a map from values to their display values for a column.

        This maps a value to its `display_value` if it exists, or just itself
        otherwise.
        """
        col_def = self._popmod.schema[col]
        return {v.value: v.display_value or v.value for v in col_def.values}

    def row_assignment(self, rowids, random_seed=None):
        # type: (List[int], int) -> Any
        """Return the model structure for a list of rows.

        Returns a list of model structures, one for each model in the ensemble.
        The results are not easily interpretable in their current form. This
        will likely be the backing call for an easier-to-understand API.

        Args:
            rowids: The rowids to generate assignments for.
            random_seed: An optional seed to make the results deterministic.
        """
        targets = self._popmod.select(rowids=rowids)
        nulled_df = targets.where(pd.notnull(targets), None)
        req = {'targets': nulled_df.to_dict(orient='list')}
        if random_seed:
            req['random_seed'] = random_seed
        resp = self._popmod._endpoint.row_assignment.post(json=req).json()
        for model in resp['models']:
            for view in model['views']:
                for cluster in view['clusters']:
                    # Translate 0-based rowNums back into the original rowids
                    cluster['rowids'] = [
                        rowids[rowNum] for rowNum in cluster['rowNums']
                    ]
                    del cluster['rowNums']
        return resp

    def wheres_the_info(
            self,
            col1,  # type: str
            col2,  # type: str
            num_cells=5  # type: int
    ):
        # type: (...) -> List[Tuple[str, str, float]]
        """Returns the values for which the MI is the highest.

        The values are returned as a list of (val1, val2, mi) tuples) of
        length `num_cells`.

        Suppose you're efficiently encoding data distributed by the joint
        distribution of col1 and col2. Then, `mi` is the number of bits you'll
        save on average for each datum for attributable to (val1, val2) being
        encoded efficiently relative to the product of the marginals. If `mi`
        is negative, that amount of efficiency is _lost_ encoding that
        particular combination.

        Currently only works on two categorical columns.
        """
        pt = self._joint_probability_table(col1, col2)
        marg_pt = self._product_of_marginal_probabilities_table(pt)
        # Log base 2 so we get bits, not nats
        mi_table = pt * np.log2(pt / marg_pt)
        total_mi = np.sum(np.sum(mi_table))
        assert total_mi >= 0
        # Total MI is non-negative, but the individual elements don't have to
        # be. Make them all positive for sorting purposes.
        mi_abs_table = np.absolute(mi_table)

        # Use display_values if they exist.
        # TODO(asilvers): Probably want a more general way of doing this
        # and want to start using it in other methods
        mi_abs_table = mi_abs_table.rename(
            index=self._display_value_map(col1),
            columns=self._display_value_map(col2))

        largest = mi_abs_table.stack().nlargest(num_cells)
        res = []
        for (c1v, c2v), mi_abs in largest.iteritems():
            # Sort based on mi_abs, but then look up the original mi
            mi = mi_table[c2v][c1v]
            res.append((c1v, c2v, mi))
        return res

    def wheres_the_r2(
            self,
            col1,  # type: str
            col2,  # type: str
            num_cells=5  # type: int
    ):
        # type: (...) -> List[Tuple[str, str, float]]
        """Returns values where the joint and and marginal product differ.

        For a pair of columns, returns the values in the observed data for
        which the difference between the joint probability and the product of
        the marginal probabilities is the highest.

        The values are returned as a list of (val1, val2, difference) tuples
        of length `num_cells`.

        Currently only works on two categorical columns.
        """
        pt = self._joint_probability_table(col1, col2)
        marg_pt = self._product_of_marginal_probabilities_table(pt)

        # Compute a table of the differences so we can preserve the sign and
        # figure out whether values are higher or lower than `marg_pt`. The
        # values are (actual - `marg_pt`), so positive values mean that that
        # cell occurs more often than the product of the marginals.
        diff_table = pt - marg_pt
        # Square the table so we can sort ignoring sign.
        diff2_table = diff_table**2

        # Use display_values if they exist.
        # TODO(asilvers): Probably want a more general way of doing this
        # and want to start using it in other methods
        diff2_table = diff2_table.rename(index=self._display_value_map(col1),
                                         columns=self._display_value_map(col2))

        largest = diff2_table.stack().nlargest(num_cells)
        res = []
        for (c1v, c2v), diff2 in six.iteritems(largest):
            # Sort based on diff2, but then look up the original diff
            diff = diff_table[c2v][c1v]
            res.append((c1v, c2v, diff))
        return res

    def _joint_probability_table(
            self,
            col1,  # type: str
            col2  # type: str
    ):  # type: (...) -> DataFrame
        """Returns a table of the joint probabilities between two columns.

        Only works for categorical columns. asilvers@ is trying to think of the
        right abstraction for continuous columns.
        """
        col1_def = self._popmod.schema[col1]
        col2_def = self._popmod.schema[col2]
        if (col1_def.stat_type != 'categorical' or
                col2_def.stat_type != 'categorical'):
            raise NotImplementedError(
                'Both columns must be categorical for now')
        col1_vals = [v.value for v in col1_def.values]
        col2_vals = [v.value for v in col2_def.values]
        targets = {col1: [], col2: []}  # type: Dict[str, List[str]]
        for c1v, c2v in itertools.product(col1_vals, col2_vals):
            targets[col1].append(c1v)
            targets[col2].append(c2v)

        jpt = self._popmod.joint_probability(targets=targets)
        jpt = jpt.set_index([col1, col2])
        ps = jpt['p']
        assert 0.999 < np.sum(ps) < 1.001
        shape = (len(col1_vals), len(col2_vals))
        ct = DataFrame(
            ps.values.reshape(shape), columns=col2_vals, index=col1_vals)
        return ct

    def _product_of_marginal_probabilities_table(self, probability_table):
        # type: (DataFrame) -> DataFrame
        """Returns a table of joint probabilities assuming independence.

        Returns a table where each cell represents the probability of the
        respective columns taking on the values in that cell, assuming
        independence. The probabilities for each column are the marginal
        probabilities for each column, so the table is the cartesian product
        of the marginals.

        This is one half of the terms in an unnormalized chi^2 table if that
        makes it clearer, where the other half is `_joint_probability_table`.
        """
        pt = probability_table
        col1_vals = pt.index
        col2_vals = pt.columns
        # This is essentially
        # marg_pt = (scipy.stats.chi2_contingency(np.reshape(ps, shape)))[3]
        # but without the scipy dep.
        c1_margs = {v: sum(pt.loc[v]) for v in col1_vals}
        c2_margs = {v: sum(pt[v]) for v in col2_vals}
        marginals = []
        for c1v, c2v in itertools.product(col1_vals, col2_vals):
            marginals.append(c1_margs[c1v] * c2_margs[c2v])
        marg_pt = pd.DataFrame(
            np.reshape(marginals, pt.shape), columns=col2_vals,
            index=col1_vals)
        return marg_pt

    def total_logpdf(self, targets=None):  # type: (List[str]) -> float
        """Returns the log probability of the data under this model.

        Returns the sum of the log probabilities of all the rows in in the data
        for the columns in `targets`. This is similar to calling
        `row_probability` and summing the results except that `row_probability`
        returns None on rows with missing data, and this ignore it.

        This is in the log domain since the values are expected to be very
        small.
        """
        targets = self._popmod._columns_from_arg(targets)
        req = {'targets': targets}
        return self._popmod._endpoint.total_logpdf.post(json=req).json()

    def logpdf_from_simulate_by_model(
            self,
            df,  # type: DataFrame
            log_probability_column='lp'  # type: str
    ):  # type: (...) -> DataFrame
        """Return the logpdf of the values returned by `simulate_by_model`.

        This is so far mostly useful to implement mutual information from a
        client.
        """
        grouped = df.groupby('model')
        models = sorted(grouped.groups)
        targets = [grouped.get_group(m).to_dict('list') for m in models]
        req = {'targets': targets}
        resp = self._popmod._endpoint.logpdf_by_model.post(json=req)
        return pd.concat(
            DataFrame(targets[i]).assign(model=i).assign(
                **{log_probability_column: d})
            for i, d in enumerate(resp.json()))

    def infer_plot(
            self, target, rowid=None, using=None,
            given=None):  # type: (str, int, List[str], Dict[str, Any]) -> plt
        """Plot the model's pdf for a column given a row.

        Plot the pdf for a single column of a row, given the rest of the values
        in that row, as is done in `PopulationModel.infer`. Also plots the
        inferred value, and, if present, the actual value. This may be done for
        either an actual row or a hypothetical row of givens.

        If `using` is provided, only infer `target` based on the columns listed
        in `using`. This is useful when trying to avoid using one outcome
        variable to predict another. This only makes sense when using `rowid`,
        not `given`.
        """
        if rowid is not None and given is not None:
            raise ValueError(
                'At most one of `rowid` or `given` may be specified.')
        if given is not None and using is not None:
            raise ValueError('`using` only makes sense when passing `rowid`.')
        stat_type = self._popmod.schema[target].stat_type
        if stat_type not in ['realAdditive', 'realMultiplicative']:
            raise NotImplementedError('Only implemented for real columns')

        # Fix a seed so the bounds are deterministic
        sel = self._popmod.select(targets=[target], limit=100,
                                  random_seed=17)[target].dropna()
        min_sel, max_sel = min(sel), max(sel)
        width = max_sel - min_sel
        bounds = (min_sel - .1 * width, max_sel + .1 * width)

        # TODO(asilvers): Integrate this to make sure our bounds were good?
        x = np.linspace(bounds[0], bounds[1], num=10000)

        if rowid:
            # Select only `using` if provided (plus the actual value),
            # otherwise select everything
            to_sel = None if not using else (using + [target])
            # Condition on the values in that row
            row_vals = self._popmod.select(to_sel, rowids=[rowid]).to_dict(
                orient='records')[0]
            # Drop empty columns
            row_vals = {k: v for k, v in row_vals.items() if v is not None}
            given = row_vals
            # Drop the target column from givens if it exists.
            real_x = given.pop(target, None)
        else:
            given = copy.deepcopy(given) or {}
            real_x = None

        def pdf(x):
            return self._popmod.joint_probability(targets={target: list(x)},
                                                  given=given)['p']

        fig = plt.figure()
        ax = fig.add_subplot(2, 1, 1)
        ax.plot(x, pdf(x), 'blue')
        ax.set_xlabel(target)
        ax.set_ylabel('density')

        # Make a dataframe to infer into
        df = pd.DataFrame(given, index=[0])
        df[target] = [None]
        inf_x = self._popmod.infer_unobserved(df)[target]
        inf_y = pdf(inf_x)[0]
        inf_plt, = ax.plot(inf_x, inf_y, marker='o', markersize=10,
                           color='red', label='Inferred')
        handles = [inf_plt]

        if real_x:
            real_y = pdf([real_x])[0]
            real_plt, = ax.plot(real_x, real_y, marker='o', markersize=10,
                                color='black', label='Real')
            handles.append(real_plt)

        ax.legend(handles=handles)

        if stat_type == 'realMultiplicative':
            ax.set_xscale('log')

        return fig
