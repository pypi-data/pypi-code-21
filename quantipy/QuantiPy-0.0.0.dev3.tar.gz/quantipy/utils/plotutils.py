# -*- coding: utf-8 -*-

def _kwtolegkw(kwargs=None):
    """
    Remove legend keywords from kwargs and return them as separate dictionary!

    :type kwargs: dict
    :param kwargs: Keyword arguments of a function.
    :rtype: (dict,dict)
    :returns: kwargs without legend kwargs, legend kwargs
    """
    if not kwargs==None:
        legkwlist = ['loc', 'bbox_to_anchor', 'ncol', 'fontsize', 'fancybox',
            'shadow', 'mode', 'labelspacing', 'columnspacing', 'borderpad', 
            'handlelength','handleheight', 'handletextpad', 'borderaxespad',
            'bbox_transform', 'title', 'shadow', 'numpoints','scatterpoints',]
        legkwargs = {}
        plotkwargs = {}
        for kw in kwargs:
            if kw in legkwlist:
                legkwargs[kw] = kwargs[kw]
            else:
                plotkwargs[kw] = kwargs[kw]
        if not 'loc' in legkwargs:
            legkwargs['loc'] = 1
        
        return plotkwargs, legkwargs

    else:
        return None, None

