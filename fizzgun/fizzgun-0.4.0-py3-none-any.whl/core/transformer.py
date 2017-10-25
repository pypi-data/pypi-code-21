import copy

from fizzgun.application.service_contexts import TransformerContext
from fizzgun.bubbles.bubble_arsenal import BubbleArsenal
from fizzgun.core.common import Worker
from fizzgun.models import HttpRequest


class Transformer(Worker):
    """
    Receives original requests and generates alterations of them
    """
    def initialize(self, bubbles_config=None):
        self._arsenal = BubbleArsenal(
            self.transformer_context.module_importer,
            self.transformer_context.id_generator,
            self.transformer_context.random_generator,
            self.transformer_context.stdout_writer
        )
        if bubbles_config:
            self._arsenal.load_from_config(bubbles_config)

    def process(self, work):
        request = HttpRequest(work['original'])
        for transformation, expectations, bubble in self.transform(request):
            output = copy.deepcopy(work)
            output.update({'modified': transformation, 'expectations': expectations, 'bubble': bubble})
            yield output

    def transform(self, request):
        for bubble in self._arsenal.bubbles():
            expectations = bubble.expectations._marshall()
            for transformation in bubble.inflate(request):
                yield transformation, expectations, {'name': bubble.name, 'description': bubble.description}

    @property
    def transformer_context(self) -> TransformerContext:
        return self.service_context
