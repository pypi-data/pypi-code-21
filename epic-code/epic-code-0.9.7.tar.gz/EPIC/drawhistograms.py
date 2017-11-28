from __future__ import print_function 
import numpy as np
import itertools
import time
import os, sys
import collections
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import cm
import click
from EPIC import common
import scipy.stats as st
import scipy.interpolate as interpolate

try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    input = raw_input
except NameError:
    pass

plt.rcParams['axes.linewidth'] = 0.5
#plt.rcParams['text.latex.unicode'] = True
#plt.rcParams['font.serif'] = 'Palatino'
#plt.rcParams['legend.fontsize'] = 'medium'
plt.rcParams['xtick.top'] = True
plt.rcParams['ytick.right'] = True
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
plt.rcParams['xtick.major.width'] = 0.5
plt.rcParams['ytick.major.width'] = 0.5

class Histogram(object):
    def __init__(self):
        pass

class TrueFit(object):
    def __init__(self, weight, mu, sigma):
        self.weight = weight
        self.mu = mu
        self.sigma = sigma

def preparehistogram(H, b, w, vmin, vmax, parname, mhist=None, crange=False, smooth_hist=False):
    if mhist:
        if crange:
            h = common.normalize(H, (0, mhist), newlims=crange)
        else:
            h = common.normalize(H, (0, mhist), newlims=(vmin, vmax))
    else:
        h = H

    if smooth_hist:
        x = np.loadtxt(os.path.join(smooth_hist, '..', 'kde_estimates', 'kde_support-%s.txt' % parname))
        y = np.loadtxt(os.path.join(smooth_hist, '..', 'kde_estimates', 'kde_density-%s.txt' % parname))
        if mhist:
            if crange:
                y = common.normalize(y, (0, mhist), newlims=crange)
            else:
                y = common.normalize(y, (0, mhist), newlims=(vmin, vmax))
        else:
            pass
        # old interpolation (deprecated)
        #X = b[:-1] + w/2
        #X = np.concatenate(([b[0]-w[0]/2,], X, [b[-1]+w[-1]/2,]))
        #Y = np.concatenate(([vmin], h, [vmin]))
        #y = interpolate.interp1d(X, Y, kind=smooth_hist)
        #x = np.linspace(b[0]-w[0]/2, b[-1]+w[-1]/2, 150)

    else:
        x = None
        y = None

    hx = np.ravel(list(zip(b[:-1], b[:-1]+w)))
    hy = np.ravel(list(zip(h, h)))
    hx = np.concatenate(([hx[0]], hx, [hx[-1]]))
    hy = np.concatenate(([vmin], hy, [vmin]))

    return x, y, hx, hy
        
def draw_on_axes(listdirlen, parname, customunits, ax, smooth_hist, hist_properties, title_above=True, MHIST=None, CRANGE=False, UseTex=False, title_pos='upper right', fontsize=8, args=None):

    if args:
        title_pos = common.lookarg1list('title_pos=', args)
        if title_pos:
            dict_title = {}
            for pos in title_pos:
                par, side = pos.split(':')
                dict_title[par] = 'upper %s' % side

            title_pos = parname in dict_title and dict_title[parname]
        title_pos = title_pos or 'upper right'

        bfmark = common.lookarg1('bf=', args)

        fontsize = common.lookarg1('fontsize=', args, instance=int) or fontsize

    fcolor = hist_properties.color
    from common import alphas
    if listdirlen > 1:
        alphas = [0.40, 0.25, 0.10]

    nrange = CRANGE or (hist_properties.vmin, hist_properties.vmax)
    dx = (hist_properties.separators[-1] - hist_properties.separators[0])/(hist_properties.separators.size-1)

    def HIST(X, mhist):
        d, m = divmod(X - hist_properties.separators[0], dx)
        i = int(round(d))
        try:
            c = hist_properties.count[i]/hist_properties.norm
        except IndexError:
            assert i == len(hist_properties.count)
            c = hist_properties.count[i-1]/hist_properties.norm
        if not mhist:
            mhist = max(hist_properties.count)*1.15
        return common.normalize(c, (0, mhist), newlims=nrange)

    if listdirlen == 1:
        if smooth_hist:
            x, Hx = smooth_hist
            #Hx = interpolate.interp1d(x, Hx)
            #x = np.linspace(x[0], x[-1], num=5500)
            #Hx = Hx(x)
        else:
            x = np.linspace(hist_properties.separators[0], hist_properties.separators[-1], num=400)
            Hx = np.array([HIST(X,MHIST) for X in x])

        for sigma_up, alpha in zip(hist_properties.sigma_up, alphas):
            sigma_lim = common.normalize(sigma_up/hist_properties.norm, (0, MHIST), newlims=nrange)
            shadedregion = np.where(Hx > sigma_lim, True, False)
            ax.fill_between(x, hist_properties.vmin, Hx, where=shadedregion, facecolor=fcolor, linewidth=0.0, alpha=alpha) # 0 -> hist_properties.vmin

        if bfmark:
            h1 = ax.axvline(hist_properties.bestfit, linestyle='-', lw=0.3, color=(0.6, 0.6, 0.6))
        ax.set_xlim(hist_properties.vmin, hist_properties.vmax) 
        ax.set_xticks(np.linspace(hist_properties.vmin, hist_properties.vmax, num=4))
    else:
        if bfmark:
            h1 = ax.axvline(hist_properties.bestfit, linestyle='-', lw=0.3, color=fcolor)
        else:
            pass

    #ym, yM = ax.get_ylim()
    #ax.set_yticks(np.linspace(ym,yM, num=5))
    ax.tick_params(left='off', right='off')

    formatted_title = format_title(hist_properties.tex, customunits, parname, UseTex=UseTex)
    if title_above:
        ax.set_title(formatted_title, fontdict={'fontsize': fontsize})
    else:
        # title inside
        invisible_handle = mpatches.Patch(linewidth=0, label=formatted_title)
        ax.legend(loc=title_pos, handles=[invisible_handle,], frameon=False, borderaxespad=0.5, handlelength=0, handletextpad=0)

def format_title(texstring, customunits, parname, UseTex=False):
    if customunits and (parname in customunits):
        log10unit = customunits[parname]
        if log10unit <= 2:
            return r'$p(%i \, %s \mid D)$' % (10**log10unit, texstring)
        else:
            return r'$p(10^{%i} \, %s \mid D)$' % (log10unit, texstring)
    else:
        return r'$p(%s \mid D)$' % texstring

def make_histograms(nparams, parnames, tex, listwdir, bar, priors=None, derived=False, listofcolors=['C%i' % i for i in range(10) if not i==3]+['C3'], singlecolor=['C0'], nocustomunits=False, FMT=5, LEVELS=[1, 2], smooth=None, CFONT=None, args=None):
    #plt.rcParams['font.size'] = 14 # was 11
    #plt.rcParams['figure.figsize'] = 4.5, 3.5

    if args:
        # The default color for the histograms is red. It can be changed to any
        # other of your like.
        singlecolor = common.lookarg1list('singlecolor=', args) or singlecolor

        # a custom list of colors for multiple plots can be passed as a list of strings
        listofcolors = common.lookarg1list('colors=', args) or listofcolors

        smooth = common.lookarg1('smooth_hist=', args) or smooth

        # One can disable customunits although it is unlikely this will be used
        nocustomunits = common.lookarg('nocustomunits', args) or nocustomunits

        FMT = common.lookarg1('fmt=', args, instance=int) or FMT
        LEVELS = common.lookarg1list('levels=', args, instance=int) or LEVELS

        CFONT = common.lookarg1('font=', args) or CFONT

    inifile = common.get_inifile_name(os.path.join(listwdir[0], '..', '..', derived and '..' or ''))
    customunits = determine_customunits(args, inifile, nocustomunits)

    list_hist_properties = []
    if len(listwdir) > 1:
        mcolors = itertools.cycle(listofcolors)
    else:
        mcolors = itertools.cycle(singlecolor)

    for wdir in listwdir:
        #bestfit = np.loadtxt(os.path.join(os.path.split(wdir.rstrip('\\').rstrip(os.pathsep).rstrip('/'))[0], 'bf.txt'), ndmin=1)
        bestfit = np.loadtxt(os.path.join(wdir, '..', 'bf.txt'), ndmin=1)
        results_hist_table = common.create_tex_table(os.path.join(wdir, 'hist_table.tex'), cfont=CFONT)
        common.table_headings(results_hist_table, levels=LEVELS)
        if smooth and smooth.lower() in ['kde', 'kde1', 'kdh']:
            results_kde_table = common.create_tex_table(os.path.join(wdir, '..', 'kde_estimates', 'kde_table.tex'), cfont=CFONT)
            common.table_headings(results_kde_table, levels=LEVELS)
        normal_kde_filename = os.path.join(wdir, derived and '..' or '', '..', '..', 'normal_kde.txt')
        if os.path.isfile(normal_kde_filename):
            with open(normal_kde_filename, 'r') as nkde_file:
                normal_kde = nkde_file.readlines()
            normal_kde = [nkde.strip() for nkde in normal_kde]
        else:
            normal_kde = []
        hist_properties = {}
        mcor = next(mcolors)
        par_fits = np.loadtxt(os.path.join(wdir, derived and '..' or '', '..', derived and 'der_par_fits.txt' or 'par_fits.txt'))
        for i, par in enumerate(parnames):
            try:
                count = np.loadtxt(os.path.join(wdir, 'doacount-%s.txt' % par))
                seps = np.loadtxt(os.path.join(wdir, 'seps-%s.txt' % par))
                normalization = float(np.loadtxt(os.path.join(wdir, 'normalization-%s.txt' % par)))

                UNIT = 10**customunits[par] if (customunits and par in customunits) else 1

                sigmasCL, sigma_up = common.get_1D_confidence_regions(count, seps, parfit=par_fits[i], fmt=FMT, unit=UNIT, levels=LEVELS, normal=par in normal_kde)
                prior = not derived and priors[par] or ''
                common.append_distribution_parameters_to_tex(results_hist_table, tex[par], bestfit[i], sigmasCL, prior=prior, unit=UNIT, fmt=FMT)

                if smooth and smooth.lower() in ['kde', 'kde1', 'kdh']:
                    kde_support = np.loadtxt(os.path.join(wdir, '..', 'kde_estimates', 'kde_support-%s.txt' % par))
                    kde_density = np.loadtxt(os.path.join(wdir, '..', 'kde_estimates', 'kde_density-%s.txt' % par))
                    kde_sigmasCL, sigma_up = common.get_1D_confidence_regions(kde_density, kde_support, parfit=par_fits[i], fmt=FMT, unit=UNIT, levels=LEVELS, normal=par in normal_kde)
                    sigma_up *= normalization
                    common.append_distribution_parameters_to_tex(results_kde_table, tex[par], bestfit[i], kde_sigmasCL, prior=prior, unit=UNIT, fmt=FMT)

                try:
                    xvmin = prior.vmin
                    xvmax = prior.vmax 
                except AttributeError: # not derived
                    xvmin = seps[0] - 0.15*(seps[-1] - seps[0])
                    xvmax = seps[-1] + 0.15*(seps[-1] - seps[0])

                hist_properties[par] = Histogram()
                hist_properties[par].count = count
                hist_properties[par].separators = seps
                hist_properties[par].norm = normalization
                hist_properties[par].color = mcor
                hist_properties[par].bestfit = bestfit[i]
                hist_properties[par].tex = tex[par]
                hist_properties[par].vmin = xvmin
                hist_properties[par].vmax = xvmax
                hist_properties[par].parname = par
                hist_properties[par].sigma_up = sigma_up

            except (IOError, IndexError, KeyError):
                pass
                #print('!!! Some error with parameter %s.' % par)

            bar.update(1)

        common.close_tex(results_hist_table)
        if smooth and smooth.lower() in ['kde', 'kde1', 'kdh']:
            common.close_tex(results_kde_table)
        list_hist_properties.append(hist_properties)

    return list_hist_properties

def der_drawhistograms(parnames, fig, ax, tex, listwdir, list_hist_properties, bar, nocustomticks=False, nocustomrange=False, nocustomunits=False, smooth=False, show_gaussian_fit=False, show_hist=False, UseTex=False, gname=False, png=False, fontsize=8, args=None):

    if args:
        # a custom range for the plots can be specified with a .range file.
        # However, it can be disabled without having to delete or rename this file,
        # using the flat nocustomrange. With multiple workingidr, nocustomrange
        # will be True so it helps visualizing different distributions. After then
        # the user can decide for a custom range but needs to inform this option
        # via range=Och2:0.02,0.03... in the command arguments
        nocustomrange = common.lookarg('nocustomrange', args) or nocustomrange
        nocustomrange = nocustomrange or len(listwdir) > 1

        # One can also bypass custom ticks file (.ticks) with the nocustomticks
        # flag, which will also happen automatically with more than one workingdir.
        # This can be overwritten again from the command with
        # ticks=Och2:0.02,0.022,0.024.. and will also have effect any time customrange is bypassed.
        nocustomticks = common.lookarg('nocustomticks', args) or nocustomticks
        nocustomticks = nocustomticks or len(listwdir) > 1

        # One can disable customunits although it is unlikely this will be used
        nocustomunits = common.lookarg('nocustomunits', args) or nocustomunits

        # Draw smooth histogram?
        smooth = common.lookarg1('smooth_hist=', args) or smooth

        # plot the pdf of the fitted Gaussians
        show_gaussian_fit = common.lookarg('show_gaussian_fit', args) or show_gaussian_fit
        show_hist = common.lookarg('show_hist', args) or show_hist

        #whether to use Tex or not
        UseTex = common.lookarg('usetex', args) or UseTex

        # a custom name for the grid file can be given with gname to avoid
        # overwriting in a later moment
        gname = common.lookarg1('gname=', args) or gname
        png = common.lookarg('png', args) or png

        fontsize = common.lookarg1('fontsize=', args, instance=int) or fontsize

    plt.rcParams['font.size'] = fontsize

    # when more than 1 result plotted together, can only set range manually
    # (range=Odh2:0.2_0.4,Obh2=0.01_0.03, ...)
    inifile = common.get_inifile_name(os.path.join(listwdir[0], '..', '..', '..'))
    nocustomticks = nocustomrange or nocustomticks
    customticks = determine_customticks(args, inifile, not nocustomticks)
    customunits = determine_customunits(args, inifile, nocustomunits)
    customrange = determine_customrange(args, inifile, nocustomrange)

    if show_gaussian_fit:
        mu = {}
        sigma = {}
        for wdir in listwdir:
            mu[wdir], sigma[wdir] = np.loadtxt(os.path.join(wdir, '..', '..', 'der_par_fits.txt'), unpack=True)
            if isinstance(mu[wdir], float):
                mu[wdir] = [mu[wdir],]
            if isinstance(sigma[wdir], float):
                sigma[wdir] = [sigma[wdir],]

    for i, par in enumerate(parnames):
        comboH, combob, combow = {}, {}, {}
        notallwdir = []
        for wdir in listwdir:
            try:
                comboH[wdir] = np.loadtxt(os.path.join(wdir, 'combocount-%s.txt' % par))
                combob[wdir] = np.loadtxt(os.path.join(wdir, 'comboseps-%s.txt' % par))
                combow[wdir] = np.loadtxt(os.path.join(wdir, 'combowidths-%s.txt' % par))
                notallwdir.append(wdir)
            except:
                pass
        if smooth and smooth.lower() in ['kde', 'kde1', 'kdh']:
            mhist = 1.15 * max([np.loadtxt(os.path.join(wdir, '..', 'kde_estimates', 'kde_density-%s.txt' % par)).max() for wdir in notallwdir])
        else:
            mhist = 1.15 * max([comboH[wdir].max() for wdir in notallwdir])
        assert len(notallwdir) == len(list_hist_properties)
        xyvmin = min([hist_properties[par].vmin for hist_properties in list_hist_properties])
        xyvmax = max([hist_properties[par].vmax for hist_properties in list_hist_properties])
        for wdir, hist_properties in zip(notallwdir, list_hist_properties):
            ax[i].set_ylim(xyvmin, xyvmax) #0, mhist)
            #vmin, vmax = ax[i].get_ylim()
            x, y, hx, hy = preparehistogram(comboH[wdir], combob[wdir], combow[wdir], xyvmin, xyvmax, par, mhist=mhist, crange=False, smooth_hist=smooth and smooth.lower() in ['kde', 'kde1', 'kdh'] and wdir)
            #old crange: customrange and par in customrange and customrange[par]
            if smooth and smooth.lower() in ['kde', 'kde1', 'kdh']:
                fy = x, y
                #else: # (interpolation)
                #    fy = y
                #    y = y(x)
            else:
                fy = False

            if len(listwdir) > 1:
                if smooth and smooth.lower() in ['kde', 'kde1', 'kdh']:
                    ax[i].plot(x, y, lw=1., ls='-', color=hist_properties[par].color)
                    if show_hist:
                        ax[i].plot(hx, hy, lw=0.5, ls='-', color=hist_properties[par].color)
                else:
                    ax[i].plot(hx, hy, lw=1, ls='-', color=hist_properties[par].color)
            else:
                if smooth and smooth.lower() in ['kde', 'kde1', 'kdh']:
                    ax[i].plot(x, y, lw=1.5, ls='-', color='black')#hist_properties[par].color)
                    if show_hist:
                        ax[i].plot(hx, hy, lw=0.5, ls='-', color='black')#hist_properties[par].color)
                else:
                    ax[i].plot(hx, hy, lw=1.5, ls='-', color='black')#hist_properties[par].color)

            if show_gaussian_fit:
                X = np.linspace(hx[0], hx[-1], num=300)
                ax[i].axvline(mu[wdir][i] - sigma[wdir][i], ls='--', lw=0.3, color='b')
                ax[i].axvline(mu[wdir][i] - 2* sigma[wdir][i], ls='--', lw=0.3, color='b')
                ax[i].axvline(mu[wdir][i] + sigma[wdir][i], ls='--', lw=0.3, color='b')
                ax[i].axvline(mu[wdir][i] + 2*sigma[wdir][i], ls='--', lw=0.3, color='b')
                normalized_fit_curve = common.normalize(
                        1/mhist * st.distributions.norm(
                            mu[wdir][i],
                            sigma[wdir][i]
                            ).pdf(X), 
                        (0, 1), 
                        newlims=customrange[par] if customrange and par in customrange else (hist_properties[par].vmin, hist_properties[par].vmax)
                        )
                ax[i].plot(X, normalized_fit_curve, lw=0.8, color='b')

            draw_on_axes(len(listwdir), par, customunits, ax[i], (smooth and smooth.lower() in ['kde', 'kde1', 'kdh']) and fy, hist_properties[par], title_above=False, MHIST=mhist, CRANGE=(xyvmin,xyvmax), UseTex=UseTex, args=args)
            # here we need to give a CRANGE because vmin and vmax used
            # otherwise are the ones from x-axis. customrange (x-axis) is
            # ignored

        wdir = listwdir[-1]
        ax[i].tick_params(size=3)

        xvmin, xvmax = (customrange and par in customrange and customrange[par]) or ax[i].get_xlim()
        ax[i].set_xlim(xvmin, xvmax)
        intv = (xvmax - xvmin)/3
        imarg = intv/2
        ax[i].set_xticks(np.linspace(xvmin+imarg, xvmax-imarg, num=3))

        if par in customticks:
            ax[i].set_xticks(customticks[par])

        if customunits and (par in customunits):
            xticks = ax[i].get_xticks()
            log10unit = customunits[par]
            ax[i].set_xticklabels(xticks*eval('1e%i' % log10unit))
            if log10unit <= 2:
                ax[i].set_xlabel(r'$%i \, %s$' % (10**log10unit, tex[par]))
            else:
                ax[i].set_xlabel(r'$10^{%i} \, %s$' % (log10unit, tex[par]))
        else:
            ax[i].set_xlabel(r'$' + tex[par] + '$')

        ax[i].set_yticklabels('')
        
        bar.update(1)

    if isinstance(fig, list):
        if len(listwdir) > 1 and not gname:
            while not gname:
                gname = input('Custom common prefix for separate pdf files: ')
        gname = gname or 'params_hist'

        for figure, par in zip(fig, parnames):
            figure.set_size_inches(1.8, 2.)
            figure.tight_layout()
            figure.savefig(os.path.join(wdir, 'der-%s-%s.pdf' % (gname, par)))
            if png:
                figure.savefig(os.path.join(wdir, 'der-%s-%s.png' % (gname, par)))
        if len(listwdir) > 1:
            return os.path.join(wdir, 'der-%s-X.pdf' % gname)
    else:
        fig.set_size_inches(1.6*len(parnames), 2.)
        fig.tight_layout()
        fig.subplots_adjust(wspace=0.0)
        if len(listwdir) > 1 and not gname:
            while not gname:
                gname = input('Custom name for pdf file: ')

        gname = gname or 'params_hist'
        fig.savefig(os.path.join(wdir, 'der-%s.pdf' % gname))
        if png:
            fig.savefig(os.path.join(wdir, 'der-%s.png' % gname))
        if len(listwdir) > 1:
            return os.path.join(wdir, 'der-%s.pdf' % gname)

def make_2dhistograms(grid, subplots, nuisance, modelname,
        list_hist_properties, priors, tex, listwdir, parnames, bar,
        nocustomrange=False, nocustomticks=False, nocustomunits=False,
        smooth=False, singlecolor=['C0'], 
        listofcolors=['C%i' % i for i in range(10) if not i==3]+['C3'],
        bfmark=False, CMAP=False, contours=False, png=False, gname=False,
        show_gaussian_fit=False, show_hist=False, LEVELS=[1, 2], UseTex=False,
        fontsize=8, args=None):

    # this is different from the parnames.p file because we may want to see the
    # nuisance parameters (nonuisance flag)
    parnames = [par for par in parnames if not par in nuisance] 
    nparams = len(parnames)

    if args:

        # a custom range for the plots can be specified with a .range file.
        # However, it can be disabled without having to delete or rename this file,
        # using the flat nocustomrange. With multiple workingidr, nocustomrange
        # will be True so it helps visualizing different distributions. After then
        # the user can decide for a custom range but needs to inform this option
        # via range=Och2:0.02,0.03... in the command arguments
        nocustomrange = common.lookarg('nocustomrange', args) or nocustomrange
        nocustomrange = nocustomrange or len(listwdir) > 1

        # One can also bypass custom ticks file (.ticks) with the nocustomticks
        # flag, which will also happen automatically with more than one workingdir.
        # This can be overwritten again from the command with
        # ticks=Och2:0.02,0.022,0.024.. and will also have effect any time customrange is bypassed.
        nocustomticks = common.lookarg('nocustomticks', args) or nocustomticks
        nocustomticks = nocustomticks or len(listwdir) > 1

        # One can disable customunits although it is unlikely this will be used
        nocustomunits = common.lookarg('nocustomunits', args) or nocustomunits

        # Draw smooth histogram?
        smooth = common.lookarg1('smooth_hist=', args) or smooth

        # Default marker for best-fit point is x, but this can be changed. When
        # using +, o or square, vertical and horizontal lines are also drawn through
        # that point along the entire frame.
        bfmark = common.lookarg1('bf=', args) or bfmark

        # default format for plots is pdf. png images can also be saved using the flag png
        png = common.lookarg('png', args) or png

        # a custom name for the grid file can be given with gname to avoid
        # overwriting in a later moment
        gname = common.lookarg1('gname=', args) or gname

        # plot the pdf of the fitted Gaussians
        show_gaussian_fit = common.lookarg('show_gaussian_fit', args) or show_gaussian_fit
        show_hist = common.lookarg('show_hist', args) or show_hist

        # if the results to plot are from one simulation only (len(listwdir)==1), a
        # colormap can be used in the 2D-histograms. In this case, you can set
        # cmap=gist_heat,w for example to use the gist_heat color map with white
        # ('w') grid frames. If more than one workingdir is given, this setting
        # will be ignored and just set to False.
        CMAP = common.lookarg1list('cmap=', args) or CMAP
        contours = common.lookarg1('contours=', args) or contours

        # The default color for the histograms is red. It can be changed to any
        # other of your like.
        singlecolor = common.lookarg1list('singlecolor=', args) or singlecolor

        # a custom list of colors for multiple plots can be passed as a list of strings
        listofcolors = common.lookarg1list('colors=', args) or listofcolors

        # whether to use Tex or not
        UseTex = common.lookarg('usetex', args) or UseTex

        LEVELS = common.lookarg1list('levels=', args, instance=int) or LEVELS
        fontsize = common.lookarg1('fontsize=', args, instance=int) or fontsize 

    plt.rcParams['font.size'] = fontsize

    CMAP = len(listwdir) == 1 and CMAP 

    # when more than 1 result plotted together, can only set range manually
    # (range=Odh2:0.2_0.4,Obh2=0.01_0.03, ...)
    inifile = common.get_inifile_name(os.path.join(listwdir[0], '..', '..'))
    nocustomticks = nocustomrange or nocustomticks
    customticks = determine_customticks(args, inifile, not nocustomticks)
    customunits = determine_customunits(args, inifile, nocustomunits)
    customrange = determine_customrange(args, inifile, nocustomrange)

    if show_gaussian_fit:
        true_fit = os.path.isfile(inifile.replace('.ini', '.true_fit'))
        if true_fit:
            true_fit = []
            with open(inifile.replace('.ini', '.true_fit'), 'r') as tf_file: 
                tf_lines = tf_file.readlines()
                for line in tf_lines:
                    line = line.strip().split()
                    this_par_fit = []
                    for i in range(len(line)//3):
                        fit = TrueFit(*[float(l) for l in line[0+i*3:3+i*3]])
                        this_par_fit.append(fit)
                    true_fit.append(this_par_fit)
        mu = {}
        sigma = {}
        for wdir in listwdir:
            mu[wdir], sigma[wdir] = np.loadtxt(os.path.join(wdir, '..', 'par_fits.txt'), unpack=True) 

    def loadtxtfrom(prefix, wdir, JX, JY):
        return np.loadtxt(os.path.join(wdir, '%s-%s-%s.txt' % (prefix, parnames[JX], parnames[JY])))

    from common import alphas
    if len(listwdir) > 1:
        alphas = [0.40, 0.25, 0.10]

    superposalpha = 1 # min(1, sum(alphas[:len(LEVELS)]))

    for i in range(nparams*nparams):
        jx, jy = divmod(i, nparams)
        if jx > jy: 
            if len(listwdir) > 1:
                mcolor = itertools.cycle(listofcolors)
            else:
                mcolor = itertools.cycle(singlecolor)
            for wdir, hist_properties in zip(listwdir, list_hist_properties):
                try:
                    mcor = next(mcolor)
                    H = loadtxtfrom('H', wdir, jx, jy)
                    #seps = loadtxtfrom('seps', wdir, jx, jy)
                    xedg = loadtxtfrom('xedg', wdir, jx, jy)
                    yedg = loadtxtfrom('yedg', wdir, jx, jy)
                    sigmalevels, H = common.sigmalevels_2D(H, xedg, yedg, levels=LEVELS)
                    hrange = loadtxtfrom('hrange', wdir, jx, jy)
                    if CMAP:
                        XX = loadtxtfrom('XX', wdir, jx, jy)
                        YY = loadtxtfrom('YY', wdir, jx, jy)
                        subplots[jx][jy].pcolormesh(XX, YY, H.transpose(), cmap=CMAP[0])
                    else:
                        # contorno:
                        if smooth and smooth.lower() in ['kde', 'kde2', 'kdh']:
                            kde_hrange = loadtxtfrom('kde2d_hrange', os.path.join(wdir, '..', 'kde_estimates'), jx, jy)
                            kde_H = loadtxtfrom('kde2d_density', os.path.join(wdir, '..', 'kde_estimates'), jx, jy)
                            kde_xsupport = loadtxtfrom('kde2d_xsupport', os.path.join(wdir, '..', 'kde_estimates'), jx, jy) 
                            kde_ysupport = loadtxtfrom('kde2d_ysupport', os.path.join(wdir, '..', 'kde_estimates'), jx, jy) 
                            kde_sigmalevels, kde_H = common.sigmalevels_2D(kde_H, kde_xsupport, kde_ysupport, levels=LEVELS)

                        if len(listwdir) > 1:
                            if smooth and smooth.lower() in ['kde', 'kde2', 'kdh']:
                                subplots[jx][jy].contour(kde_H.transpose(),
                                        levels=kde_sigmalevels[::-1],
                                        extent=kde_hrange.flatten(),
                                        colors=mcor, linewidths=0.5,
                                        linestyles=['solid', 'solid'])
                                if show_hist:
                                    subplots[jx][jy].contour(H.transpose(),
                                            levels=sigmalevels[::-1],
                                            extent=hrange.flatten(),
                                            colors=mcor, linewidths=0.5,
                                            linestyles=['dotted', 'dotted'])
                            else:
                                subplots[jx][jy].contour(H.transpose(),
                                        levels=sigmalevels[::-1],
                                        extent=hrange.flatten(), colors=mcor,
                                        linewidths=0.5, linestyles=['solid',
                                            'solid'])

                        if smooth and smooth.lower() in ['kde', 'kde2', 'kdh']:
                            for il in range(len(kde_sigmalevels)):
                                subplots[jx][jy].contourf(kde_H.transpose(),
                                        levels=np.concatenate([kde_sigmalevels[::-1][-(il+1):],[np.inf]]),
                                        extent=kde_hrange.flatten(),
                                        colors=mcor, alpha=alphas[il]) 
                            if show_hist:
                                subplots[jx][jy].contour(H.transpose(),
                                        levels=sigmalevels[::-1],
                                        extent=hrange.flatten(), colors='k',
                                        linewidths=0.5, linestyles=['dotted',
                                            'dotted']) 
                        else:
                            for il in range(len(sigmalevels)):
                                subplots[jx][jy].contourf(H.transpose(),
                                        levels=np.concatenate([sigmalevels[::-1][-(il+1):],[np.inf]]),
                                        extent=hrange.flatten(), colors=mcor,
                                        alpha=alphas[il]) # fill onesigma

                    if show_gaussian_fit:
                        corr_xy = float(loadtxtfrom('corr_xy', wdir, jx, jy))
                        sigxy2 = corr_xy * sigma[wdir][jx] * sigma[wdir][jy]
                        IF = np.matrix([[sigma[wdir][jx]**2, sigxy2], [sigxy2, sigma[wdir][jy]**2]])
                        thx1s, thy1s = common.draw_ellipse(IF, (mu[wdir][jx], mu[wdir][jy]), CLsigma=common.CL68)
                        subplots[jx][jy].plot(thy1s, thx1s, ls='-', color='k', lw=0.3)
                        thx2s, thy2s = common.draw_ellipse(IF, (mu[wdir][jx], mu[wdir][jy]), CLsigma=common.CL95)
                        subplots[jx][jy].plot(thy2s, thx2s, ls='-', lw=0.3, color='k')
                except (IOError, ValueError):
                    pass

                if bfmark:
                    try:
                        bfx, bfy = hist_properties[parnames[jy]].bestfit, hist_properties[parnames[jx]].bestfit
                        bfmark_color = mcor if len(listwdir) > 1 else (0.6, 0.6, 0.6)
                        subplots[jx][jy].plot(bfx, bfy, mfc='w', markersize=5,
                                marker=bfmark, markeredgecolor='w',
                                markeredgewidth=0.5) # mcor
                        #if CMAP:
                        #    subplots[jx][jy].plot(bfx, bfy, markersize=4, marker=bfmark, markeredgecolor=cm.get_cmap(CMAP[0])(0)[:3], mfc=cm.get_cmap(CMAP[0])(0)[:3])
                        #    if contours:
                        #        subplots[jx][jy].contour(H.transpose(), levels=sigmalevels[::-1], extent=hrange.flatten(), colors=contours, linewidths=0.5) # sigmalevels[::-1][1:] for 1sigma contour only
                    #if bfmark in ['+', 'o', 's']:
                        subplots[jx][jy].axhline(bfy, linestyle='-', lw=0.3, color=bfmark_color)
                        subplots[jx][jy].axvline(bfx, linestyle='-', lw=0.3, color=bfmark_color)
                    except KeyError:
                        pass

            subplots[jx][jy].tick_params(size=3)

            if CMAP:
                subplots[jx][jy].set_facecolor(cm.get_cmap(CMAP[0])(0)[:3])


            if customrange and parnames[jy] in customrange:
                intv = (customrange[parnames[jy]][1] - customrange[parnames[jy]][0])/3
                imarg = intv/2
                subplots[jx][jy].set_xlim(customrange[parnames[jy]])
                subplots[jx][jy].set_xticks(np.linspace(customrange[parnames[jy]][0]+imarg, customrange[parnames[jy]][1]-imarg, num=3))
            else:
                pmin, pmax = priors[parnames[jy]].vmin, priors[parnames[jy]].vmax
                intv = (pmax - pmin)/3
                imarg = intv/2
                subplots[jx][jy].set_xlim(pmin, pmax)
                subplots[jx][jy].set_xticks(np.linspace(pmin+imarg, pmax-imarg, num=3))
            
            if parnames[jy] in customticks:
                subplots[jx][jy].set_xticks(customticks[parnames[jy]])
                    
            if customrange and parnames[jx] in customrange:
                intv = (customrange[parnames[jx]][1] - customrange[parnames[jx]][0])/3
                imarg = intv/2
                subplots[jx][jy].set_ylim(customrange[parnames[jx]])
                subplots[jx][jy].set_yticks(np.linspace(customrange[parnames[jx]][0]+imarg, customrange[parnames[jx]][1]-imarg, num=3))
            else:
                pmin, pmax = priors[parnames[jx]].vmin, priors[parnames[jx]].vmax
                intv = (pmax - pmin)/3
                imarg = intv/2
                subplots[jx][jy].set_ylim(pmin, pmax)
                subplots[jx][jy].set_yticks(np.linspace(pmin+imarg, pmax-imarg, num=3))

            if parnames[jx] in customticks:
                subplots[jx][jy].set_yticks(customticks[parnames[jx]])

            if CMAP:
                plt.setp([subplots[jx][jy].get_xticklines(), subplots[jx][jy].get_yticklines()], color=CMAP[1])
                plt.setp(subplots[jx][jy].spines.values(), color=CMAP[1])

            bar.update(1)

        elif jx < jy:
            if not isinstance(grid, list):
                grid.delaxes(subplots[jx][jy])
        else:
            comboH, combob, combow = {}, {}, {}
            notallwdir = []
            for wdir in listwdir:
                try:
                    comboH[wdir] = np.loadtxt(os.path.join(wdir, 'combocount-%s.txt' % parnames[jx]))
                    combob[wdir] = np.loadtxt(os.path.join(wdir, 'comboseps-%s.txt' % parnames[jx]))
                    combow[wdir] = np.loadtxt(os.path.join(wdir, 'combowidths-%s.txt' % parnames[jx]))
                    notallwdir.append(wdir)
                except:
                    pass
            if smooth and smooth.lower() in ['kde', 'kde1', 'kdh']:
                mhist = 1.15*max([np.loadtxt(os.path.join(wdir, '..', 'kde_estimates', 'kde_density-%s.txt' % parnames[jx])).max() for wdir in notallwdir])
            else:
                mhist = 1.15*max([comboH[wdir].max() for wdir in notallwdir])
            assert len(notallwdir) == len(list_hist_properties)
            for wdir, hist_properties in zip(notallwdir, list_hist_properties):
                pmin, pmax = priors[parnames[jx]].vmin, priors[parnames[jx]].vmax
                x, y, hx, hy = preparehistogram(comboH[wdir], combob[wdir],
                        combow[wdir], pmin, pmax, parnames[jx], mhist,
                        customrange and parnames[jx] in customrange and
                        customrange[parnames[jx]], smooth_hist=smooth and
                        smooth.lower() in ['kde', 'kde1', 'kdh'] and wdir)
                if smooth and smooth.lower() in ['kde', 'kde1', 'kdh']:
                    fy = x, y
                    #else: # (interpolation)
                    #    fy = y
                    #    y = y(x)
                else:
                    fy = False

                if len(listwdir) > 1:
                    if smooth and smooth.lower() in ['kde', 'kde1', 'kdh']:
                        subplots[jx][jy].plot(x, y, lw=1., ls='-', color=hist_properties[parnames[jx]].color)
                        if show_hist:
                            subplots[jx][jy].plot(hx, hy, lw=0.3, ls='-', color=hist_properties[parnames[jx]][3].color)
                    else:
                        subplots[jx][jy].plot(hx, hy, lw=1, ls='-', color=hist_properties[parnames[jx]].color)
                else:
                    if smooth and smooth.lower() in ['kde', 'kde1', 'kdh']:
                        subplots[jx][jy].plot(x, y, lw=1.5, ls='-', color='black')#hist_properties[parnames[jx]].color)
                        if show_hist:
                            subplots[jx][jy].plot(hx, hy, lw=0.3, ls='-', color='black')#hist_properties[parnames[jx]].color)
                    else:
                        subplots[jx][jy].plot(hx, hy, lw=1.5, ls='-', color='black')#hist_properties[parnames[jx]].color)


                if show_gaussian_fit:
                    X = np.linspace(hx[0], hx[-1], num=300)
                    if true_fit:
                        D = np.sum([gaussian.weight * st.distributions.norm(gaussian.mu, gaussian.sigma).pdf(X) for gaussian in true_fit[jx]], axis=0)
                        subplots[jx][jy].plot(X, common.normalize(
                            1/mhist * D, 
                            (0, 1),
                            newlims=customrange[parnames[jx]] if customrange and parnames[jx] in customrange else (hist_properties[parnames[jx]].vmin, hist_properties[parnames[jx]].vmax)
                            ), lw=0.8, color='b')
                        for gaussian in true_fit[jx]:
                            subplots[jx][jy].axvline(gaussian.mu - gaussian.sigma, ls='--', lw=0.3, color='b')
                            subplots[jx][jy].axvline(gaussian.mu - 2* gaussian.sigma, ls='--', lw=0.3, color='b')
                            subplots[jx][jy].axvline(gaussian.mu + gaussian.sigma, ls='--', lw=0.3, color='b')
                            subplots[jx][jy].axvline(gaussian.mu + 2*gaussian.sigma, ls='--', lw=0.3, color='b')
                    else:
                        subplots[jx][jy].axvline(mu[wdir][jx] - sigma[wdir][jx], ls='--', lw=0.3, color='b')
                        subplots[jx][jy].axvline(mu[wdir][jx] - 2* sigma[wdir][jx], ls='--', lw=0.3, color='b')
                        subplots[jx][jy].axvline(mu[wdir][jx] + sigma[wdir][jx], ls='--', lw=0.3, color='b')
                        subplots[jx][jy].axvline(mu[wdir][jx] + 2*sigma[wdir][jx], ls='--', lw=0.3, color='b')
                        normalized_fit_curve = common.normalize(
                                1/mhist * st.distributions.norm(
                                    mu[wdir][jx],
                                    sigma[wdir][jx]
                                    ).pdf(X),
                                (0, 1), 
                                newlims=customrange[parnames[jx]] if customrange and parnames[jx] in customrange else (hist_properties[parnames[jx]].vmin, hist_properties[parnames[jx]].vmax)
                                )
                        subplots[jx][jy].plot(X, normalized_fit_curve, lw=0.8, color='b')

                draw_on_axes(len(listwdir), parnames[jx], customunits, subplots[jx][jy], (smooth and smooth.lower() in ['kde', 'kde1', 'kdh']) and fy, hist_properties[parnames[jx]], title_above=not isinstance(grid, list), MHIST=mhist, CRANGE=customrange and parnames[jx] in customrange and customrange[parnames[jx]], args=args)
            wdir = listwdir[-1]
            subplots[jx][jy].tick_params(size=3)
            bar.update(1)
        

    for j in range(nparams):
        if isinstance(grid, list) or j == nparams-1:
            lastrowpar = parnames[j]
            if customrange and lastrowpar in customrange:
                subplots[j][j].set_xlim(customrange[lastrowpar])
                intv = (customrange[lastrowpar][1] - customrange[lastrowpar][0])/3
                imarg = intv/2
                subplots[j][j].set_xticks(np.linspace(customrange[lastrowpar][0]+imarg, customrange[lastrowpar][1]-imarg, num=3))
            else:
                pmin, pmax = priors[lastrowpar].vmin, priors[lastrowpar].vmax
                subplots[j][j].set_xlim(pmin, pmax)
                intv = (pmax - pmin)/3
                imarg = intv/2
                subplots[j][j].set_xticks(np.linspace(pmin+imarg, pmax-imarg, num=3))

            if lastrowpar in customticks:
                subplots[j][j].set_xticks(customticks[lastrowpar])

    for j in range(nparams):
        if isinstance(grid, list) or j == 0:
            firstcolumnpar = parnames[j]
            if customrange and firstcolumnpar in customrange:
                subplots[j][j].set_ylim(customrange[firstcolumnpar])
            else:
                subplots[j][j].set_ylim(priors[firstcolumnpar].vmin, priors[firstcolumnpar].vmax)

    for i in range(nparams*nparams):
        jx, jy = divmod(i, nparams)
        par = parnames[jy]
        if jx >= jy and (isinstance(grid, list) or jx == nparams-1):
            if customunits and (par in customunits):
                xticks = subplots[jx][jy].get_xticks()
                log10unit = customunits[par]
                subplots[jx][jy].set_xticklabels(xticks* eval('1e%i' % log10unit))
                if log10unit <= 2:
                    subplots[jx][jy].set_xlabel(r'$%i \, %s$' % (10**log10unit, tex[par]))
                else:
                    subplots[jx][jy].set_xlabel(r'$10^{%i} \, %s$' % (log10unit, tex[par]))
            else:
                subplots[jx][jy].set_xlabel(r'$' + tex[par] + '$')
            

    # different range from above
    for i in range(0,nparams*nparams):
        jx, jy = divmod(i, nparams)
        par = parnames[jx]
        if jx > jy and (isinstance(grid, list) or jy == 0):
            if customunits and (par in customunits):
                yticks = subplots[jx][jy].get_yticks()
                log10unit = customunits[par]
                subplots[jx][jy].set_yticklabels(yticks* eval('1e%i' % log10unit))
                if log10unit <= 2:
                    subplots[jx][jy].set_ylabel(r'$%i \, %s$' % (10**log10unit, tex[par]))
                else:
                    subplots[jx][jy].set_ylabel(r'$10^{%i} \, %s$' % (log10unit, tex[par]))
            else:
                subplots[jx][jy].set_ylabel(r'$' + tex[par] + '$')


    for i in range(nparams):
        if isinstance(grid, list) or i == 0:
            subplots[i][i].set_yticklabels('')

    if len(listwdir) > 1 and not isinstance(grid, list):
        mcolor = itertools.cycle(listofcolors)
        legs = []
        for wdir in listwdir:
            with open(os.path.join(wdir, '..', '..', 'labels.txt'), 'r') as lf:
                lbl = lf.readlines()
            lbl = [l.strip() for l in lbl]
            legs.append(mpatches.Patch(color=next(mcolor), alpha=superposalpha, linewidth=1, label=' + '.join(lbl)))
        subplots[-1][-1].legend(title=modelname, handles=legs, frameon=False, borderaxespad=0.5, handletextpad=0.8,
                bbox_to_anchor=(1,1), bbox_transform=grid.transFigure)

    if isinstance(grid, list):
        if len(listwdir) > 1 and not gname:
            while not gname:
                gname = input('Custom common prefix for separated pdf files: ')

        if CMAP and not gname:
            gname = 'grid%s' % CMAP[0]
        if (not CMAP) and not gname:
            gname = 'grids2s'

        for i in range(nparams*nparams):
            jx, jy = divmod(i, nparams)
            if jx >= jy:
                grid[jx][jy].set_size_inches(2. if jx > jy else 1.8, 2.)
                grid[jx][jy].tight_layout()

                grid[jx][jy].savefig(os.path.join(wdir, gname + '-' + '-'.join(list(set([parnames[jx], parnames[jy]])))+ '.pdf'))
                if png:
                    grid[jx][jy].savefig(os.path.join(wdir, gname + '-' + '-'.join(list(set([parnames[jx], parnames[jy]])))+ '.png'), dpi=360)
            else:
                pass

        if len(listwdir) > 1:
            return os.path.join(wdir, '%s-X-X.pdf' % gname)
        
    else:
        grid.set_size_inches(nparams*1.6, nparams*1.6)
        grid.tight_layout()

        #grid.subplots_adjust(top=toppos)
        #grid.subplots_adjust(left=lateral)
        #grid.subplots_adjust(right=1-lateral)
        grid.subplots_adjust(hspace=0.0)
        grid.subplots_adjust(wspace=0)

        if len(listwdir) > 1 and not gname:
            while not gname:
                gname = input('Custom name for pdf file: ')

        if CMAP and not gname:
            gname = 'grid%s' % CMAP[0]
        if (not CMAP) and not gname:
            gname = 'grids2s'

        # will use the last wdir
        grid.savefig(os.path.join(wdir, '%s.pdf' % gname))
        #print(wdir, '%s.pdf' % gname)
        if png:
            grid.savefig(os.path.join(wdir, '%s.png' % gname), dpi=360)
            #print(wdir, '%s.png' % gname)

        if len(listwdir) > 1:
            return os.path.join(wdir, '%s.pdf' % gname)

def determine_customticks(args, inifile, ticks=True):
    cticks = {}
    if ticks:
        ticks = os.path.isfile(inifile.replace('.ini', '.ticks')) and inifile.replace('.ini', '.ticks')
        ticks = ticks or common.lookarg1('ticks=', args)
        if ticks:
            for (par, xyticks) in load_ticks(ticks):
                cticks[par] = xyticks     
    else:
        ticks = common.lookarg1list('ticks=', args)
        if ticks:
            for tck in ticks:
                par, aticks = tck.split(':')
                aticks = aticks.split('_')
                cticks[par] = [float(at) for at in aticks]
    return cticks

def determine_customunits(args, inifile, nocustomunits=False):
    unitsfile = os.path.isfile(inifile.replace('.ini', '.units')) and inifile.replace('.ini', '.units')
    if unitsfile and not nocustomunits:
        dictunits = {}
        for par, log10unit in load_units(unitsfile):
            dictunits[par] = log10unit
        customunits = dict(dictunits)
    else:
        customunits = common.lookarg1list('units=', args)
        if customunits:
            dictunits = {}
            for unitslist in customunits:
                par, unit = unitslist.split(':')
                dictunits[par] = int(unit)
            customunits = dict(dictunits)

    if customunits:
        h2phys = ['Och2', 'Obh2', 'Orh2', 'Odh2']
        der = ['Oc0', 'Ob0', 'Or0', 'Od0']
        for p, d in zip(h2phys, der):
            if p in customunits:
                if not (d in customunits):
                    customunits[d] = customunits[p]
        if 'Oc0' in customunits:
            if not 'Om0' in customunits:
                customunits['Om0'] = customunits['Oc0']

    return customunits

def determine_customrange(args, inifile, nocustomrange=False):
    rangefile = os.path.isfile(inifile.replace('.ini', '.range')) and inifile.replace('.ini', '.range')
    if rangefile and not nocustomrange:
        priorsrange, _, _ = common.lookprior(common.readfile(rangefile), needs_mq=False)
        pars = list(priorsrange.keys())
        dictrange = collections.OrderedDict()
        for par in pars:
            dictrange[par] = priorsrange[par].vmin, priorsrange[par].vmax
        customrange = collections.OrderedDict(dictrange)
    else:
        customrange = common.lookarg1list('range=', args)
        if customrange:
           dictrange = collections.OrderedDict()
           for crange in customrange:
               par, interval = crange.split(':')
               xa, xb = interval.split('_')
               dictrange[par] = float(xa), float(xb)
           customrange = collections.OrderedDict(dictrange)
    return customrange

def build_histograms(listwdir, include_nuisance=True, UseTex=False, use_derived=False, cfont='cmr10', dont_include_pars=[], args=None):

    if args:
        # include or not nuisance parameters in the plots
        include_nuisance = not common.lookarg('nonuisance', args)
        dont_include_pars = common.lookarg1list('dont_include_pars', args) or dont_include_pars

        # wether to use tex or not
        UseTex = common.lookarg('usetex', args) or UseTex

        use_derived = common.lookarg('use_derived', args) or use_derived

        cfont = common.lookarg1('font=', args) or cfont

    if UseTex:
        plt.rc('font',**{'family':'serif','serif':[cfont]}) # 'cmr10'
        tex_packages = [
                r'\usepackage{amsmath}',
                ]
        if cfont and cfont.lower() == 'times':
            tex_packages.append(r'\usepackage{txfontsb}')
            #tex_packages.append(r'\usepackage{mathptmx}')
        plt.rcParams['text.latex.preamble'] = tex_packages
        plt.rc('text', usetex=True)

    inifile = common.get_inifile_name(os.path.join(listwdir[0], '..', '..'))
    modelname = common.read1linestring(common.readfile(os.path.join(listwdir[0], '..', '..', inifile)), 'NAME')
    priors, nuisance, _, tex, parnames, nparams, nchains = common.load_chains_and_model_details(os.path.join(listwdir[0], '..', '..'))
    if include_nuisance:
        nuisance = []
    nuisance += dont_include_pars

    try:
        derparnames = pickle.load(open(os.path.join(listwdir[0], '..', '..', 'der_parnames.p'), 'rb'))
        nderpars = len(derparnames)
    except IOError:
        nderpars = 0

    nderpars = use_derived and nderpars 

    numberhists = len(listwdir) * (nparams + nderpars) + \
            2*nparams + 2*nderpars - len(nuisance) + \
            (nparams-len(nuisance))*(nparams-len(nuisance)-1) # 2 * ( ) // 2
    plotting_histograms_all = common.fixed_length('Plotting distributions of all parameters...')
    with click.progressbar(length=numberhists, width=10, show_pos=False, empty_char='.', label=plotting_histograms_all, info_sep='  |  ', show_eta=False) as bar:
        if nderpars:
            der_list_wdir = []
            for wdir in listwdir:
                root, resultsfolder = os.path.split(wdir.rstrip('\\').rstrip(os.pathsep).rstrip('/'))
                der_list_wdir.append(os.path.join(root, 'der_pars', resultsfolder))
            der_list_hist_properties = make_histograms(nderpars, derparnames, tex, der_list_wdir, bar, derived=True, CFONT=cfont, args=args)
            der_subplots_fig, ax = plt.subplots(1, nderpars)
            if nderpars == 1:
                ax = [ax,]
            saved_der_hist = der_drawhistograms(derparnames, der_subplots_fig,
                    ax, tex, der_list_wdir, der_list_hist_properties, bar,
                    args=args)
            der_separate_figs = [plt.subplots() for _ in range(nderpars)]
            der_drawhistograms(
                    derparnames, 
                    [fig[0] for fig in der_separate_figs],
                    [fig[1] for fig in der_separate_figs], 
                    tex, der_list_wdir, der_list_hist_properties, bar,
                    args=args)

        list_hist_properties = make_histograms(nparams, parnames, tex, listwdir, bar, priors=priors, CFONT=cfont, args=args)
        grid, subplots = plt.subplots(nparams-len(nuisance), nparams-len(nuisance), sharex='col', sharey='row')
        if nparams-len(nuisance) == 1:
            subplots = [[subplots,],]
        saved_hist = make_2dhistograms(grid, subplots, nuisance, modelname, list_hist_properties, priors, tex, listwdir, parnames, bar, args=args)

        nuisance_sep = [] # or nuisance
        plt.rcParams['figure.max_open_warning'] = (nparams-len(nuisance_sep))**2 + nparams-len(nuisance_sep)
        separate_figs = [[plt.subplots() if i <= j else (None, None) \
                for i in range(nparams-len(nuisance_sep))] \
                for j in range(nparams-len(nuisance_sep))]
        make_2dhistograms(
                [[fig[0] for fig in sep_fig] for sep_fig in separate_figs],
                [[fig[1] for fig in sep_fig] for sep_fig in separate_figs], 
                nuisance_sep, modelname, list_hist_properties, priors, tex,
                listwdir, parnames, bar, args=args)


    if saved_hist:
        print("Saved %s" % saved_hist)
    if nderpars and saved_der_hist:
        print("Saved %s" % saved_der_hist)

def load_units(unitsfile):
    lines = common.readfile(unitsfile)
    lines = [l.split() for l in lines if len(l.split()) > 0]
    lines = [[l[0], int(l[1])] for l in lines]
    return lines

def load_ticks(ticksfile):
    lines = common.readfile(ticksfile)
    lines = [l.split() for l in lines if len(l.split()) > 0]
    lines = [[l[0], eval(l[1])] for l in lines]
    return lines

if __name__ == '__main__':

    listworkingdir = [arg for arg in sys.argv if os.path.isdir(arg)]

    itime = time.time()

    build_histograms(listworkingdir, args=sys.argv)
    ftime = time.time()
    print('Total time: %s' % common.printtime(ftime - itime))
    print('')

