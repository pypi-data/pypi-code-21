
from SmslsUtils.MalsRecorder import MalsDataCollector
import time, datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class MalsDataPlotter:
    stats_window = 20

    def __init__(self, data_collector):
        self.mdc = data_collector

        # setup the data graph
        self.fig = plt.figure(facecolor='0.8')
        self.ax = plt.subplot2grid((7, 1), (0, 0), rowspan=5)
        self.ax2 = plt.subplot2grid((7, 1), (6, 0), rowspan=2)
        self.plot_lines = []
        for chan in range(self.mdc.num_channels):
            line, = self.ax.plot([], [], lw=2, label='P' + str(chan+1))
            self.plot_lines.append(line)
        self.ax.grid()
        self.ax.legend(loc='upper left')
        self.ax.set_ylim(0, 100000)
        self.ax.set_xlim(0, 1)
        self.ax.set_xlabel("Time (sec)", fontsize=12)
        self.ax.set_ylabel("Optical Power (pW)", fontsize=12)
        self.ax.set_title("Real-Time Scattering Graph", fontsize=16)

        # setup the stats table
        self.table_cols = ('Gain', 'Current', 'Mean', 'Median', 'Std', 'Min', 'Max', 'SNR')
        self.table_rows = ('P1', 'P2', 'P3', 'P4', 'P5', 'P6')
        colors = [line.get_color() for line in self.plot_lines]
        cell_text = [[0.0 for x in range(len(self.table_cols))] for y in range(self.mdc.num_channels)]
        self.stats_table = plt.table(cellText=cell_text,
                          rowLabels=self.table_rows,
                          rowColours=colors,
                          colLabels=self.table_cols,
                          loc='center')
        self.ax2.axis('tight')
        self.ax2.axis('off')

    def update_plot(self, data):

        if (len(data) > 1):

            xdata = data['ElapsedTime'].values
            self.ax.set_xlim(xdata[0], xdata[-1])

            ydata = {}
            for chan in range(self.mdc.num_channels):
                pow_str = 'P' + str(chan+1)
                ydata[chan] = data[pow_str].values
                self.plot_lines[chan].set_data(xdata, ydata[chan])

                # collect stats from recent data 
                window = data[pow_str].tail(self.stats_window)
                
                mean = window.mean()
                std = window.std()
                snr = mean / std if std > 0.01 else 0

                gain_str = 'G' + str(chan+1)
                float_frmt = lambda x: round(x, 1)
                self.stats_table._cells[(chan+1,0)]._text.set_text(float_frmt(data[gain_str].iloc[-1]))
                self.stats_table._cells[(chan+1,1)]._text.set_text(float_frmt(data[pow_str].iloc[-1]))
                self.stats_table._cells[(chan+1,2)]._text.set_text(float_frmt(mean))
                self.stats_table._cells[(chan+1,3)]._text.set_text(float_frmt(window.median()))
                self.stats_table._cells[(chan+1,4)]._text.set_text(float_frmt(std))
                self.stats_table._cells[(chan+1,5)]._text.set_text(float_frmt(window.min()))
                self.stats_table._cells[(chan+1,6)]._text.set_text(float_frmt(window.max()))
                self.stats_table._cells[(chan+1,7)]._text.set_text(float_frmt(snr))
                self.stats_table.set_fontsize(14)

            return self.plot_lines, self.stats_table

    def run(self):

        self.mdc.start()

        # NOTE: mdc.update_data() is a generator function that produces data which is passed into update_plot()
        ani = animation.FuncAnimation(self.fig, self.update_plot, self.mdc.update_data, interval=self.mdc.sample_rate_ms, blit=False, repeat=False)
        plt.show()

        self.mdc.stop()


if __name__ == '__main__':
    use_hardware = False
    if use_hardware:
        port = 'COM7'
        filename = datetime.datetime.now().strftime("Mals_%Y-%m-%d_%H-%M-%S")
        filepath = './data/' + filename + ".csv"
        mdc = MalsDataCollector(port=port, filepath=filepath)
    else:
        filepath = './example.csv'
        mdc = MalsDataCollector(filepath=filepath)

    mdp = MalsDataPlotter(mdc)
    mdp.run()
