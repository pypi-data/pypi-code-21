import re


'''
Container for other data structures.
PlannerItem.item -> original data structure
'''
class PlannerItem():
    def __init__(self, item):
        self.id = item.id
        self.priority = item.priority
        self.expected_perent = 0
        self.diff = 0
        self.item = item

    def __repr__(self):
        return "[PlannerItem](%d)" % self.id


class PriorityPlanner():
    def __init__(self, cfg, preprocess=None):
        self.cfg = cfg
        self.stats = {"total":0, "done":0}
        self.preprocess = preprocess

    def internal_pre_process(self, items):
        new_items = []
        priority_sum = 0

        for item in items:
            if item.priority == 0:
                continue
            if item.priority < 0:
                raise Exception("p.priority is less than 0")

            new_items.append(PlannerItem(item))
            priority_sum += item.priority

        self.items = new_items

        if priority_sum == 0:
            return False

        for item in self.items:
            item.expected = float(item.priority) / priority_sum
            item.diff = item.expected
            item.actual = 0

        return True

    def update_stats(self, pid):
        stats = self.stats
        if stats.has_key(pid):
            stats[pid] += 1
        else:
            stats[pid] = 1
        stats['total'] += 1
        stats['done'] += 1

    def get_items(self):
        return self.items

    def calc_actual(self):
        total = self.stats["total"]
        for item in self.items:
            count = self.stats.get(item.id, 0)
            if total == 0:
                item.actual = 0
            else:
                item.actual = float(count) / total
            item.diff = item.expected - item.actual

    '''
    each item in items needs to have attr "id" and "priority"
    '''
    def plan(self, items, choose_func):
        if not self.internal_pre_process(items):
            raise StopIteration()
        if self.preprocess:
            self.preprocess(self.stats)
            self.calc_actual()
        n = 0
        items = self.items
        stats = self.stats
        while True:
            items = sorted(items, key=lambda x:x.diff, reverse=True)
            for item in items[:]:
                pid = item.id

                r = choose_func(item)
                if r:
                    self.update_stats(item.id)
                    self.calc_actual()
                    n += 1
                    yield r
                    break
                else:
                    items.remove(item)
            else:
                raise StopIteration()

        raise StopIteration()

