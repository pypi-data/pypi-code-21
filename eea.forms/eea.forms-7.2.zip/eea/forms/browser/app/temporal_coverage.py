""" Temporal coverage widget
"""


from itertools import groupby

try:
    from Products.EEAContentTypes.interfaces import ITemporalCoverageAdapter
    HAS_TEMPORALCOVERAGE_ADAPTER = True
except ImportError:
    HAS_TEMPORALCOVERAGE_ADAPTER = False


def grouped_coverage(data):
    """ Given an iterable of numbers, group them by range
    """

    source = [int(x) for x in sorted(set(data))]
    output = []


    def group_func(idx_nr):
        """ Used as comparator for grouping
        """
        index, number = idx_nr
        return index - number


    for _key, group in groupby(enumerate(source), group_func):
        result = [x[1] for x in group]

        if len(result) == 1:
            output.append("{0}".format(result[0]))
        else:
            output.append("{0}-{1}".format(result[0], result[-1]))

    return output


class FormatTempCoverage(object):
    """ Format temporal coverage display
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        data = []
        if HAS_TEMPORALCOVERAGE_ADAPTER:
            try:
                adapter = ITemporalCoverageAdapter(self.context)
                data = adapter.value()
            except (AttributeError, TypeError):
                return ''
        else:
            field = self.context.getField('temporalCoverage')
            if field:
                data = field.getAccessor(self.context)()
                if not data:
                    return ''

        return ", ".join(grouped_coverage(data))
