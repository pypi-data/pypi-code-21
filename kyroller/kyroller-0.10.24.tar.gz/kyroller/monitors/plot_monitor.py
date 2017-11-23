
from multiprocessing import Queue, Process
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.ticker as tkr
from ..utils import humen_read_number
import datetime as dt
import time


class Monitor(Process):
    def __init__(self):
        Process.__init__(self)
        self.queue = Queue()

    def recorder_assets(self, assets_snapshot):
        self.queue.put(('asset', assets_snapshot))
        pass


class PlogMonitor(Monitor):
    def __init__(self):
        Monitor.__init__(self)
        self._assets_snapshoters = []

    def push(self, assets_snapshoter):
        if len(self._assets_snapshoters) == 0 or self._assets_snapshoters[-1] != assets_snapshoter:
            self._assets_snapshoters.append(assets_snapshoter)

    def run(self):
        import warnings
        warnings.simplefilter("ignore")
        fig = plt.figure()
        ax = fig.add_subplot(111)

        is_drawn = False
        x_size = 0
        plt.ion()
        plt.show()
        while True:
            new_x_size = len(self._assets_snapshoters)
            if new_x_size == 0:
                time.sleep(1)
                continue
            elif new_x_size == x_size:
                plt.pause(0.000001)
                continue
            x_size = new_x_size
            timestamps = [s.timestamp for s in self._assets_snapshoters]
            balances = [s.balance for s in self._assets_snapshoters]
            marker_values = [s.market_value for s in self._assets_snapshoters]
            alls = [s.all for s in self._assets_snapshoters]
            frozens = [s.frozen_balance for s in self._assets_snapshoters]
            x = [dt.datetime.fromtimestamp(ts) for ts in timestamps]
            ax.set_xlim(x[0], x[-1] + dt.timedelta(hours=1))
            if not is_drawn:
                ax.xaxis.set_major_formatter(DateFormatter("%m-%d %H:%M"))
                y_format = tkr.FuncFormatter(
                    lambda v, pos: humen_read_number(v))
                ax.yaxis.set_major_formatter(y_format)
                plt.subplots_adjust(bottom=0.2)
                plt.xticks(rotation=25)
                plt.rcParams['font.sans-serif'] = ['SimHei']
                plt.title('资产变动')
                line_balance, = ax.plot(x, balances,  linestyle='-',
                                        color='green',
                                        marker='o', markersize=1.5, label="现金")
                line_market_value, = ax.plot(x, marker_values,  linestyle='-',
                                             color='blue',
                                             marker='o', markersize=1.5, label="股票市值")
                line_all, = ax.plot(x, alls,  linestyle='-',
                                    color='red',
                                    marker='o', markersize=1.5, label="全部资产")
                line_forzen, = ax.plot(x, frozens,  linestyle='-',
                                       color='cyan',
                                       marker='o', markersize=1.5, label="冻结金额")
                ax.set_ylim(0, max(alls) * 1.2)
                plt.legend(loc='best')
                plt.xlabel = '元'
                is_drawn = True
                plt.draw()
            else:
                line_balance.set_data(x, balances)
                line_market_value.set_data(x, marker_values)
                line_all.set_data(x, alls)
                line_forzen.set_data(x, frozens)
