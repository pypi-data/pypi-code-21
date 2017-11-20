
class BaseCollectionTrigger:
    """
    A basic class which you should use for declare your own collection triggers.
    """
    def __init__(self, collection, trigger):
        """
        :param collection: A `Collection` instance
        :param trigger: A trigger string which is a part of an url
        """
        self.collection = collection
        self.trigger = trigger

    def exists(self):
        raise NotImplementedError('Method "exists" should return a boolean value.')

    def get_data(self):
        raise NotImplementedError('Should return data object.')

    def get_default_tags(self):
        raise NotImplementedError('Should return default tags.')

    def check_tags(self, tags):
        raise NotImplementedError('Should return boolean.')

    def get_default_url(self):
        raise NotImplementedError('Should return URL.')

    def get_prefixes(self):
        raise NotImplementedError('Should return a list of supported prefixes.')
