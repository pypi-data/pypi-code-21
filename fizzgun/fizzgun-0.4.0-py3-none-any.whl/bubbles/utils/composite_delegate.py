from fizzgun.bubbles import Bubble
from fizzgun.bubbles.utils.bubble_delegate import BubbleDelegate


class CompositeDelegate(BubbleDelegate):

    def __init__(self):
        self._components = []

    def add_component(self, component: 'BubbleDelegate'):
        self._components.append(component)

    def generate(self, request):
        for comp in self._components:
            if not comp.does_apply(request):
                continue
            for sample in comp.generate(request):
                yield sample

    def does_apply(self, request):
        return any(comp.does_apply(request) for comp in self._components)


class BubbleWithDelegates(Bubble):

    def initialize(self, *args, **kwargs):
        super(BubbleWithDelegates, self).initialize(*args, **kwargs)
        self._delegate = CompositeDelegate()

    @property
    def delegate(self) -> CompositeDelegate:
        return self._delegate

    # Override
    def does_apply(self, request):
        return self.delegate.does_apply(request)

    # Override
    def generate(self, request):
        return self.delegate.generate(request)
