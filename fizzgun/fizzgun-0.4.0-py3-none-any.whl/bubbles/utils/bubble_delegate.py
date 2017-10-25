

class BubbleDelegate(object):

    def generate(self, request):
        raise NotImplementedError("Method 'generate' must be implemented in %s" % self.__class__.__name__)

    def does_apply(self, _request):
        return True
