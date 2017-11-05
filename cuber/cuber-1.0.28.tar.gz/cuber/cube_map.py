from cuber import cube
from cuber import utils
from cuber import workflow
import copy

class CubeMap(cube.Cube):
    '''
    This does not allow to restore full result of map operation, because map-graph is not fully defined by its structure it also dependse on versions of code of used cubes.
    Disableing restoring, we force to apply (not eval!) graph for every item.
    '''
    restorable = False 

    def __init__(self, workflow, array_field, 
            apply_params = {}, 
            disable_inmemory_cache = False, 
            disable_file_cache = False, 
            perfomance_logging = False,
            pass_original_items = False,
            **kwargs):
        self.workflow = workflow
        self.apply_params = apply_params
        self.array_field = array_field

        self.disable_inmemory_cache = utils.parse_bool(disable_inmemory_cache)
        self.disable_file_cache = utils.parse_bool(disable_file_cache)
        self.perfomance_logging = utils.parse_bool(perfomance_logging)

        self.pass_original_items = utils.parse_bool(pass_original_items)
        self.kwargs = kwargs # data form dependency

    def name(self):
        return 'map_v1.0_{}'.format(utils.universal_hash((
                self.workflow,
                self.pass_original_items,
                self.apply_params,
                self.array_field,
                self.kwargs,
            )))

    def eval(self):
        mapped = []
        for item in self.kwargs[self.array_field]:
            graph_args = copy.deepcopy(self.apply_params)
            graph_args.update(copy.deepcopy(item))
            wf = workflow.Workflow(
                graph = self.workflow,
                graph_args = graph_args,
            )
            res = wf.run(
                disable_inmemory_cache = self.disable_inmemory_cache, 
                disable_file_cache = self.disable_file_cache,
                perfomance_logging = self.perfomance_logging,
            )
# if we pass original items, these all have to be dicts
            assert (isinstance(res, dict) and isinstance(item, dict)) or not self.pass_original_items
            if self.pass_original_items:
                mapped_item = copy.deepcopy(item) 
                mapped_item.update(res)
            else:
                mapped_item = res
            mapped.append(mapped_item)

        # formatting result
        result = {}
        for key, value in self.kwargs.iteritems():
            if key != self.array_field:
                result[key] = value
            else: 
                result[key] = mapped
        return result
