import sys
import os
import signal
import imp
from kyroller.engine import Engine
from kyroller.strategy import Strategy
from kyroller.types import *
import argparse


def load_from_file(filepath):
    class_inst = None
    mod_name, file_ext = os.path.splitext(os.path.split(filepath)[-1])
    expected_class = mod_name
    if file_ext.lower() == '.py':
        py_mod = imp.load_source(mod_name, filepath)
    elif file_ext.lower() == '.pyc':
        py_mod = imp.load_compiled(mod_name, filepath)
    else:
        py_mod = imp.load_compiled(mod_name, filepath + '.py')

    if hasattr(py_mod, expected_class):
        class_inst = getattr(py_mod, expected_class)()

    return class_inst


def quit(signum, frame):
    print('got ctrl+c')
    os.kill(os.getpid(), signal.SIGINT)
    sys.exit()


def run():

    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)

    parser = argparse.ArgumentParser(description='回测一个策略')
    parser.add_argument('--strategy', dest='strategy', action='store',
                        help='策略文件（文件名需要和策略类相同）')

    parser.add_argument('--balance', dest='balance', action='store',
                        type=int,
                        default=1000000,
                        help='初始现金')
    parser.add_argument('--positions', dest='positions', action='store',
                        type=str, default='',
                        help='初始现金')
    parser.add_argument('--subs', dest='subs', action='store',
                        type=str,
                        help='订阅的消息')
    parser.add_argument('--start', dest='start', action='store',
                        type=str,
                        required=True,
                        help='开始时间')
    parser.add_argument('--end', dest='end', action='store',
                        required=True,
                        type=str,
                        help='结束时间')

    args = parser.parse_args()
    strategy_file = args.strategy
    balance = args.balance
    start = args.start
    end = args.end
    subs = args.subs

    def parse_position(_str):
        sp = _str.split(':')
        return Position(sp[0], int(sp[1]))

    positions = list(map(parse_position, filter(
        lambda s: len(s) > 0, args.positions.split(','))))

    strategy = load_from_file(strategy_file)
    engine = Engine(strategy=strategy)
    # 初始化余额 100w

    account = BackTestAccount(balance, 0, positions=positions)
    print('初始资产：', account)

    # 画出资产变动图表
    engine.plot_assets()

    # engine.run_realtime(
    #     subs='tick_1s.sz000002',account=account)
    # 支持
    # bar_1m.all 全市场
    # bar_1m.sz000001 单只
    # bar_1m.sz000001,bar_30s.sz000001  组合
    # 表达式  tick_1s.sz000001   tick_30s.sz000001 等

    engine.run_rollback(subs=subs, account=account,
                        start=start, end=end)
    print('end')
    engine.wait()


if __name__ == '__main__':
    run()
