import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def _get_axis(ax):
    if ax is None:
        fig = plt.figure()
        ax = fig.gca(projection='3d')
    return ax


def _create_axis_from_data(z, axes=None):
    x = np.linspace(0, z.shape[0], z.shape[0])
    y = np.linspace(0, z.shape[1], z.shape[1])
    if axes is None:
        return x, y
    elif axes == 0:
        return x
    elif axes == 1:
        return y
    else:
        raise ValueError("axes must be None, 0 or 1, but is %s." % str(axes))


def _plot_matrix(x, y, z, ax, func, **kwargs):
    x = np.array(x)
    y = np.array(y)
    z = np.array(z)
    if z.ndim != 2:
        raise ValueError("Data must be 2-dimensional but is " +
                         "%d-dimensional" % z.ndim)
    if x.ndim != 1:
        raise ValueError("x-axis must be 1-dimensional but is " +
                         "%d-dimensional" % x.ndim)
    if y.ndim != 1:
        raise ValueError("y-axis must be 1-dimensional but is " +
                         "%d-dimensional" % y.ndim)
    if x.shape[0] != z.shape[0]:
        raise ValueError("First dimension of data must have the same size " +
                         "as the x-Axis.")
    if y.shape[0] != z.shape[1]:
        raise ValueError("Second dimension of data must have the same size " +
                         "as the y-Axis.")

    x, y = np.meshgrid(x, y)

    return func(x, y, z, **kwargs)


def plot_matrix_scatter(z, ax=None, **kwargs):
    ax = _get_axis(ax)
    x, y = _create_axis_from_data(z)
    return _plot_matrix(x, y, z, ax=ax, func=ax.scatter, **kwargs), ax


def plot_matrix_surface(z, ax=None, **kwargs):
    ax = _get_axis(ax)
    x, y = _create_axis_from_data(z)
    return _plot_matrix(x, y, z, ax=ax, func=ax.plot_surface, **kwargs), ax


def plot_matrix_wireframe(z, ax=None, **kwargs):
    ax = _get_axis(ax)
    x, y = _create_axis_from_data(z)
    return _plot_matrix(x, y, z, ax=ax, func=ax.plot_wireframe, **kwargs), ax


def plot_matrix_contour(z, ax=None, **kwargs):
    ax = _get_axis(ax)
    x, y = _create_axis_from_data(z)
    return _plot_matrix(x, y, z, ax=ax, func=ax.contour, **kwargs), ax


def plot_matrix_contourf(z, ax=None, **kwargs):
    ax = _get_axis(ax)
    x, y = _create_axis_from_data(z)
    return _plot_matrix(x, y, z, ax=ax, func=ax.contourf, **kwargs), ax


def plot_axis_matrix_scatter(x, y, z, ax=None, **kwargs):
    ax = _get_axis(ax)
    return _plot_matrix(x, y, z, ax=ax, func=ax.plot_scatter, **kwargs), ax


def plot_axis_matrix_surface(x, y, z, ax=None, **kwargs):
    ax = _get_axis(ax)
    return _plot_matrix(x, y, z, ax=ax, func=ax.plot_surface, **kwargs), ax


def plot_axis_matrix_wireframe(x, y, z, ax=None, **kwargs):
    ax = _get_axis(ax)
    return _plot_matrix(x, y, z, ax=ax, func=ax.plot_wireframe, **kwargs), ax


def plot_axis_matrix_contour(x, y, z, ax=None, **kwargs):
    ax = _get_axis(ax)
    return _plot_matrix(x, y, z, ax=ax, func=ax.contour, **kwargs), ax


def plot_axis_matrix_contourf(x, y, z, ax=None, **kwargs):
    ax = _get_axis(ax)
    return _plot_matrix(x, y, z, ax=ax, func=ax.contourf, **kwargs), ax
