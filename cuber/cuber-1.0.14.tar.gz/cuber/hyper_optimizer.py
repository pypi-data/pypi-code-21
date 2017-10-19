# -*- coding: utf-8 -*-
import workflow
import sqlite3
import GPy
import GPyOpt
import logging
import datetime
import json
import numpy as np
import random

logger = logging.getLogger(__name__)

class HyperOptimizerHandler():
    '''
    optimisation_params format:
    {
        'vars': {
            var1: {
                'bounds': [0.01, 1.5]
            },
            alpha: {
                'bounds': [0, 10]
            }
        }
    }
    history row format: (result is contained in another column)
    {
        var1: 0.5,
        alpha: 6.1
    }
    '''
    def __init__(self, seed = 1, optimize_id = None, graph = None, optimization_params = None, comment = ''):
        self.setup_db()
        random.seed(seed)
        np.random.seed(seed)
        if optimize_id is not None:
            self.optimize_id = optimize_id
        else:
            self.db_register(graph, optimization_params, comment)

    def setup_db(self):
        db_file = 'optimizer.db'

        self.db_connect = sqlite3.connect(db_file)
        c = self.db_connect.cursor()
        c.executescript('''
            CREATE TABLE IF NOT EXISTS optimizers
                             (optimize_id INTEGER PRIMARY KEY, graph text, params text, comment text, start_time text, end_time text, status text);

            CREATE TABLE IF NOT EXISTS steps
                            (step_id Integer primary key, optimize_id INTEGER, step_params text, result float)

            ''')
        self.db_connect.commit()
        logger.info('DB: prepared')

    def db_register(self, graph, optimization_params, comment):
        c = self.db_connect.cursor()
        c.execute(
        '''
            INSERT INTO optimizers (graph, params, comment, start_time, status) VALUES (?, ?, ?, ?, ?)
        ''',
            (graph, json.dumps(optimization_params), comment, datetime.datetime.now().isoformat(), 'register')
        )
        self.optimize_id = c.lastrowid
        logger.info('Optimize ID: {}'.format(self.optimize_id))
        self.db_connect.commit()
        logger.info('DB: registered')

    def get_graph(self):
        c = self.db_connect.cursor()
        c.execute(
        '''
            SELECT graph FROM optimizers WHERE optimize_id = ?
        ''',
            (self.optimize_id, )
        )
        return c.fetchone()[0]

    def get_params(self):
        c = self.db_connect.cursor()
        c.execute(
        '''
            SELECT params FROM optimizers WHERE optimize_id = ?
        ''',
            (self.optimize_id, )
        )
        return json.loads(c.fetchone()[0])

    def get_history(self):
        c = self.db_connect.cursor()
        c.execute(
        '''
            SELECT step_params, result FROM steps WHERE optimize_id = ?
        ''',
            (self.optimize_id, )
        )
        result_ = []
        for step_params, result in c.fetchall():
            result_.append({
                'step_params': json.loads(step_params),
                'result': result
            })
        return result_

    def save_result(self, point, result):
        step_params = {}
        for val, var in zip(point, self.get_params()['vars'].keys()):
            step_params[var] = val
        c = self.db_connect.cursor()
        c.execute(
        '''
            INSERT INTO steps (optimize_id, step_params, result) VALUES (?, ?, ?)
        ''',
            (self.optimize_id, json.dumps(step_params), result)
        )
        self.db_connect.commit()
        logger.info('Result saved')

    def deduplicate_history(self):
        c = self.db_connect.cursor()
        c.execute(
        '''
        delete   from steps
        where    rowid not in
                 (
                 select  min(rowid)
                 from    steps
                 group by
                    step_params,
                    result,
                    optimize_id
                 ) and optimize_id = ?
        ''',
            (self.optimize_id, )
        )
        self.db_connect.commit()

    def update_history(self, X, Y):
        for x, y in zip(X, Y):
            self.save_result(x, y[0])
        self.deduplicate_history()

class HyperOptimizer():
    def __init__(self, *args, **kwargs):
        '''
        :param optimization_field: field of result to omptimise
        '''
        self.handler = HyperOptimizerHandler(*args, **kwargs)
        self.optimization_field = self.handler.get_params()['target']

    def substitute_params(self, point):
        # TODO: Remove this function. This is basic functionallity of workflow now.
        '''
        :param point: array of vars' values in order of dictionary
        '''
        graph = self.handler.get_graph()
        for value, var in zip(point, self.handler.get_params()['vars'].keys()):
            graph = graph.replace('$' + var, str(value))
        #logger.info('Subs graph: {}'.format(graph))
        return graph


    def eval_point(self, point):
        #logger.info('Point: {}'.format(point))
        wf = workflow.Workflow(graph = self.substitute_params(point))
        data = wf.run()
        return data[self.optimization_field]

    def get_problem(self):
        params = self.handler.get_params()
        for param in params.keys():
            assert param in {'maximaize', 'vars', 'target'}
        bounds = [{'name': var, 'domain': var_params['bounds'], 'type': 'continuous'} for var, var_params in params['vars'].iteritems()]

        X = []
        Y = []
        for hist in self.handler.get_history():
            step_params = []
            for var, value in hist['step_params'].iteritems():
                step_params.append(value)
            X.append(np.array(step_params))
            Y.append(np.array([hist['result']]))
        X = np.array(X) if len(X) != 0 else None
        Y = np.array(Y) if len(Y) != 0 else None

        #logger.info('Bounds: {}'.format(bounds))
        #logger.info('History: {}'.format((X, Y)))

        maximaize = params.get('maximaize', 'false') in ('true', 'yes', 't', 'y')

        myProblem = GPyOpt.methods.BayesianOptimization(lambda X: self.eval_point(X[0]) * (-1. if maximaize else 1.), bounds, X = X, Y = Y, exact_feval = True)
        return myProblem

    def step(self):
        myProblem = self.get_problem()
        myProblem.run_optimization(1)

        #logger.info('New optimal point: {}'.format(myProblem.x_opt))

        self.handler.update_history(myProblem.X, myProblem.Y)
        #logger.info('History2: {}'.format((myProblem.X, myProblem.Y)))

    def add_point(self, point, value = None):
        '''
        :param point: dict: var -> val
        '''
        f_value = value # copy, because we use value as another variable
        params = self.handler.get_params()
        assert params['vars'].keys() == point.keys(), \
                'Vars-list must be the same:\nhave: {}\nexpected: {}'.format(point.keys(), params['vars'].keys())

        point_ = []
        for var, value in point.iteritems():
            point_.append(value)

        if f_value is None:
            logger.info('Value is None. Evaluating...')

            maximaize = params.get('maximaize', 'false') in ('true', 'yes', 't', 'y')
            f_value = self.eval_point(point_) * (-1. if maximaize else 1.)
            logger.info('Evaluated')

        self.handler.save_result(point_, f_value)


    def optimize(self, iters = 10):
        for i in xrange(iters):
            logger.info('{} step'.format(i+1))
            self.step()
        myProblem = self.get_problem()
        myProblem.run_optimization(None)
        return myProblem.x_opt
