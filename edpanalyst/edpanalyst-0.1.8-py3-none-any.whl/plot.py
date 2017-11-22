def heatmap(column_rel, **kwargs):
    """Plot a heatmap of data, probably from a column association call.

    This may be useful for other data frames, but most of the time you will
    want to call this like `edpanalyst.heatmap(popmod.mutual_information())`.
    """
    # TODO(asilvers): This probably deserves to live somewhere else, and needs
    # some helpers.
    try:
        import seaborn as sns  # type: ignore
    except ImportError:
        raise RuntimeError(
            'edpanalyst.heatmap requires that the "seaborn" python package '
            'be installed.')
    # Reset the index to get the two index columns first and second, and the
    # value column third.
    # TODO(asilvers): Check these assumptions rather than just blowing up if
    # you pass an unpexpectedly shaped data frame.
    plot_df = column_rel.fillna(0).reset_index()
    hmap = sns.clustermap(plot_df, linewidths=0.2, pivot_kws={
        'index': 'X',
        'columns': 'Y',
        'values': 'I'
    }, **kwargs)
    for l in hmap.ax_heatmap.get_yticklabels():
        l.set_rotation('horizontal')
    return hmap
