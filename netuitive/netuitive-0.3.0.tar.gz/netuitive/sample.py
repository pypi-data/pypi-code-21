
class Sample(object):

    """
        A data point of the Metric
        :param metricId: Metric FQN
        :type metricId: string
        :param timestamp: Timestamp for the sample
        :type timestamp: int
        :param value: Value of the sample
        :type value: float
        :param min: Minimum of the sample
        :type min: float
        :param max: Maximum of the sample
        :type max: float
        :param avg: Average of the sample
        :type avg: float
        :param sum: Sum of the sample
        :type sum: float
        :param cnt: Count of the sample
        :type cnt: float
    """

    def __init__(self,
                 metricId,
                 timestamp,
                 val=None,
                 min=None,
                 max=None,
                 avg=None,
                 sum=None,
                 cnt=None):

        self.metricId = metricId
        self.timestamp = timestamp

        if val is not None:
            self.val = val

        if max is not None:
            self.max = max

        if avg is not None:
            self.avg = avg

        if cnt is not None:
            self.cnt = cnt

        if min is not None:
            self.min = min

        if sum is not None:
            self.sum = sum
