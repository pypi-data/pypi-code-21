from ..base import Model, ModelPipe, NodeKeys


class SuperResolutionKernel(ModelPipe):
    def __init__(self, reps, name='kernel', **configs):
        super().__init__(reps, name, **config)

    def _kernel(self, feeds):
        x = feeds[NodeKeys.INPUT]
        


class SRB(Model):
    def __init__(self, image_input, represents=None, name='srb', **configs):
        super().__init__(name=name, inputs={'ipt': image_input, 'rep': represents},
                         **configs)

    def _kernel(self, feeds):
        if feeds['rep'] is None:
