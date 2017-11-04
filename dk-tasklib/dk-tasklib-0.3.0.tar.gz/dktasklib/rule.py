# -*- coding: utf-8 -*-

import invoke


class BuildRule(object):
    requires = []
    after = []
    _temp_mark = _perm_mark = False

    def __init__(self, *args, **kwargs):
        # print "name:", self.__class__.__name__
        # print "ARGS:", args
        # print "KW:", kwargs
        self.ctx = None
        self.kwargs = kwargs
        self.args = ()
        if len(args) == 0:
            return

        ctx = None
        first, rest = args[0], args[1:]
        if isinstance(first, invoke.Context):
            ctx = first
            self.args = rest
        else:
            self.args = args

        if ctx is not None:
            self.run(ctx)

    def run(self, ctx):
        self.ctx = ctx
        for task_obj in self.topsort(self.requires):
            task_obj.run(ctx)

        if self.needs_to_run():
            self(*self.args, **self.kwargs)
            for task_obj in self.topsort(self.after):
                task_obj.run(ctx)

    def __call__(self, *args, **kwargs):
        raise NotImplemented

    def needs_to_run(self):
        return True

    def topsort(self, tasklist):
        """Topological sort
        """
        # id(t) was originally t.__name__, id(t) means there will be no sharing...
        tasks = {id(t): t for t in tasklist}
        res = []

        def visit(name, task):
            if task._temp_mark:
                raise ValueError("Circularity", name, res)
            if not task._perm_mark:
                task._temp_mark = True
                for d in task.requires:
                    visit(d, tasks[d])
                task._perm_mark = True
                task._temp_mark = False
                res.append(name)

        while 1:
            unmarked = set((name, task) for name, task in tasks.items()
                           if not (task._perm_mark or task._temp_mark))
            if not unmarked:
                return [tasks[k] for k in res]
            name, task = unmarked.pop()
            visit(name, task)


# @task
# class CreateFoo(BuildRule):
#     """Create foo.txt
#     """
#     requires = [FileExists('foo.txt')]
#
#     def needs_to_run(self):
#         # return False
#         return not os.path.exists('foo.txt') or int(open('foo.txt').read()) < time.time()
#
#     def __call__(self, name):
#         print "name:", name
#         with open('foo.txt', 'w') as fp:
#             print >>fp, int(time.time())
#         self.ctx.run('echo foo')
#         print 'foo:', open('foo.txt').read()
