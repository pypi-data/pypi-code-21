# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('QT4Agg')
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import sys
reload(sys)
sys.setdefaultencoding('utf8')
matplotlib.rcParams['agg.path.chunksize'] = 10000


def qc_plots(measurement_group, output_dir,
             start_date, end_date, w, tz):
    """Write PDF of all measurements in Measurement Group

       :param MeasurementGroup measurement_group: MeasurementGroup object to QC
       :param str output_dir: Path to directory where PDF file is written
                              (excluding file name, file name taken from
                              MeasurementGroup object)
       :param str start_date: Left x-axis bound of plots
       :param str end_date: Right x-axis bound of plots
       :param str w: Sampling frequency of data
       :param str tz: Time zone of data
       """
    fig_list = list()
    concat_method = measurement_group.concat_method
    start = pd.to_datetime(start_date).tz_localize(tz)
    end = pd.to_datetime(end_date).tz_localize(tz)
    if concat_method == 'concat_measurements':
        for m in measurement_group.meas_list:
            ts = m.data.loc[start:end]
            if ts.empty:
                print ('No data recorded during metering period for ' +
                       m.meas_des)
            else:
                ts = ts.resample(w).mean()
                fig = plt.figure()
                if 'State' in m.quant:
                    plt.step(ts.index, ts.values, color='b', rasterized=True,
                             label=m.label)
                    plt.ylim(top=1.1, bottom=-0.1)
                    plt.scatter(start, ts.min(), marker='x', color='k', s=60,
                                label='Start/End of Metering Period')
                    plt.scatter(end, ts.min(), marker='x', color='k', s=60)
                elif 'Counts' in m.quant:
                    plt.plot(ts, color='b', rasterized=True, label=m.label)
                    plt.ylim(bottom=-1)
                    plt.scatter(start, ts.min(), marker='x', color='k', s=60,
                                label='Start/End of Metering Period')
                    plt.scatter(end, ts.min(), marker='x', color='k', s=60)
                elif 'Monthly' in m.label:
                    plt.scatter(ts.index, ts.values, color='b',
                                rasterized=True, label=m.label)
                    plt.scatter(start, ts.min(), marker='x', color='k', s=60,
                                label='Start/End of Metering Period')
                    plt.scatter(end, ts.min(), marker='x', color='k', s=60)
                else:
                    plt.plot(ts.index, ts.values, color='b',
                             rasterized=True, label=m.label)
                    plt.scatter(start, ts.min(), marker='x', color='k', s=60,
                                label='Start/End of Metering Period')
                    plt.scatter(end, ts.min(), marker='x', color='k', s=60)
                mng = plt.get_current_fig_manager()
                mng.window.showMaximized()
                plt.title(m.name.split('_')[0])
                plt.legend(loc='upper right', scatterpoints=1)
                plt.ylabel(m.quant + ' ' + '[' + m.dim + ']')
                plt.xlabel('Time')
                plt.grid()
                fig_list.extend(
                    [manager.canvas.figure
                     for manager in
                     matplotlib._pylab_helpers.Gcf.get_all_fig_managers()])
                plt.close('all')
    elif concat_method == 'concat_dataframes':
        for column_name in measurement_group.meas_df:
            mng = plt.get_current_fig_manager()
            mng.window.showMaximized()
            plt.plot(measurement_group.meas_df[column_name], color='b',
                     rasterized=True)
            plt.title(column_name)
            plt.xlabel('Time')
            plt.grid()
            fig_list.extend(
                [manager.canvas.figure
                 for manager in
                 matplotlib._pylab_helpers.Gcf.get_all_fig_managers()])
            plt.close('all')
    pdf_path = output_dir + '\\' + measurement_group.name + ' QC Plots.pdf'
    pdf = PdfPages(pdf_path)
    for fig in fig_list:
        pdf.savefig(fig)
    pdf.close()
