# -*- coding: utf-8 -*-
"""This module handles plotting of the statistics."""
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import font_manager, colors
from matplotlib.backends.backend_pdf import PdfPages

import numpy as np
from functools import partial
from collections import Counter, defaultdict

plt.style.use('ggplot')
plt.rcParams['legend.facecolor'] = "white" # make legends white
plt.rcParams['axes.facecolor'] = "white" # make the background white
plt.rcParams['font.size'] = 8


class Margins(dict):
    """Class to store all margin information in one place."""
    def __getattr__(self, attribute):
        return self.get(attribute)

    __setattr__ = dict.__setitem__

    __delattr__ = dict.__delitem__


def plot_locus_types_per_individual(ax, stats, bar_size, locus_type_colors):
    """Plot distribution of locus types per individual.

    Arguments:
        ax (pyplot.axes): Target plot.
        stats (StatisticsDict): The data to plot. Should be filled in output module.
        bar_size (int): Size of the bars.
        locus_type_colors (iterable): List of four colors.
    """
    # plot locus type distribution per individual as stacked barplots
    # stacking the plots is achieved by setting the left value to the cumulative
    # counts up to this point
    ax.set_title("Distribution of Locus Types per Individual")
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True)) # force xaxis to be integer

    # compute offsets for layered hbar plotting
    # the common counts are the base, homozygous mutations are layered
    # on top of the common counts and so on.
    offset_mutation_homo = [count for count in stats.transposed_type_counts["common"]]
    offset_mutation_hetero = [count_homo + offset_homo for count_homo, offset_homo in zip(stats.transposed_type_counts["mutation homozygous"], offset_mutation_homo)]
    offset_dropout = [count_hetero + offset_hetero for count_hetero, offset_hetero in zip(stats.transposed_type_counts["mutation heterozygous"], offset_mutation_hetero)]

    # assemble indices -> vertical bar positions
    locus_type_indices = np.arange(len(stats.locus_type_labels))*bar_size

    common_bars = ax.barh(
        locus_type_indices,
        stats.transposed_type_counts["common"],
        color=locus_type_colors[0],
        height=bar_size,
        tick_label=stats.locus_type_labels,
        align="center",
    )
    homozygous_bars = ax.barh(
        locus_type_indices,
        stats.transposed_type_counts["mutation homozygous"],
        left=offset_mutation_homo,
        color=locus_type_colors[1],
        height=bar_size,
        align="center",
    )
    heterozygous_bars = ax.barh(
        locus_type_indices,
        stats.transposed_type_counts["mutation heterozygous"],
        left=offset_mutation_hetero,
        color=locus_type_colors[2],
        height=bar_size,
        align="center",
    )
    dropout_bars = ax.barh(
        locus_type_indices,
        stats.transposed_type_counts["dropout"],
        left=offset_dropout,
        color=locus_type_colors[3],
        height=bar_size,
        align="center",
    )
    # put legend below the plot.
    ax.legend(
        [common_bars[0], homozygous_bars[0], heterozygous_bars[0], dropout_bars[0]],
        ["common locus", "homozygous mutations", "heterozygous mutations", "missing reads"],
        loc='upper center',
        bbox_to_anchor=(0.5, -0.2),
        ncol=2,
    )


def plot_global_locus_type_distribution(ax, stats, bar_size, locus_type_colors):
    """Plot the distribution of Locus types into one bar plot.

    Also add labels to show the exact counts for each locus type.

    Arguments:
        ax (axes): Subplot to plot into.
        stats (Stats, Namespace like dict): 
        bar_size (int):
        locus_type_colors (list of colors): 

    Returns:
        None: Plots the result into the axes object.
    """
    # plot total distribution of locus events
    ax.set_title("Global Distribution of Locus Event Types")
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True)) # force xaxis to be integer
    total_type_count_indices = np.arange(len(stats.total_type_count_labels))*bar_size
    total_type_count_bars = ax.barh(
        total_type_count_indices,
        stats.total_type_counts,
        height=bar_size,
        tick_label=stats.total_type_count_labels,
        align="center",
    )
    
    # set colors of bars to fit the mapping used for ax
    for i in range(len(stats.total_type_count_labels)):
        total_type_count_bars[3-i].set_facecolor(locus_type_colors[i])
    
    rects = ax.patches
    labels = stats.total_type_counts     # use values as labels
    for rect, label in zip(rects, labels):
        # evaluate face color fo abr
        rgb = rect.get_facecolor()
        h, s, v = colors.rgb_to_hsv(rgb[:-1])
        # set white text for dark background colors
        if v > 0.7:
            high_contrast_color = 'k' # black
        else:
            high_contrast_color = 'w' # white
        # estimate position for text (center of each bar)
        width = rect.get_width()
        height = rect.get_height()
        xpos = width / 2
        ypos = rect.get_y() + height/2
        # only show label if the value is > 0
        if label:
            ax.text(xpos, ypos, label, ha='center', va='center',
                     color=high_contrast_color)


def plot_pcr_ratios(ax, stats, bar_size, copy_rate_colors):
    """Plot pcr ratios and put labels on top."""
    ax.set_title("PCR Ratio")
    pcr_ratio_labels = ["Singletons", "HRL Reads", "Valid Reads", "All Reads"]
    pcr_ratio_indices = np.arange(len(pcr_ratio_labels))*bar_size
    valid_bars = ax.barh(
            pcr_ratio_indices,
            stats.valid_read_rates,
            height=bar_size,
            tick_label=pcr_ratio_labels,
            color=copy_rate_colors[0],
            align="center",
        )
    pcr_bars = ax.barh(
            pcr_ratio_indices,
            stats.pcr_copy_rates,
            height=bar_size,
            left=stats.valid_read_rates,
            color=copy_rate_colors[1],
            align="center",
        )
    # put legend below plot
    ax.legend(
        [valid_bars[0], pcr_bars[0]], ["Actual Reads", "PCR Duplicates"],
        loc='upper center',
        bbox_to_anchor=(0.5, -0.2),
        ncol=2,
    )
    
    rects = pcr_bars.patches
    copy_rate_labels = [round(rate, 4) if rate > 0 else "" for rate in stats.pcr_copy_rates]     # use values as labels
    for rect, label in zip(rects, copy_rate_labels):
        # evaluate lightness of the facecolor to find a 
        # label color with high contrast
        rgb = rect.get_facecolor()
        h, s, v = colors.rgb_to_hsv(rgb[:-1])
        # set white text for dark background colors
        if v > 0.7:
            high_contrast_color = 'k'
        else:
            high_contrast_color = 'w'
        # estimate position for text
        width = rect.get_width()
        height = rect.get_height()
        xpos = rect.get_x() + (width / 2)
        ypos = rect.get_y() + (height / 2)
        ax.text(xpos, ypos,  label, ha='center', va='center',
                 color=high_contrast_color)


def plot_read_origin_breakdown(ax, stats, bar_size, read_origin_colors):
    """Plot the breakdown of read origins."""
    ax.set_title("Read Origin Breakdown")
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True)) # force xaxis to be integer
    ax.margins(0,0) # prevent white spaces on top and bottom of the plot

    read_origin_indices = np.arange(len(stats.read_origin_labels))*bar_size
    origin_bars = ax.barh(
        read_origin_indices,
        stats.read_origin_counts,
        height=bar_size,
        tick_label=stats.read_origin_labels,
        align="center",
    )
    
    # set bar colors
    nr_of_labels = len(stats.read_origin_labels)
    for i in range(nr_of_labels):
        origin_bars[nr_of_labels-1-i].set_facecolor(read_origin_colors[i])
    ax.tick_params(axis="y", labelsize=7)

    rects = origin_bars.patches
    origin_labels = [rate if rate > 0 else "" for rate in stats.read_origin_counts]     # use values as labels
    for rect, label in zip(rects, origin_labels):
        # evaluate lightness of the facecolor to find a 
        # label color with high contrast
        rgb = rect.get_facecolor()
        h, s, v = colors.rgb_to_hsv(rgb[:-1])
        # set white text for dark background colors
        if v > 0.7:
            high_contrast_color = 'k'
        else:
            high_contrast_color = 'w'
        # estimate position for text
        height = rect.get_height()
        ypos = rect.get_y() + (height / 2)

        width = rect.get_width()
        # check if the bar is very slim (less than 5 percent of total width)
        if (width / ax.get_xlim()[1]) < 0.05:
            # write label right of the bar
            xpos = rect.get_x() + (width * 1.1)
            ax.text(xpos, ypos,  label, ha='left', va='center')
        else:
            # write label on the bar
            xpos = rect.get_x() + (width / 2)
            selected_color = high_contrast_color
            ax.text(xpos, ypos,  label, ha='center', va='center',
                     color=high_contrast_color)



def plot_mutations_per_individual(ax, stats, bar_size, locus_type_colors):
    """Plot the total number of mutations per individual as a horizontal barchart."""
    ax.set_title("Total number of mutations per individual")
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True)) # force xaxis to be integer
    ax.margins(0,0) # prevent white spaces on top and bottom of the plot

    individual_total_mutations_indices = np.arange(len(stats.individual_total_mutations_labels))*bar_size
    common_bars = ax.barh(
        individual_total_mutations_indices,
        stats.individual_total_mutations,
        color=locus_type_colors[1],
        height=bar_size,
        tick_label=stats.individual_total_mutations_labels,
        align="center",
    )


def plot_mean_mutation_number(ax, stats, bar_size, locus_type_colors):
    """Plot the mean nr of mutations per individual as a horizontal barchart."""
    ax.set_title("Mean number of mutations per mutation event")
    ax.margins(0,0) # prevent white spaces on top and bottom of the plot
    mean_mutations_indices = np.arange(len(stats.mean_mutations_labels))*bar_size
    common_bars = ax.barh(
        mean_mutations_indices,
        stats.mean_mutations_per_event,
        color=locus_type_colors[1],
        height=bar_size,
        tick_label=stats.mean_mutations_labels,
        align="center",
    )
    # plot the total dataset mean as a dashed line
    total_mean_line = ax.axvline(
        stats.total_mutations_mean,
        color=locus_type_colors[3],
        lw=1.5,
        ls="dashed",
    )
    # code to place mean value as label
    label="Mean: {:.2f}".format(stats.total_mutations_mean)
    ax.text(
        stats.total_mutations_mean * 0.99,
        ax.get_ylim()[0] + 1.5,
        label,
        ha='right',
        va='center',
        color=locus_type_colors[3],
        )


def plot_allele_nr_distribution(ax, stats, bar_size, locus_type_colors):
    """Plot the distribution of the number of alleles over all loci."""
    ax.set_title("Distribution of #Different Alleles per Locus")
    labels, values = zip(*stats.alleles_per_locus.items())
    indexes = np.arange(len(labels))
    ax.margins(0,0) # prevent white spaces on top and bottom of the plot
    nice_labels = ["{} Alleles".format(c) if c > 1 else "{} Allele".format(c) for c in labels]

    allele_count_bars = ax.barh(
        indexes,
        list(reversed(values)),
        color=locus_type_colors[1],
        height=1,
        tick_label=list(reversed(nice_labels)),
        align="center",
    )
    ax.set_xlabel('Number of Loci')
    mean_nr_alleles = sum([value * count for value, count in stats.alleles_per_locus.items()]) / stats.nr_loci


def plot_coverage_distribution(ax, stats):
    """
    """
    ax.set_title("Distribution of Individual Coverage Values")
    size = max(stats.valid_coverage_distribution)
    stats.valid_coverage_distribution[0] = 0  # remove loci dropping out by mutations
    ax.hist(
        list(stats.valid_coverage_distribution.keys()),
        weights=list(stats.valid_coverage_distribution.values()),
        bins=range(size+5),
        color="#1d91c0", # dark petrol
        )
    ax.set_xlabel('Coverage')
    ax.set_ylabel('Nr of Loci')


def plot_statistics(stats, conf, args, paths):
    """Assemble data for overview page.
    """
    # determine number of individuals
    if args.nr_individuals <= 6:
        nr_pages = 2
    elif args.nr_individuals <= 30:
        nr_pages = 4
    else:
        nr_pages = "many"

    # size of a4 paper in inches
    a5_portrait = (5.845, 8.27)
    a5_landscape = (8.27, 5.842)
    a4_portrait = (8.27, 11.69)
    a4_landscape = (11.69, 8.27)
    a2_portrait = (16.53, 23.39)
    a2_landscape = (23.39, 16.53)
    margins = Margins(left=0.24, wspace=0.2, hspace=1.1,
                      bottom=0.0, top=0.925)

    def a4_pages(x):
        return (8.27, x * 11.69)
    # set size of the bars
    # this can be overruled by matplotlib setting the graphics size
    bar_size = 10
    # try to use a decent font. If sans is not installed
    # this will default to Vera Sans
    matplotlib.rc('font', family='sans')

    # size of page headers
    title_size = 13

    # yellow - light green - petrol - blue
    # from colorbrew2.org
    locus_type_colors = [
        "#ffffcc", # yellow
        "#a1dab4", # light green
        "#41b6c4", # light petrol
        "#225ea8", # blue
        ]
    copy_rate_colors = [
        "#ffffcc", # yellow
        "#1d91c0", # dark petrol
        ]
    read_origin_colors = [
        "#ffffcc", # yellow
        "#a1dab4", # light green
        "#41b6c4", # light petrol
        "#225ea8", # blue
        "#41b6c4", # light petrol
        "#225ea8", # blue
        ]


    if nr_pages == 2:
        with PdfPages(paths.statistics) as pdf:
            # create figure
            fig = plt.figure(figsize=a4_portrait)
            fig.suptitle("Dataset Statistics", fontsize=title_size)
            rows, columns = (5, 1)
            ax1 = plt.subplot(rows, columns, 1) # Subplot for distribution of types per individual
            ax2 = plt.subplot(rows, columns, 2) # Subplot of total distribution
            ax3 = plt.subplot(rows, columns, 3) # Subplot for PCR ratios
            ax4 = plt.subplot(rows, columns, 4) # Subplot for read origin
        
            plt.subplots_adjust(left=margins.left, wspace=margins.wspace,
                                hspace=margins.hspace, bottom=margins.bottom,
                                top=margins.top)
        
            plot_locus_types_per_individual(ax1, stats, bar_size, locus_type_colors)
            plot_global_locus_type_distribution(ax2, stats, bar_size, locus_type_colors)
            plot_pcr_ratios(ax3, stats, bar_size, copy_rate_colors)
            plot_read_origin_breakdown(ax4, stats, bar_size, read_origin_colors)
    
            # take a look at the tight_layout function
            pdf.savefig(bbox_inches='tight') # save first pdf page and start a new one
            plt.close()
    
    
            fig = plt.figure(figsize=a4_portrait)
            fig.suptitle("Dataset Statistics", fontsize=title_size)
            rows, columns = (4, 1)
            ax5 = plt.subplot(rows, columns, 1) # total number of mutations per individual
            ax6 = plt.subplot(rows, columns, 2) # mean nr of mutations per event
            ax7 = plt.subplot(rows, columns, 3) # 
            ax8 = plt.subplot(rows, columns, 4) # 
            plt.subplots_adjust(left=margins.left, wspace=margins.wspace,
                                hspace=margins.hspace, bottom=margins.bottom,
                                top=margins.top)
    
            plot_mutations_per_individual(ax5, stats, bar_size, locus_type_colors)
            plot_mean_mutation_number(ax6, stats, bar_size, locus_type_colors)
            plot_allele_nr_distribution(ax7, stats, bar_size, locus_type_colors)
            plot_coverage_distribution(ax8, stats)
    
            pdf.savefig(bbox_inches='tight') # save second page
            plt.close()

    elif nr_pages == 4:
        # four pages
        with PdfPages(paths.statistics) as pdf:
            # create figures for page 1
            fig = plt.figure(figsize=a4_portrait)
            fig.suptitle("Dataset Statistics", fontsize=title_size)
            rows, columns = (2, 1)
            ax1 = plt.subplot(rows, columns, 1) # Subplot for distribution of types per individual
            ax2 = plt.subplot(rows, columns, 2) # Subplot of total distribution
        
            plt.subplots_adjust(left=margins.left, wspace=margins.wspace,
                                hspace=margins.hspace, bottom=margins.bottom,
                                top=margins.top)
        
            plot_locus_types_per_individual(ax1, stats, bar_size, locus_type_colors)
            plot_global_locus_type_distribution(ax2, stats, bar_size, locus_type_colors)
    
            # take a look at the tight_layout function
            pdf.savefig(bbox_inches='tight') # save first pdf page and start a new one
            plt.close()

            # create figures for page 2
            fig = plt.figure(figsize=a4_portrait)
            fig.suptitle("Dataset Statistics", fontsize=title_size)
            rows, columns = (2, 1)
            ax3 = plt.subplot(rows, columns, 1) # Subplot for PCR ratios
            ax4 = plt.subplot(rows, columns, 2) # Subplot for read origin
        
            plt.subplots_adjust(left=margins.left, wspace=margins.wspace,
                                hspace=margins.hspace, bottom=margins.bottom,
                                top=margins.top)
        
            plot_pcr_ratios(ax3, stats, bar_size, copy_rate_colors)
            plot_read_origin_breakdown(ax4, stats, bar_size, read_origin_colors)
    
            # take a look at the tight_layout function
            pdf.savefig(bbox_inches='tight') # save first pdf page and start a new one
            plt.close()
    
            # create figures for page 3
            fig = plt.figure(figsize=a4_portrait)
            fig.suptitle("Dataset Statistics", fontsize=title_size)
            rows, columns = (2, 1)
            ax5 = plt.subplot(rows, columns, 1) # total number of mutations per individual
            ax6 = plt.subplot(rows, columns, 2) # mean nr of mutations per event
            plt.subplots_adjust(left=margins.left, wspace=margins.wspace,
                                hspace=margins.hspace, bottom=margins.bottom,
                                top=margins.top)
    
            plot_mutations_per_individual(ax5, stats, bar_size, locus_type_colors)
            plot_mean_mutation_number(ax6, stats, bar_size, locus_type_colors)
    
            pdf.savefig(bbox_inches='tight') # save second page
            plt.close()

            # create figures for page 4
            fig = plt.figure(figsize=a4_portrait)
            fig.suptitle("Dataset Statistics", fontsize=title_size)
            rows, columns = (2, 1)
            ax7 = plt.subplot(rows, columns, 1) # distribution of null alleles
            ax8 = plt.subplot(rows, columns, 2) # free
            plt.subplots_adjust(left=margins.left, wspace=margins.wspace,
                                hspace=margins.hspace, bottom=margins.bottom,
                                top=margins.top)

            plot_allele_nr_distribution(ax7, stats, bar_size, locus_type_colors)
            plot_coverage_distribution(ax8, stats)
    
            pdf.savefig(bbox_inches='tight') # save second page
            plt.close()
    else:
        # handle large individual sizes
        # 60 datasets comfortably fit on a page
        blocks, rest = divmod(args.nr_individuals, 60)
        if rest:
            blocks += 1
        long_page = a4_pages(blocks)

        long_margins = Margins(left=0.24, wspace=0.2, hspace=0.5,
                               bottom=1.0, top=1.0)
        with PdfPages(paths.statistics) as pdf:
            # create figures for page 1
            fig = plt.figure(figsize=long_page)
            fig.suptitle("Dataset Statistics", fontsize=title_size)
            rows, columns = (1, 1)
            ax1 = plt.subplot(rows, columns, 1) # Subplot for distribution of types per individual

            # plt.subplots_adjust(left=long_margins.left, wspace=long_margins.wspace,
            #                     hspace=long_margins.hspace, bottom=long_margins.bottom,
            #                     top=long_margins.top)
        
            plt.tight_layout()
            plot_locus_types_per_individual(ax1, stats, bar_size, locus_type_colors)
            # take a look at the tight_layout function
            pdf.savefig(bbox_inches='tight') # save first pdf page and start a new one
            plt.close()

            fig = plt.figure(figsize=a5_portrait)
            fig.suptitle("Dataset Statistics", fontsize=title_size)
            rows, columns = (1, 1)
            ax1 = plt.subplot(rows, columns, 1) # Subplot for distribution of types per individual

        
            plt.subplots_adjust(left=margins.left, wspace=margins.wspace,
                                hspace=margins.hspace, bottom=margins.bottom,
                                top=margins.top)
            ax2 = plt.subplot(rows, columns, 1) # Subplot of total distribution
            plot_global_locus_type_distribution(ax2, stats, bar_size, locus_type_colors)
    
            # take a look at the tight_layout function
            pdf.savefig(bbox_inches='tight') # save first pdf page and start a new one
            plt.close()

            # create figures for page 2
            fig = plt.figure(figsize=a4_portrait)
            fig.suptitle("Dataset Statistics", fontsize=title_size)
            rows, columns = (2, 1)
            ax3 = plt.subplot(rows, columns, 1) # Subplot for PCR ratios
            ax4 = plt.subplot(rows, columns, 2) # Subplot for read origin
        
            plt.subplots_adjust(left=margins.left, wspace=margins.wspace,
                                hspace=margins.hspace, bottom=margins.bottom,
                                top=margins.top)
        
            plot_pcr_ratios(ax3, stats, bar_size, copy_rate_colors)
            plot_read_origin_breakdown(ax4, stats, bar_size, read_origin_colors)
    
            # take a look at the tight_layout function
            pdf.savefig(bbox_inches='tight') # save first pdf page and start a new one
            plt.close()
    
            # create figures for page 3
            fig = plt.figure(figsize=long_page)
            fig.suptitle("Dataset Statistics", fontsize=title_size)
            rows, columns = (1, 1)
            ax5 = plt.subplot(rows, columns, 1) # total number of mutations per individual
            plot_mutations_per_individual(ax5, stats, bar_size, locus_type_colors)
            pdf.savefig(bbox_inches='tight') # save second page
            plt.close()

            fig = plt.figure(figsize=long_page)
            fig.suptitle("Dataset Statistics", fontsize=title_size)
            rows, columns = (1, 1)
            ax6 = plt.subplot(rows, columns, 1) # mean nr of mutations per event
            plt.subplots_adjust(left=margins.left, wspace=margins.wspace,
                                hspace=margins.hspace, bottom=margins.bottom,
                                top=margins.top)
            plot_mean_mutation_number(ax6, stats, bar_size, locus_type_colors)
    
            pdf.savefig(bbox_inches='tight') # save second page
            plt.close()

            # create figures for page 4
            fig = plt.figure(figsize=a4_portrait)
            fig.suptitle("Dataset Statistics", fontsize=title_size)
            rows, columns = (2, 1)
            ax7 = plt.subplot(rows, columns, 1) # distribution of null alleles
            ax8 = plt.subplot(rows, columns, 2) # free
            plt.subplots_adjust(left=margins.left, wspace=margins.wspace,
                                hspace=margins.hspace, bottom=margins.bottom,
                                top=margins.top)

            plot_allele_nr_distribution(ax7, stats, bar_size, locus_type_colors)
            plot_coverage_distribution(ax8, stats)
    
            pdf.savefig(bbox_inches='tight') # save second page
            plt.close()
