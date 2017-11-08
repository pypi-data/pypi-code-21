import matplotlib,numpy,math
import matplotlib.pyplot as plt
from .retrieve             import time_convert
from astropy.units         import Quantity
from datetime              import datetime
from matplotlib            import pyplot
from gwpy.table            import EventTable
from gwpy.plotter          import SegmentPlot,TimeSeriesPlot
from gwpy.plotter          import FrequencySeriesPlot,SpectrogramPlot
from gwpy.segments         import SegmentList
from gwpy.frequencyseries  import FrequencySeries
from gwpy.spectrogram      import Spectrogram
from gwpy.time             import from_gps
from gwpy.timeseries       import TimeSeries
from pylab                 import *
from scipy                 import signal

def plot_activity(full_seglist):
    """
    Plot full activity period for station.

    Parameters
    ----------
    full_seglist : dictionary
      Continuous list of available data in the selected time period
    """
    # Import gwpy tools
    plot = SegmentPlot()
    # Initialize plotting figure
    ax = plot.gca()
    # Plot all segment in figure
    ax.plot(full_seglist)
    # Save figure
    pyplot.savefig("activity.png",dpi=300)

def plot_asd(station,data):
    """
    Plot Amplitude Spectral Density. AGG complexity starts to complain
    with large numbers of points. And we somehow invoke precision issues
    that need to be ameliorated.
    """
    if station!='fake':
        for d in data:
            d.x0 = Quantity(int(d.x0.value * 500), d.xunit)
            d.dx = Quantity(1, d.xunit)
        data.coalesce()
        for d in data:
            d.x0 = Quantity(d.x0.value / 500, d.xunit)
            d.dx = Quantity(0.002, d.xunit)
    # Initialize plotting functionality
    plot = FrequencySeriesPlot()
    # Loop over all the time series
    for d in data:
        # Generate 8 seconds per FFT with 4 second (50%) overlap
        spectrum = d.asd(8, 4)
        # Create plotting axis
        ax = plot.gca()
        # Plot square root of the spectrum
        ax.plot(numpy.sqrt(spectrum))
    # Set x axis to log scale
    ax.set_xscale('log')
    ax.set_xlabel('Frequency [Hz]')
    # Set y axis to log scale
    ax.set_yscale('log')
    ax.set_ylabel('Amplitude [pT]')
    # Set x axis limits
    ax.set_xlim(1e-1, 500)
    import matplotlib.ticker as ticker
    x = ax.get_xticklabels()
    def myticks(x,pos):
        if x == 0: return "$0$"
        exponent = int(np.log10(x))
        coeff = x/10**exponent
        if coeff==1:
            return r"$10^{{ {:2d} }}$".format(exponent)
        else:
            return r"${:2.0f} \times 10^{{ {:2d} }}$".format(coeff,
                                                             exponent)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(myticks))
    # Save figure
    plot.savefig("asd.png",dpi=300)
    
def plot_time_series(data,station='station-name',t0=None,t1=None,seglist=None,burst=None,fname='time_series'):
    """
    Generate a plot of the whole data time series
    """
    if type(data[0])==float64:
        data = [TimeSeries(data,sample_rate=data.sample_rate,epoch=data.start_time)]
    plot = TimeSeriesPlot()
    ax = plot.gca()
    # Loop over all the time series
    for ts in data:
        # Plot time series for each segment
        ax.plot(ts, color='black')
    # Display title
    ax.set_title('$\mathrm{'+station+'}$')
    ax.set_ylabel('Magnetic Field')
    # Plot fake signal
    if burst is not None:
        ax.plot(burst, color='red')
    # Plot activity segments
    if seglist!=None:
        activity = SegmentList(seglist[station].active)
        plotargs = {'label':'data present','facecolor':'g','edgecolor':'k'}
        plot.add_state_segments(activity,plotargs=plotargs)
    # Set limits
    if t0 is not None and t1 is not None:
        t0,t1 = time_convert(t0,t1)
        plot.axes[0].set_epoch(t0)
        plot.axes[1].set_epoch(t0)
        ax.set_xlim(t0,t1)
    # Fix exceeded cell block limit error
    matplotlib.pyplot.rcParams['agg.path.chunksize'] = 20000
    # Save figure
    plot.savefig('%s.png'%fname)
    
def plot_whitening(data,station='station-name',t0=None,t1=None,stride=20,fftlength=6,overlap=3,seglist=None):
    """
    Generate a spectrogram plot and normalized spectrogram
    norm: \sqrt{S(f,t)} / \sqrt{\overbar{S(f)}}
    """
    if type(data[0])==float64:
        data = [TimeSeries(data,sample_rate=data.sample_rate,epoch=data.start_time)]
    # Setup plots
    plot = SpectrogramPlot()
    ax = plot.gca()
    white_plot = SpectrogramPlot()
    wax = white_plot.gca()
    # Loop through available time series
    for ts in data:
        #if (len(ts) * ts.dt).value < stride:
        #    continue
        spec = ts.spectrogram(stride,fftlength=fftlength,overlap=overlap)
        wspec = spec.ratio('median')
        ax.plot(spec, cmap='jet',norm=matplotlib.colors.LogNorm())
        wax.plot(wspec, vmin=0.1, vmax=100,cmap='jet',norm=matplotlib.colors.LogNorm())
    # Define y axis and title
    ax.set_title('$\mathrm{'+station+'}$')
    ax.set_ylim(0.1, ts.sample_rate.value/2.)
    ax.set_yscale('log')
    wax.set_title('$\mathrm{'+station+'}$')
    wax.set_ylim(0.1, ts.sample_rate.value/2.)
    wax.set_yscale('log')
    plot.add_colorbar(label='Amplitude')
    white_plot.add_colorbar(label='Amplitude')
    # Plot activity panels for real data
    if seglist!=None:
        activity = SegmentList(seglist[station].active)
        plotargs = {'label':'data present','facecolor':'g','edgecolor':'k'}
        plot.add_state_segments(activity,plotargs=plotargs)
        white_plot.add_state_segments(activity,plotargs=plotargs)
    # Set plotting limits of x axis if edges defined
    if t0!=None and t1!=None:
        t0,t1 = time_convert(t0,t1)
        plot.axes[0].set_epoch(t0)
        plot.axes[2].set_epoch(t0)
        white_plot.axes[0].set_epoch(t0)
        white_plot.axes[2].set_epoch(t0)
        ax.set_xlim(t0,t1)
        wax.set_xlim(t0,t1)
    # Save figures
    plot.savefig("spectrogram.png",dpi=300)
    white_plot.savefig("whitened.png",dpi=300)

def plot_triggers(filename='excesspower.xml.gz',fname='triggers.png'):
    events = EventTable.read(filename,format='ligolw.sngl_burst')
    #plot = events.plot('time','central_freq','duration','bandwidth',color='snr')
    time = events['peak_time'] + events['peak_time_ns'] * 1e-9
    events.add_column(events['peak_time'] + events['peak_time_ns'] * 1e-9, name='time')
    plot = events.plot('time','central_freq',color='snr',edgecolor='none')
    plot.axes[0].set_epoch(int(min(time)))
    plot.set_xlim((int(min(time)),round(max(time))))
    plot.set_ylabel('Frequency [Hz]')
    plot.set_yscale('log')
    #plot.set_title('GNOME '+station+' station event triggers')
    plot.add_colorbar(cmap='copper_r',label='Tile Energy')
    pyplot.savefig(fname,dpi=300)

def plot_bank(fdb):
    pyplot.figure()
    for i, fdt in enumerate(fdb):
        if i==2:
            pyplot.plot(fdt.frequencies, fdt, 'k-')
            break
    pyplot.grid()
    #xmin = fdb[0].frequencies[0].value
    #xmax = fdb[-1].frequencies[-1].value
    #pyplot.xlim([xmin,xmax])
    pyplot.xlabel("frequency [Hz]")
    pyplot.savefig('bank.png',dpi=300)
    pyplot.close()

def plot_filters(tdb,fmin,band):
    pyplot.figure()
    pyplot.subplots_adjust(left=0.2,right=0.95,bottom=0.15,top=0.95,hspace=0,wspace=1)
    for i, tdt in enumerate(tdb[:8:3]):
        ax = pyplot.subplot(3, 1, i+1)
        ax.plot(tdt.times.value - 2., numpy.real_if_close(tdt.value), 'k-')
        c_f = fmin + band/2 + 3 * (band*i) + 2.
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("%d Hz" % c_f)
        ax.set_xlim(25.0, 31.0)
        ax.set_ylim([-max(tdt.value), max(tdt.value)])
        #if i!=2: pyplot.setp(ax.get_xticklabels(), visible=False)
    pyplot.savefig('filters.png',dpi=300)
    pyplot.close()
    
def plot_ts(ts, fname="ts.png"):
    plot = TimeSeriesPlot()
    ax = plot.gca()
    ax.plot(TimeSeries(ts, sample_rate=1.0/ts.delta_t, epoch=ts.start_time))
    ax.set_xlim(ts.start_time,ts.end_time)
    pyplot.savefig(fname)
    pyplot.close()

def plot_spectrum(fd_psd):
    plot = FrequencySeriesPlot()
    ax = plot.gca()
    ax.plot(FrequencySeries(fd_psd, df=fd_psd.delta_f))
     #pyplot.ylim(1e-10, 1e-3)
    pyplot.xlim(0.1, 500)
    pyplot.loglog()
    pyplot.savefig("psd.png",dpi=300)
    pyplot.close()

def plot_spectrogram(spec,dt,df,ymax,t0,t1,fname="specgram.png"):
    plot = SpectrogramPlot()
    ax = plot.gca()
    ax.plot(Spectrogram(spec,dt=dt,df=df,epoch=float(t0)),cmap='viridis')
    plot.add_colorbar(label='Amplitude')
    pyplot.xlim(t0,t1)
    pyplot.ylim(0,ymax)
    pyplot.savefig(fname)#,dpi=300)
    pyplot.close()

def plot_tiles_ts(tdb,ndof,df,sample_rate,t0,t1,fname="tiles.png"):
    fig = TimeSeriesPlot(figsize=(12,12))
    fig.suptitle('%i channels, %i Hz bandwidth, %i DOF'%(len(tdb),df,ndof))
    plt.subplots_adjust(left=0.03, right=0.97, bottom=0.07, top=0.95, hspace=0, wspace=0)
    for i, tdf in enumerate(tdb):
        ts_data = TimeSeries(tdf,epoch=float(t0),sample_rate=sample_rate)
        ax = fig.add_subplot(len(tdb),1,len(tdb)-i)
        ax.plot(ts_data)
        ax.set_xlim(t0,t1)
        if i>0:
            ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
    pyplot.savefig(fname)
    pyplot.close()

def plot_tiles_tf(tdb,ndof,df,ymax,sample_rate,t0,t1,fname="tiles.png"):
    for i, tdf in enumerate(tdb):
        ts_data = TimeSeries(tdf,epoch=float(t0),sample_rate=sample_rate)
        f, t, Sxx = signal.spectrogram(tdf, sample_rate)
        pyplot.figure(figsize=(12,8))
        pyplot.subplots_adjust(left=0.1, right=0.97, bottom=0.07, top=0.95, hspace=0, wspace=0)
        pyplot.pcolormesh(t, f, Sxx)
        pyplot.ylabel('Frequency [Hz]')
        pyplot.xlabel('Time [sec]')
        pyplot.ylim(0,ymax)
        pyplot.show()
        pyplot.savefig(fname.replace('.png','_%03i.png'%i))
        pyplot.close()
    quit()

def plot_spectrogram_from_ts(ts,fname='specgram.png'):
    plot = SpectrogramPlot()
    ax = plot.gca()
    ax.plot(Spectrogram(spec))
    #pyplot.ylim(1e-9, 1e-2)
    #pyplot.xlim(0.1, 500)
    #pyplot.loglog()
    pyplot.savefig(fname)
    pyplot.close()

def build_spec(ts,freq,spec,psd,fname,scale='linear',window=0.,station='',dy=None,xmin=None,xmax=None):
    # Convert time array into minute unit
    offset = int(window*ts.sample_rate.value)
    epoch = ts.times[offset].value
    times = (ts.times.value-epoch)/60
    # Define minimum and maximum time, frequency, field and power values
    tmin,tmax = times[offset],times[len(times)-offset-1]
    fmin,fmax = 0.1,ts.sample_rate.value/2.
    mmin,mmax = min(ts[offset:len(times)-offset].value),max(ts[offset:len(times)-offset].value)
    # Remove data from specific frequency ranges
    #idxs = numpy.where(np.logical_or(freq<0.0001,1000<freq))[0]
    #spec = numpy.delete(spec,idxs,0)
    #freq = numpy.delete(freq,idxs,0)
    # Initialise axis
    matplotlib.rcParams['agg.path.chunksize'] = 10000
    matplotlib.rcParams['xtick.labelsize'] = 10 
    matplotlib.rcParams['ytick.labelsize'] = 10 
    fig = plt.figure(figsize=(12,8))
    fig.suptitle(station)
    plt.subplots_adjust(left=0.07, right=0.95, bottom=0.1, top=0.95, hspace=0, wspace=0)
    ax1 = fig.add_axes([0.20,0.75,0.693,0.20])
    ax2 = fig.add_axes([0.20,0.10,0.693,0.64], sharex=ax1)
    ax3 = fig.add_axes([0.07,0.10,0.123,0.64])
    ax4 = fig.add_axes([0.90,0.10,0.030,0.64])
    # Plot time series
    ymin = mmin if dy==None else (mmax+mmin-dy)/2
    ymax = mmax if dy==None else (mmax+mmin+dy)/2
    ax1.plot(times,ts.value,alpha=0.5)
    ax1.set_xlim(tmin,tmax)
    ax1.set_ylim(ymin,ymax)
    ax1.set_ylabel('Magnetic Fields [pT]',fontsize=11)
    ax1.tick_params(bottom='off',labelbottom='off') 
    ax1.grid(b=True, which='major', alpha=0.7, ls='--')
    # Plot spectrogram
    img = ax2.imshow(spec,extent=[times[0],times[-1],freq[-1],freq[0]],
                     aspect='auto',interpolation='nearest',
                     cmap='viridis',norm=matplotlib.colors.LogNorm())
    ax2.set_xlabel('Time [minutes] from %s UTC'%from_gps(epoch),fontsize=15)
    ax2.set_xlim(tmin,tmax)
    ax2.set_ylim(fmin,fmax)
    ax2.set_yscale(scale)
    ax2.grid(False)
    # Set up axis range for spectrogram
    twin_ax = ax2.twinx()
    twin_ax.set_yscale('log')
    twin_ax.set_xlim(tmin,tmax)
    twin_ax.set_ylim(fmin,fmax)
    twin_ax.grid(False)
    ax2.tick_params(which='both', labelleft=False, left=False)
    twin_ax.tick_params(which='both', labelleft=False,left=False, labelright=False, right=False)
    # Plot PSD of time series data
    ticks = matplotlib.ticker.FuncFormatter(lambda v,_:("$10^{%.0f}$"%math.log(v,10)))
    imin = abs(psd[:,0]-fmin).argmin()
    imax = abs(psd[:,0]-fmax).argmin()
    pmin = min(psd[imin:imax,1]) if xmin==None else xmin
    pmax = max(psd[imin:imax,1]) if xmax==None else xmax
    ax3.loglog(psd[:,1],psd[:,0],alpha=0.5)
    ax3.set_xlim(pmin,pmax)
    ax3.set_ylim(fmin,fmax)
    ax3.xaxis.set_major_formatter(ticks)
    ax3.yaxis.set_major_formatter(ticks)
    ax3.set_xlabel('PSD $[\mathrm{pT}^2/\mathrm{Hz}]$',fontsize=11)
    ax3.set_ylabel('Frequency [Hz]',fontsize=15)
    ax3.grid(b=True, which='major', alpha=0.7, ls='--')
    # Add color bar and save figure
    cmin,cmax =	int(math.log(spec.min(),10)),int(math.log(spec.max(),10))
    fig.colorbar(img,cax=ax4,ticks=[10**i for i in range(cmin,cmax+1,1)])
    ax4.set_ylabel('Power $|\mathrm{W}_v|^2$ $[\mathrm{pT}^2/\mathrm{Hz}]$',fontsize=15,labelpad=10)
    plt.savefig(fname,transparent=True)
    plt.close(fig)
