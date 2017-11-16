from .layout import active_frame


def kwargs_pop_dataset(**kwargs):
    frame, dataset = kwargs.pop('frame', None), kwargs.pop('dataset', None)
    if dataset is None:
        if frame is None:
            frame = active_frame()
        dataset = frame.dataset
    elif frame is None:
        frame = dataset.frame
    else:
        assert frame.dataset == dataset
    return frame,dataset, kwargs


def kwargs_pop_frame(**kwargs):
    frame = kwargs.pop('frame', active_frame())
    return frame, kwargs


def kwargs_pop_plot(**kwargs):
    frame, plot = kwargs.pop('frame', None), kwargs.pop('plot', None)
    if plot is None:
        if frame is None:
            frame = active_frame()
        plot = frame.plot()
    elif plot is None:
        plot = frame.plot()
    else:
        assert frame.plot() == plot
    return frame, plot, kwargs
