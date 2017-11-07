"""Exposes the Slack result recorder."""
try:
    import requests
except ImportError:
    pass


class Slack(object):
    """Send a Slack notification when a pipeline completes.

    Args:
        url (str): Slack Webhook URL
        channel (str): The channel name to post to
        values: (dict): A mapping of result keys to report

    Note:
        Use of this class requires the installation of the `slackclient module
        <https://slackapi.github.io/python-slackclient/>`_.
    """

    def __init__(self, url, channel, values):
        """Initialize the recorder."""
        self.url = url
        self.channel = channel
        self.values = values

    def write(self, results):
        """Send a message to Slack.

        Args:
            results (dict): A dictionary of results to record
        """
        msg = ['Pirec task complete']
        for field in self.values:
            msg.append('{0}: {1}'.format(field, self.values[field](results)))
        payload = {
            'text': '\n'.join(msg),
            'channel': self.channel,
        }
        requests.post(self.url, json=payload)
