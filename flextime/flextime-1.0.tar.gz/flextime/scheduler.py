import networkx as nx, dateutil.parser, re

from flextime import utils
from functools import reduce
from datetime import datetime

class TimeBlock:
    max_cost = 1000
    def __init__(self, data):
        required_keys = ['day', 'name', 'start', 'end', 'resource_tiers']
        self.task_minutes = []
        if all([k in data for k in required_keys]):
            for k, v in data.items():
                setattr(self, k, v)
        else:
            print('Missing required attributes in TimeBlock')
            exit(1)

    def __str__(self):
        return "{} - {} ({}-{}) [{} / {}]".format(
            self.day,
            self.name,
            '{:02d}:{:02d}'.format(*divmod(self.start, 60)),
            '{:02d}:{:02d}'.format(*divmod(self.end, 60)),
            self.effective_minutes(),
            self.num_minutes(),
        )

    def toordinal(self):
        return (dateutil.parser.parse(self.day), self.start)
    
    def cost(self, task):
        cost = 10
        
        offset_cost = 10
        offset_multiplier = 2
        missing_multiplier = len(self.resource_tiers)
        for r in task.wants():
            offset_exponent = next((i for i, tier in enumerate(self.resource_tiers) if r in tier), missing_multiplier)
            if offset_exponent == 0:
                offset_exponent = missing_multiplier
            cost *= offset_multiplier**offset_exponent

        attrition_rate = 0.9

        early_threshold = 7
        days_between = (task.due() - self.day_date()).days
        early_multiplier = attrition_rate**days_between if days_between > 0 else 1
        if days_between < early_threshold:
            cost *= early_multiplier
        else:
            cost /= early_multiplier
            
        cost = int(cost)
        return cost if cost <= TimeBlock.max_cost else TimeBlock.max_cost
        
    def day_date(self):
        return dateutil.parser.parse(self.day)

    def resources(self):
        if isinstance(self.resource_tiers[0], list):
            return [item for sublist in self.resource_tiers for item in sublist]
        else:
            return self.resource_tiers
        
    def can_complete(self, task):
        available = self.day_date() >= task.available()
        within_due = self.day_date() <= task.due()
        needs_satisfied = all([(n in self.resources()) for n in task.needs()])

        return available and within_due and needs_satisfied
    
    def has_tasks(self):
        return len(self.tasks) > 0
    
    def attention_ratio(self):
        if hasattr(self, 'attention'):
            return self.attention / 100.0
        else:
            return 1
        
    def effective_minutes(self):
        return int((self.end - self.start) * self.attention_ratio())

    def num_minutes(self):
        return self.end - self.start
    
class Scheduler:
    def __init__(self, tasktree, schedule_file):
        self._tasktree = tasktree
        self._datatree = utils.file_to_dict(schedule_file)

        abbrevs = [
            (['mon', 'm'], 'monday'),
            (['tues', 't'], 'tuesday'),
            (['wed', 'w'], 'wednesday'),
            (['thurs', 'r'], 'thursday'),
            (['fri', 'f'], 'friday'),
            (['sat', 's'], 'saturday'),
            (['sun', 'u'], 'sunday'),
        ]

        def extend_map(acc, abbrev_tup):
            abbrev, day = abbrev_tup
            acc.update(dict.fromkeys(abbrev, day))
            return acc

        self.abbrev_map = reduce(extend_map, abbrevs, {})

    def expand_day(self, day_abbrev):
        return self.abbrev_map[day_abbrev] if day_abbrev in self.abbrev_map else 'unknown'

    def time_blocks(self):
        def time_block_gen():
            for k, v in self._datatree.items():
                name = k
                if isinstance(v, list) and len(v) > 1:
                    base = v[0]
                    time_defs = [dict(base, **d) for d in v[1:]]
                elif isinstance(v, dict):
                    base = v
                    time_defs = [v]
                else:
                    print('Wtf are you putting in your schedule config?')
                    exit(1)

                for d in time_defs:
                    if 'days' in d:
                        for day in d['days']:
                            day = self.expand_day(day)
                            block = dict(base, name=k, start=d['start'], end=d['end'], day=day)

                            tb = TimeBlock(block)
                            n = datetime.now()
                            if not (tb.day_date().day == n.day and 60*n.hour + n.minute > tb.end):
                                yield tb

        return sorted(list(time_block_gen()), key = lambda b: b.toordinal());
                
    def scheduled_tasks(self):
        time_blocks = self.time_blocks()
        graph = nx.DiGraph()

        total_minutes = 0
        total_task_minutes = 0

        for i, tb in enumerate(time_blocks):
            total_minutes += tb.num_minutes()
            graph.add_node('time.{}'.format(i))

        tasks = self._tasktree.sorted_leaves('d')

        for j, task in enumerate(tasks):
            total_task_minutes += task.time()

        graph.add_node('source', demand=-total_task_minutes)

        for j, task in enumerate(tasks):
            graph.add_node('task.{}'.format(j), demand=task.time())
            graph.add_edge('source', 'task.{}'.format(j), weight=TimeBlock.max_cost + 1)


        for i, tb in enumerate(time_blocks):
            graph.add_edge('source', 'time.{}'.format(i), capacity=tb.effective_minutes())
            for j, task in enumerate(tasks):
                if tb.can_complete(task):
                    graph.add_edge(
                        'time.{}'.format(i),
                        'task.{}'.format(j),
                        weight=tb.cost(task),
                    )

        try:
            flowDict = nx.min_cost_flow(graph)
        except nx.exception.NetworkXUnfeasible:
            print("No optimal solution found; you're probably going to lose some sleep.")
            exit(1)

        # Need to be returning tuples of number of minutes that go toward the task
        # and putting tasks with 0 time in unscheduled_tasks
        # for k, v in flowDict.items():
        #     if k == 'source':
        #         unscheduled_tasks
        #     else:
        #         time_ind = k.split('.')[1]
        #         for dest, mins in v.items():
        #             if mins > 0:
        #                 task_ind = dest.split('.')[1]
                        
        #                 time_blocks[time_ind].task_minutes.append((mins, tasks[task_ind]))
        for i, tb in enumerate(time_blocks):
            time_key = 'time.{}'.format(i)
            #tb.task_minutes = [task for j, task in enumerate(tasks) if 'task.{}'.format(j) in flowDict[time_key] and flowDict[time_key]['task.{}'.format(j)] > 0]
            tb.tasks = [(flowDict[time_key]['task.{}'.format(j)], task) for j, task in enumerate(tasks)
                        if 'task.{}'.format(j) in flowDict[time_key] and flowDict[time_key]['task.{}'.format(j)] > 0]

        unscheduled_tasks = [(flowDict['source']['task.{}'.format(i)], task) for i, task in enumerate(tasks)
                             if 'task.{}'.format(i) in flowDict['source'] and flowDict['source']['task.{}'.format(i)] > 0]
        
        return (unscheduled_tasks, time_blocks)
