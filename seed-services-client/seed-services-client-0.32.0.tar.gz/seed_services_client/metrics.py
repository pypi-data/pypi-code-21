from demands import JSONServiceClient


class MetricsApiClient(object):
    """
    Client for the Metrics API.

    :param str url: The full URL of the API
    :param tuple auth:
        A tuple containing (username, password) for the authentication of the
        service. Defaults to not using authentication.
    :param demands.JSONServiceClient session:
        The session to use for requests. Defaults to creating a new session.
    """
    def __init__(self, url, auth=None, session=None):
        if session is None:
            session = JSONServiceClient(
                url=url,
                auth=auth)
        self.session = session

    def get_metrics(self, **kwargs):
        """
        Gets the metrics for the specified parameters.

        :param list_or_str m:
            A list of strings representing the metric names that you want to
            query, or a string representing the metric name of the single
            metric that you want to query.
        :param str from:
            The relative or absolute time to start the time period.
        :param str until:
            The relative or absolute time to end the time period.
        :param str nulls:
            What to do with null values. 'keep' keeps the null values, 'omit'
            removes the null values from the returned data points, 'zeroize'
            converts all null values to zero.
        :param str interval:
            The time length that each data point should cover, ie. the time
            resolution of the returned data.
        :param bool align_to_from:
            If False, the buckets will be aligned according to the nearest
            rounded value, ie. for a 10 minute interval, buckets will start at
            00h00, 00h10, 00h20, etc.
            If True, the buckets will be aligned according to the 'from' value
        """
        if 'from_' in kwargs:
            from_ = kwargs.pop('from_')
            kwargs['from'] = from_

        return self.session.get('/metrics/', params=kwargs)

    def fire_metrics(self, **kwargs):
        """
        Fires data points for a specific metrics.

        Takes in arguments in the format 'metric_name=metric_value', where
        metric_name is the name of the metric that you want to fire a data
        point for, and metric_value is the value you want for fire for that
        metric.
        """
        return self.session.post('/metrics/', data=kwargs)
