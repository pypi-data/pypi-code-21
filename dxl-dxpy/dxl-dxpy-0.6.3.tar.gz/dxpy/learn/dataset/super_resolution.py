from ..graph import Graph
from ..model.image import MultiDownSampler


class SuperResolutionDataset(Graph):
    """
    SuperResolutionDataset is a special kind of dataset which 
    """

    def __init__(self, name, origial_dataset_maker, input_key=None, nb_down_sample=None, with_shape_info=None, origin_shape=None, **config):
        super().__init__(name, input_key=input_key,
                         nb_down_sample=nb_down_sample,
                         with_shape_info=with_shape_info,
                         origin_shape=origin_shape,
                         **config)
        self._dataset_maker = origial_dataset_maker
        self.__construct()

    @classmethod
    def _default_config(cls):
        from dxpy.collections.dicts import combine_dicts
        return combine_dicts({'with_shape_info': False}, super()._default_config())

    def __down_sample_keys(self, start):
        return [('image{}x'.format(2**i), 2**i) for i in range(start, self.param('nb_down_sample') + 1)]

    def __construct(self):
        self.register_node('dataset',
                           self._dataset_maker())
        down_sample_ratios = {k: [v] * 2 for k,
                              v in self.__down_sample_keys(1)}
        origin_key = self.__down_sample_keys(0)[0][0]
        self.register_node('down_sampler',
                           MultiDownSampler(self.nodes['dataset'][self.param('input_key')],
                                            down_sample_ratios=down_sample_ratios,
                                            keep_original=True, original_key=origin_key,
                                            register_output_with_prefix=False))
        for k, _ in self.__down_sample_keys(0):
            self.register_node(k, self.nodes['down_sampler'][k])
