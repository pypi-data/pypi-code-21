# -*- coding: utf-8 -*-
"""
Created on Fri Dec 23 23:24:31 2016

@author: aeloyq
"""
import numpy as np

import bokeh.plotting as plt
import bokeh.layouts as lyt
import bokeh.models as models
from bokeh.palettes import Spectral4

'''
def plot(self, costs, errors, params, roles):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pylab as plt
    x_axis = np.arange(len(costs)) + 1

    plt.figure(1)
    plt.cla()
    plt.title(nnbuilder.config.name)
    plt.ylabel('Loss')
    plt.xlabel('Epochs')
    plt.plot(x_axis, costs, label='Loss', color='orange')
    plt.legend()
    plt.savefig(self.path + 'process_cost.png')

    plt.figure(2)
    plt.cla()
    plt.title(nnbuilder.config.name)
    plt.ylabel('Error')
    plt.xlabel('Epochs')
    plt.plot(x_axis, errors, label='Error', color='blue')
    plt.legend()
    plt.savefig(self.path + 'process_error.png')

    n_im = len(params)
    a = np.int(np.sqrt(n_im))
    b = a
    if a * b < n_im: a += 1
    if a * b < n_im: b += 1
    plt.figure(3, (b * 4, a * 4))
    plt.cla()

    i = 0
    for key, param in params.items():
        i += 1
        if roles[key] is weight:
            plt.subplot(a, b, i)
            value = param
            plt.title(key + ' ' + str(value.shape))
            img = np.asarray(value)
            if img.ndim != 1:
                plt.imshow(img, cmap='gray')
        elif roles[key] is bias:
            plt.subplot(a, b, i)
            y = param
            plt.title(key + ' ' + str(y.shape))
            x_axis_bi = np.arange(y.shape[0])
            plt.plot(x_axis_bi, y, color='black')
    plt.savefig(self.path + 'paramsplot.png')

    plt.cla()
'''


def progress(name, path, loss, error, campare_saving, compare_name, valid):
    n = len(campare_saving)
    length = len(loss)
    x = list(range(length))
    tools = "pan,wheel_zoom,box_select,reset,save"
    data = dict(x=x, loss=loss, error=error)
    for i in range(n):
        save_loss = campare_saving[i]['losses']
        save_error = campare_saving[i]['errors']
        save_length = len(save_loss)
        pad_length = max(length - save_length, 0)
        data['loss' + str(i)] = save_loss[:length] + [np.nan] * pad_length
        data['error' + str(i)] = save_error[:length] + [np.nan] * pad_length
    source = models.ColumnDataSource(data=data)
    plt.output_file(path, title='Training Progress')
    p1 = plt.figure(plot_width=500, plot_height=400, y_axis_type="log", title='Loss-Epoch', tools=tools,
                    x_axis_label='n of epoch', y_axis_label='loss', active_drag='pan', active_scroll="wheel_zoom")
    for i, color in zip(range(n), Spectral4):
        p1.line('x', 'loss' + str(i), line_width=1, source=source, color=color, alpha=0.5,
                legend=compare_name[i], line_dash="dashed")
    p1.line('x', 'loss', line_width=2, source=source, color='coral', legend=name)
    p1.title.text_font_size = "25px"
    p1.legend.click_policy = "hide"
    p1.legend.location = "top_right"
    p2 = plt.figure(plot_width=500, plot_height=400, y_axis_type="log", title='Error-Epoch', tools=tools,
                    x_range=p1.x_range, x_axis_label='n of epoch', y_axis_label='error', active_drag='pan',
                    active_scroll="wheel_zoom")
    for i, color in zip(range(n), Spectral4):
        p2.line('x', 'error' + str(i), line_width=1, source=source, color=color, alpha=0.5,
                legend=compare_name[i], line_dash="dashed")
    p2.line('x', 'error', line_width=2, source=source, color='coral', legend=name)
    p2.title.text_font_size = "25px"
    p2.legend.click_policy = "hide"
    p2.legend.location = "top_right"
    p = lyt.gridplot([[p1, p2]], toolbar_location="below", merge_tools=True)
    if valid is not None:
        tab1 = models.widgets.Panel(child=p, title="Test")
        loss, error = valid[0],valid[1]
        length = len(loss)
        x = list(range(length))
        data = dict(x=x, loss=loss, error=error)
        source = models.ColumnDataSource(data=data)
        v1 = plt.figure(plot_width=500, plot_height=400, y_axis_type="log", title='Loss-Epoch', tools=tools,
                        x_axis_label='n of epoch', y_axis_label='loss', active_drag='pan', active_scroll="wheel_zoom")
        v1.line('x', 'loss', line_width=2, source=source, color='coral', legend=name)
        v1.title.text_font_size = "25px"
        v1.legend.click_policy = "hide"
        v1.legend.location = "top_right"
        v2 = plt.figure(plot_width=500, plot_height=400, y_axis_type="log", title='Error-Epoch', tools=tools,
                        x_range=v1.x_range, x_axis_label='n of epoch', y_axis_label='error', active_drag='pan',
                        active_scroll="wheel_zoom")
        v2.line('x', 'error', line_width=2, source=source, color='coral', legend=name)
        v2.title.text_font_size = "25px"
        v2.legend.click_policy = "hide"
        v2.legend.location = "top_right"
        v = lyt.gridplot([[v1, v2]], toolbar_location="below", merge_tools=True)
        tab2 = models.widgets.Panel(child=v, title="Valid")
        tabs = models.widgets.Tabs(tabs=[tab1, tab2], sizing_mode="stretch_both")
        plt.save(tabs)
    else:
        plt.save(p)
