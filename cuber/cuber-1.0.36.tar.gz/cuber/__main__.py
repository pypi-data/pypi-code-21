import logging.config
import click
import logging
import numbers
import os.path
import cPickle as pickle
import time
import configparser
import sqlite3
import datetime
import json
import commentjson
import os
import datetime
import sys

import workflow
import cube
import hyper_optimizer
import utils

logging.basicConfig(level=logging.INFO,
                            format='%(levelname)s: %(asctime)s ::: %(name)s: %(message)s (%(filename)s:%(lineno)d)',
                                                datefmt='%Y-%m-%d %H:%M:%S')

logging_alias = logging
# TODO: save to db: graph_args, main graph, important flag, run string

def setup_logging(tg_chat, tg_token, file_logging = True, disable_existing_loggers = True, debug_logging = False):
    if tg_chat is not None:
        tg_chat = int(tg_chat)

    log_dir = './logs/'

    logging_handlers = {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        }
    }

    logging_level = 'DEBUG' if debug_logging else 'INFO'

    if file_logging:
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)
        logging_handlers['file'] = {
            'class': 'logging.FileHandler',
            'formatter': 'console',
            'filename': os.path.join(log_dir, '{}.log'.format(datetime.datetime.now().isoformat('_'))),
        }

    if tg_chat is not None:
        logging_handlers['telegram'] = {
            'class': 'telegram_handler.TelegramHandler',
            'token': tg_token,
            'chat_id': tg_chat,
            'level': 'CRITICAL',
            'formatter': 'telegram',
        }

    logging.config.dictConfig({
        'version': 1,
        'handlers': logging_handlers,
        "loggers": {
            "": {
                "level": logging_level,
                "handlers": ['console'] + (['telegram'] if tg_chat is not None else []) + (['file'] if file_logging else []),
                "propagate": "no"
            }
        },
        'formatters': {
            'console': {
                'format': '%(levelname)s: %(asctime)s ::: %(name)-10s: %(message)s (%(filename)s:%(lineno)d)',
            },
            'telegram': {
                'format': '%(message)s',
            }
        },
        'disable_existing_loggers': disable_existing_loggers,
    })

def get_startup_command():
    return ' '.join(sys.argv[1:])

class Main():
    def __init__(self):

        self.checkpoints_dir = config.get('cuber', 'checkpoints_dir', fallback = './checkpoints/')
        self.frozens_dir = config.get('cuber', 'frozens_dir', fallback = './frozens/')

        self.setup_db()


    def setup_db(self):
        path = os.path.abspath(self.checkpoints_dir)
        if not os.path.isdir(path):
            os.makedirs(path)

        db_file = os.path.join(self.checkpoints_dir, 'graphs.db')

        logging.info('DB: file: {}'.format(db_file))
        self.db_connect = sqlite3.connect(db_file)
        c = self.db_connect.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS graphs
                             (id INTEGER PRIMARY KEY, date text, file text, graph text, result text, comment text, start_time text, end_time text, status text)''')
        self.db_connect.commit()
        logging.info('DB: prepared')

    def db_register(self):
        c = self.db_connect.cursor()
        c.execute(
        '''
            INSERT INTO graphs (date, file, start_time, status, graph, comment) VALUES (?, ?, ?, ?, ?, ?)
        ''',
            (datetime.datetime.now().date().isoformat(), self.workflow_file, datetime.datetime.now().isoformat(), 'register', self.graph, self.comment)
        )
        self.db_id = c.lastrowid
        logging.info('Graph ID: {}'.format(self.db_id))
        self.db_connect.commit()
        logging.info('DB: registered')

    def db_update_status(self, status):
        c = self.db_connect.cursor()
        c.execute(
        '''
            UPDATE graphs SET status = ? WHERE id = ?
        ''',
            (status, self.db_id)
        )
        self.db_connect.commit()
        logging.info('DB: status updated to {}'.format(status))

    def db_update_comment(self, comment):
        c = self.db_connect.cursor()
        c.execute(
        '''
            UPDATE graphs SET comment = ? WHERE id = ?
        ''',
            (comment, self.db_id)
        )
        self.db_connect.commit()
        logging.info('DB: comment updated')

    def db_save_result(self, result):
        c = self.db_connect.cursor()
        c.execute(
        '''
            UPDATE graphs SET result = ?, end_time = ? WHERE id = ?
        ''',
            (result, datetime.datetime.now().isoformat(), self.db_id)
        )
        self.db_connect.commit()
        logging.info('DB: result saved')

    def db_show(self, filter_done = False):
        c = self.db_connect.cursor()
        res = c.execute(
        '''
            SELECT id, file, start_time, status, comment FROM graphs {}
        '''.format('WHERE status = "done"' if filter_done else ''),
        )
        for row in res:
            print '\t'.join(map(str, row))

    def db_show_detailed(self, db_id):
        c = self.db_connect.cursor()
        res = c.execute(
        '''
            SELECT id, graph, file, start_time, end_time, status, comment, result FROM graphs WHERE id = ?
        ''',
            (db_id, )
        )
        for row in res:
            print '\n'.join(map(str, row))

    def set_status_killed(self, graph_id):
        self.db_id = graph_id
        self.db_update_status('killed')

    def run_graph(self, workflow_file, full_result, comment, main, graph_args, 
            disable_inmemory_cache, disable_file_cache,
            frozens_id, create_frozens, use_frozens, use_frozen_only_if_exists,
            cleanup,
            perfomance_logging,
            ):
        self.workflow_file = workflow_file
        self.comment = comment
        start_time = time.time()

        with open(workflow_file) as f:
            self.graph = f.read()

        self.db_register()

        message_delay = 60 * float(config.get('cuber', 'message_delay', fallback = 3))

        job_descritpion = '{}; {}'.format(workflow_file, self.comment)

        try:
            cube.Cube.checkpoints_dir = self.checkpoints_dir
            logging.info('Checkpoints dir: {}'.format(cube.Cube.checkpoints_dir))
            wf = workflow.Workflow(workflow_file, 
                main = main, 
                graph_args = graph_args,
                frozens_dir = self.frozens_dir, 
                frozens_id = frozens_id,
                create_frozens = create_frozens,
                use_frozens = use_frozens,
                use_frozen_only_if_exists = use_frozen_only_if_exists,
            )

            self.db_update_status('running')
            data = wf.run(
                disable_inmemory_cache = disable_inmemory_cache, 
                disable_file_cache = disable_file_cache,
                cleanup = cleanup,
                perfomance_logging = perfomance_logging,
            )

            res = utils.dict_to_string(data, full = full_result)

            if time.time() - start_time >= message_delay:
                logging.critical('Calculation is done: {} (graph id: {})\n{}'.format(job_descritpion, self.db_id, res))
            else:
                logging.info('Calculation is done: {} (graph id: {})\n{}'.format(job_descritpion, self.db_id, res))
            self.db_save_result(res)
            self.db_update_status('done')
        except KeyboardInterrupt:
            if time.time() - start_time >= message_delay:
                logging.critical('Calculation is cancelled: {} (graph id: {})'.format(job_descritpion, self.db_id))
            else:
                logging.error('Calculation is cancelled: {} (graph id: {})'.format(job_descritpion, self.db_id))
            self.db_save_result('candelled')
            self.db_update_status('cancelled')
        except:
            import traceback
            traceback.print_exc()
            if time.time() - start_time >= message_delay:
                logging.critical('Calculation is failed: {} (graph id: {})'.format(job_descritpion, self.db_id))
            else:
                logging.error('Calculation is failed: {} (graph id: {})'.format(job_descritpion, self.db_id))
            self.db_update_status('failed')

config = None

@click.group()
@click.option('--logging', default = False, is_flag=True)
@click.option('--debug', default = False, is_flag=True)
def cli(logging, debug):
    global config
    config_file = '.cuber'
    config = configparser.ConfigParser()
    config.read(config_file)

    setup_logging(
        config.get('telegram', 'chat_id', fallback = None),
        config.get('telegram', 'token', fallback = None),
        file_logging = config.get('cuber', 'file_logging', fallback = False),
        disable_existing_loggers = not logging,
        debug_logging = debug,
    )

    logging_alias.info('Start up command: {}'.format(get_startup_command()))

    utils.override_default_hash_type = config.get('cuber', 'hash_type', fallback = None)

@cli.command()
def test_telegram():
    """
        Send telegram message with current config params
    """
    logging.critical('This is the test telegram message from cuber')

@cli.command()
@click.argument('workflow_file')
@click.option('--full_result', default = False, is_flag=True)
@click.option('--disable_inmemory_cache', default = False, is_flag=True)
@click.option('--disable_file_cache', default = False, is_flag=True)
@click.option('--comment', default = '')
@click.option('--main', default = 'main', help = 'Name of graph, that will be evaluated.')
@click.option('--graph_args', default = '{}', help = 'Json dict of params, that will be substituted at graph after `$` (`$alpha` and so on).')
@click.option('--create_frozens', default = None, help = 'Create frozen points at subgraphs, where you specified "frozen": true')
@click.option('--use_frozens', default = None)
@click.option('--cleanup', default = False, is_flag=True)
@click.option('--perfomance_logging', default = False, is_flag=True)
@click.option('--use_frozen_only_if_exists', default = False, is_flag=True)
def run(workflow_file, full_result, comment, main, graph_args, 
        disable_inmemory_cache, disable_file_cache,
        create_frozens, use_frozens, use_frozen_only_if_exists,
        cleanup,
        perfomance_logging,
        ):
    """
        Runs the workflow file (graph)
    """
    if create_frozens is not None and use_frozens is not None:
        assert create_frozens == use_frozens
    frozens_id = create_frozens if create_frozens is not None else use_frozens if use_frozens is not None else None
    Main().run_graph(workflow_file, full_result, 
        comment = comment, 
        disable_inmemory_cache = disable_inmemory_cache,
        disable_file_cache = disable_file_cache,    
        graph_args = json.loads(graph_args),
        main = main,
        frozens_id = frozens_id,
        create_frozens = create_frozens is not None,
        use_frozens = use_frozens is not None,
        use_frozen_only_if_exists = use_frozen_only_if_exists,
        cleanup = cleanup,
        perfomance_logging = perfomance_logging,
    )

@cli.command()
@click.argument('pickle_file')
@click.option('--only_keys', default = False, is_flag=True)
@click.option('--key', default = None)
def print_pickle(pickle_file, only_keys, key):
    with open(pickle_file, 'rb') as f:
        data = pickle.load(f)
    if only_keys:
        assert isinstance(data, dict)
        for key in data:
            print key
    else:
        if key is None:
            print data
        else:
            print data[key]

@cli.command()
@click.argument('pickle_file')
@click.option('--content', default = '{}', required = True)
def write_pickle(pickle_file, content):
    with open(pickle_file, 'wb') as f:
        pickle.dump(json.loads(content), f)
    logging.info('Done')

@cli.command()
@click.option('--opt_id', default = None)
@click.option('--iters', default = 20)
@click.option('--comment', default = '')
@click.argument('optimize_file', required=False)
def optimize(optimize_file, iters, comment, opt_id):
    """
        Creates a new optimization and starts it. If opt_id is specified, the passed optimization will be continued.
    """
    if opt_id is not None:
        ho = hyper_optimizer.HyperOptimizer(
                optimize_id = opt_id
            )
    else:
        with open(optimize_file) as f:
            optimize_json = f.read()
        optimize = commentjson.loads(optimize_json)

        with open(optimize['graph_file']) as f:
            graph = f.read()
        ho = hyper_optimizer.HyperOptimizer(
                graph = graph,
                optimization_params = optimize['params'],
                comment = comment,
            )
    result = ho.optimize(iters = iters)
    logging.info('optimisation result: {}'.format(result))

@cli.command()
@click.option('--opt_id', default = None, required = True)
@click.option('--point', default = None, required = True, help = 'JSON formatted string {var: value, ...}')
@click.option('--value', default = None, help = 'You may specify value of function at the point. Else the function will be evaluated.')
def optimize_add_point(opt_id, point, value):
    """
        Inserts users specified points to optimizer history. If you know attrs values, that prodice a good result, then this way you may suggest them to optimizer.
    """
    ho = hyper_optimizer.HyperOptimizer(
            optimize_id = opt_id
        )
    ho.add_point(json.loads(point), value)
    logging.info('Done')

@cli.command()
@click.option('--opt_id', default = None)
def optimize_show(opt_id):
    """
        Shows the optimizations or the optimization's result (if opt_id is specified).
    """
    db_connect = sqlite3.connect('optimizer.db')
    if opt_id is None:
        c = db_connect.cursor()
        res = c.execute(
        '''
            SELECT optimize_id, start_time, params, comment FROM optimizers
        ''',
        )
        for row in res:
            print '\t'.join(map(str, row))
    else:
        c = db_connect.cursor()
        res = c.execute(
        '''
            SELECT * FROM steps
            WHERE optimize_id = ?
        ''',
            (opt_id, )
        )
        for row in res:
            print '\t'.join(map(str, row))

@cli.command()
@click.option('--done', default = False, is_flag=True)
def show(done):
    """
        Shows the graphs run history.
    """
    Main().db_show(filter_done = done)

@cli.command()
@click.argument('graph_id')
def detailed(graph_id):
    """
        Shows details of one of history graphs.
    """
    Main().db_show_detailed(graph_id)

@cli.command()
@click.argument('graph_id')
def killed(graph_id):
    """
        Setup status 'killed' for graph. If you kill the process, it will not update status automatically, so it would be marked 'running'. 
    """
    Main().set_status_killed(graph_id)

@cli.command()
@click.argument('graph_id')
@click.option('--comment', required = True)
def update_comment(graph_id, comment):
    """
        Obviously, updates comment. 
    """
    m = Main()
    m.db_id = graph_id
    m.db_update_comment(comment)

if __name__ == '__main__':
    cli()
