# -*- coding: utf-8 -*-

from . import FileParser as fp
import matplotlib.pyplot as plt
import glob


def plot_experiment_file(file):

    header = fp.get_header_data(file)
    df = fp.parse_experiment_file(file)

    ax = df.plot(x='elapsedtime', y='ls8')
    ax.set_title(header['Experiment Title'])
    ax.set_xlabel('Time')
    ax.set_ylabel('Light Scattering')

    plt.show()


def plot_experiment_folder(folder):
    print("Not yet implemented.")

    for filename in glob.glob(folder + '/*.csv'):
        pass


def plot_analysis_file(file):

    header = fp.get_header_data(file)
    df = fp.parse_analysis_file(file)

    ax = df.plot(x='elapsedtime', y='lightscattering')
    ax.set_title(header['Analysis Title'])
    ax.set_xlabel('Time')
    ax.set_ylabel('Light Scattering')

    plt.show()


def plot_analysis_folder(folder):
    print("Not yet implemented.")

    for filename in glob.glob(folder + '/*.csv'):
        pass

