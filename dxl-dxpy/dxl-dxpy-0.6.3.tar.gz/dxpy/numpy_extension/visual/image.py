import matplotlib.pyplot as plt
import numpy as np
from .. import image as nei


def grid_view(image_lists, windows=None, nb_column=8, scale=1.0, cmap=None, *, hide_axis=True, tight_c=0.01, return_figure=False, dpi=None, adjust_figure_size=True):
    """ subplot list of images of multiple categories into grid subplots
    Args:
        image_lists: list of [list of images or 4D tensor]
        windows: list of windows
        nb_column: columns of images
    Returns:
        Return figure if return_figure is true, else None.
    """
    nb_cata = len(image_lists)
    if windows is None:
        windows = [(None, None)] * nb_cata
    image_lists = list(map(nei.try_unbatch, image_lists))
    for i, v in enumerate(image_lists):
        if not isinstance(v, list) and isinstance(v, np.ndarray) and v.ndim == 2:
            image_lists[i] = [v]
    image_lists = [list(map(nei.fix_dim, imgs)) for imgs in image_lists]

    nb_images = max([len(imgs) for imgs in image_lists])

    nb_row = np.ceil(nb_images / nb_column) * nb_cata

    def adjust_figure_size():
        width = nb_column * scale
        height = nb_row * scale
        if adjust_figure_size:
            shapes = [(il[0].shape[1], il[0].shape[0])
                      for il in image_lists if len(il) > 0]
            w, h = zip(*shapes)
            width *= np.mean(w) / 100
            height *= np.mean(h) / 100
        return (width, height)

    if dpi is None:
        dpi = 2000.0 / adjust_figure_size()[0]
    fig = plt.figure(figsize=adjust_figure_size(), dpi=dpi)

    for k in range(nb_cata):
        for i in range(nb_images):
            if i > len(image_lists[k]):
                continue
            r = i // nb_column * nb_cata + k
            c = i % nb_column
            ax = plt.subplot(nb_row, nb_column, r * nb_column + c + 1)
            plt.imshow(image_lists[k][i], cmap=cmap,
                       vmin=windows[k][0], vmax=windows[k][1])
            if hide_axis:
                ax.get_xaxis().set_visible(False)
                ax.get_yaxis().set_visible(False)
    if isinstance(tight_c, (list, tuple)):
        h_pad, w_pad = tight_c
    else:
        h_pad = tight_c
        w_pad = tight_c
    plt.tight_layout(h_pad=h_pad, w_pad=w_pad)
    if return_figure:
        return fig
