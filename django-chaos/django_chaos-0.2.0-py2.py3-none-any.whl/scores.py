# codign: utf-8
import logging
logger = logging.getLogger(__name__)


class Score(object):

    open_count = 0
    closed_count = 0
    score = 0

    @classmethod
    def Empty(cls):
        """
        Returns a simple empty score
        """
        return cls()

    def __init__(self, open_count=0, closed_count=0, score=0.0):
        self.open_count = open_count
        self.closed_count = closed_count
        self.score = score

    def __add__(self, other):
        return Score(
            self.open_count + other.open_count,
            self.closed_count + other.closed_count,
            self.score / 2.0 + other.score / 2.0
        )

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)


def calculate_node_score(node):
    if not node:
        logger.info('empty node, returning default score')
        return Score.Empty()
    children = node.get_descendants()
    leafs = [c for c in children if c.is_leaf_node()]
    if not leafs and node.is_root_node():
        leafs = [node]
    total_weight = sum([c.weight for c in leafs])
    closed_nodes = [c for c in leafs if c.status.is_closing_status]
    open_nodes = [c for c in leafs if not c.status.is_closing_status]
    closed_count = len(closed_nodes)
    open_count = len(open_nodes)
    total_closed_weight = sum([c.weight for c in closed_nodes])
    if total_weight == 0:
        total_weight = 1
    score = round(float(total_closed_weight) / float(total_weight), 2)
    return Score(open_count, closed_count, score)


def calculate_project_score(project):

    """
    Calculates a projects score, based
    on how many open/closed tasks it has
    """

    if not project:
        raise ValueError('project is required to calculate score')
    root_tasks = project.root_tasks.all()
    if root_tasks.count() <= 0:
        return Score.Empty()

    scores = [calculate_node_score(r) for r in root_tasks]
    return sum(scores)
