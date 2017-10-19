from collections import defaultdict
from contracts import contract
from math import ceil
from procgraph.core.constants import ETERNITY
import warnings

__all__ = [
    'ExecutionStats',
]

class Statistics(object):

    def __init__(self, block):
        self.block = block
        self.num = 0
        self.mean_cpu = 0
        self.var_cpu = 0
        self.mean_wall = 0
        self.var_wall = 0
        self.perc_cpu = None
        self.perc_wall = None
        self.perc_times = None
        self.baseline_fraction = None
        self.last_timestamp = None
        self.mean_delta = 0
        self.delta_num = 0


class ExecutionStats(object):

    def __init__(self):
        self.samples = {}
        
        self.connection2samples = defaultdict(lambda: [])
        self.block2samples = defaultdict(lambda:[])
        
    @contract(connection='isinstance(BlockConnection)',
              timestamp='pg_timestamp_or_eternity')
    def add_connection_sample(self, connection, value, timestamp):
        if timestamp == ETERNITY:
            timestamp = 0.0
        else:
            timestamp = float(timestamp)

        from .model import BlockConnection
        assert isinstance(connection, BlockConnection)
        warnings.warn('Size computation disabled due to speed')
        if self.connection2samples[connection]:
            s = self.connection2samples[connection][0]['size']
        else:
            import cPickle as pickle
            s = len(pickle.dumps(value))
        sample = dict(timestamp=float(timestamp), size=s)
        self.connection2samples[connection].append(sample)

    @contract(timestamp='pg_timestamp_or_eternity')
    def add_signal_sample(self, block, cpu, wall, timestamp):
        # assert cpu >= 0, cpu
        sample = dict(timestamp=timestamp, cpu=cpu, wall=wall)
        self.block2samples[block].append(sample)
    
    def get_all(self):
        def summarize(values):
            perc = [5, 25, 50, 75, 95]

            import numpy as np
            x = map(float, np.percentile(values, perc))
            return dict(zip(perc, x))

        def summarize_samples(samples):
            res = {}
            fields = list(samples[0].keys())
            for f in fields:
                values = [s[f] for s in samples]
                res[f] = summarize(values)
            return res

        res = {}
        res['blocks'] = {}
        from procgraph.core.model import Model

        for block, samples in self.block2samples.items():
            if not isinstance(block, Model):
                res['blocks'][block.name] = dict(stats=summarize_samples(samples))

        res['signals'] = []
        for connection, samples in self.connection2samples.items():
            stats = summarize_samples(samples)
            v = {'stats': stats,
                     'block1':connection.block1.name,
                     'block1_signal':connection.block1_signal,
            }



            if isinstance(connection.block2, Model):
                # if connected to a model, we are really connecting to the input
                block2_inputblock = connection.block2.model_input_ports[connection.block2_signal]
                block2_inputblock_name = '%s.%s' % (connection.block2.name, block2_inputblock.name)
                v['block2_signal'] = connection.block2_signal
                v['block2'] = block2_inputblock_name
            else:
                v['block2_signal'] = connection.block2_signal
                v['block2'] = connection.block2.name

            if isinstance(connection.block1, Model):
                # if connected to a model, we are really connecting to the input
                block1_inputblock = connection.block1.model_output_ports[connection.block1_signal]
                block1_inputblock_name = '%s.%s' % (connection.block1.name, block1_inputblock.name)
                v['block1_signal'] = connection.block1_signal
                v['block1'] = block1_inputblock_name
            else:
                v['block1_signal'] = connection.block1_signal
                v['block1'] = connection.block1.name
            res['signals'].append(v)
        return res
        
        
    #### Old interface
        
    def add(self, block, cpu, wall, timestamp):
        # weird wall/cpu behavior when suspending the process
        self.add_signal_sample(block,cpu,wall,timestamp)
        
        if wall < 0:
            wall = 1
        if cpu < 0:
            cpu = wall

        if cpu == 0:
            cpu = 0.0001
        if wall == 0:
            wall = 0.0001

        if not block in self.samples:
            self.samples[block] = Statistics(block)

        s = self.samples[block]

        # TODO: set parameter
        WINDOW = 100
        N = min(s.num, WINDOW)

        s.mean_cpu = (s.mean_cpu * N + cpu) / (N + 1)
        s.var_cpu = (s.var_cpu * N + (cpu - s.mean_cpu) ** 2) / (N + 1)
        s.mean_wall = (s.mean_wall * N + wall) / (N + 1)
        s.var_wall = (s.var_wall * N + (wall - s.mean_wall) ** 2) / (N + 1)
        s.num += 1

        if isinstance(timestamp, float):
            if s.last_timestamp is not None:
                delta = timestamp - s.last_timestamp
                # when the block is a model, it could be called multiple times
                if delta > 0:
                    N = s.delta_num
                    s.mean_delta = (s.mean_delta * N + delta) / (N + 1)
                    s.delta_num += 1
                    # print "%s %d mean %d" % 
                    # (s.block, delta * 1000, 1000 * s.mean_delta)

        s.last_timestamp = timestamp

    def print_info(self):
        samples = list(self.samples.values())
        write_stats(samples)


def write_stats(samples):
    for s in samples:
        assert isinstance(s, Statistics)

    # get the block that executed fewest times and use it as a baseline
    baseline = min(samples, key=lambda s: s.num)

    # update percentage
    total_cpu = sum([s.mean_cpu * s.num for s in samples])
    total_wall = sum([s.mean_wall * s.num for s in samples])
    total_times = sum([s.num for s in samples])
    for s in samples:
        s.perc_cpu = s.mean_cpu * s.num / total_cpu
        s.perc_wall = s.mean_wall * s.num / total_wall
        s.perc_times = s.num * 1.0 / total_times
        s.baseline_fraction = s.num * 1.0 / baseline.num

    # sort by percentage
    alls = sorted(list(samples), key=lambda x: (-x.perc_wall))
    min_perc = 3
    print('--- Statistics (ignoring < %d%%) baseline: %d iterations of %s' % 
          (min_perc, baseline.num, baseline.block))
    for s in alls:
        perc_cpu = ceil(s.perc_cpu * 100)
        perc_wall = ceil(s.perc_wall * 100)
        if (s != baseline and
             (perc_cpu < min_perc) and
             (perc_wall < min_perc)):
            continue
        perc_times = ceil(s.perc_times * 100)

        # jitter_cpu = ceil(100 * (sqrt(s.var_cpu) * 2 / s.mean_cpu))
        # jitter_wall = ceil(100 * (sqrt(s.var_wall) * 2 / s.mean_wall))

        if s.mean_cpu < 0.7 * s.mean_wall:
            comment = 'IO '
        else:
            comment = '   '
        # print ''.join([
        # '- cpu: %dms (+-%d%%) %02d%% of total; ' % 
        # (1000 * s.mean_cpu, jitter_cpu, perc_cpu),
        # 'wall: %dms (+-%d%%) %02d%% of total; ' % 
        # (1000 * s.mean_wall, jitter_wall, perc_wall),
        # 'exec: %02d%% of total' % perc_times])

        if s.mean_delta > 0:
            fps = 1.0 / s.mean_delta
            stats = '%3.1f fps' % fps
        else:
            stats = ' ' * len('%3.1f fps' % 0)

        name = str(s.block)
        if len(name) > 35:
            name = name[:35]
        print(''.join([
            ' cpu %4dms %2d%%| ' % (1000 * s.mean_cpu, perc_cpu),
            'wall %4dms %2d%%| ' % (1000 * s.mean_wall, perc_wall),
            'exec %2d%% %3d (%3.1fx) %s| %s ' % (perc_times,
                                             s.num,
                                             s.baseline_fraction,
                                                      stats, comment),
                                                      name]))


