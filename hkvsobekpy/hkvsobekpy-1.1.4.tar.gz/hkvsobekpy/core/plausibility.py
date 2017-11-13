import os
try:
    from pathlib import Path
except:    
    from pathlib2 import Path
import argparse
import sys
import itertools
import geopandas as gpd
from datetime import datetime, timedelta
import copy
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import re
from matplotlib.ticker import ScalarFormatter, FormatStrFormatter
import numpy as np
import pandas as pd
from scipy import optimize
import fire
import warnings
try:
    shell = get_ipython().__class__.__name__
    if shell == 'ZMQInteractiveShell':
        from tqdm import tqdm_notebook as tqdm # Jupyter notebook or qtconsole        
    elif shell == 'TerminalInteractiveShell':
        from tqdm import tqdm # Terminal running IPython
    else:
        from tqdm import tqdm # Other type (?)
except NameError:
    from tqdm import tqdm # Probably standard Python interpreter
    
#for debugging within notebook    

try:
    from IPython.core.debugger import set_trace    
except:
    pass

# for python 2/3 compatibility
try:
    xrange
except NameError:
    xrange = range    
try:
    get_ipython().magic('matplotlib inline')    
except:
    pass
from hkvsobekpy.io.his import __his_class
from hkvsobekpy.io.bui import __bui_class
his_reader = __his_class()
bui_reader = __bui_class()

class __plausibility_class(object):

    def __init__(self):
        """
        SobekResultaten class. Class met methodes om een .his bestand 
        uit te lezen.
        WaterstandStatistiek class. Class met methodes om een GumbleFit te bepalen
        """
        # initatie van lege immutable objects
        # zie: https://stackoverflow.com/a/22526544/2459096
        # python2.7: obj = argparse.Namespace()
        # python3.x: obj = types.SimpleNamespace()        
        # self.stats = argparse.Namespace()
        # self.stats.plotposities = argparse.Namespace()
        # self.stats.stap1 = argparse.Namespace()
        # self.stats.stap2 = argparse.Namespace()
        # self.stats.stap3 = argparse.Namespace()
        # self.stats.stap4 = argparse.Namespace()
        
    class __errors__(object):
        """
        error class met verschillende foutmeldingen
        """
        @staticmethod
        def gewogenGemiddeldeError():
            raise ValueError('Kan gewogen gemiddelde niet bepalen. Vereiste is minimaal 2 punten aan de linker en rechterzijde van de gekozen T')
        def gebeurtenissenError():
            raise ValueError('Meer gebeurtenissen dan N. Zorg ervoor dat je tijdreeks slechts 1 gebeurtenis per jaar heeft')
        def schrijfTabelError():
            raise ValueError('Kan deze tabel alleen wegschrijven met T10,25,50,100 voor Gumbel en T10 voor gewogen gemiddelde')

    def read_his_series(self, his_file, location, parameter, his_folder):
        """
        Extract timeseries from his-file
        
        Parameters
        ----------
        his_file : str
            name of his-file to query (e.g: 'reachseg', 'calcpnt', 'struc')
        location : str
            location to query in his-file
        parameter : str
            parameter to query in his-file
        his_folder : str
            path to folder containing the his_file
        
        Returns
        -------
        df : pandas.DataFrame
            timeseries containing all available timesteps in his-file
        """
        # get metadata from appropriate his-file
        his_reader.LeesMetadata(os.path.join(his_folder, '{0}.his'.format(his_file).upper()))
        # get dataframe for single location/parameter combination
        df = his_reader.EnkeleWaardenArray(
            location=location, 
            parameter=parameter.ljust(20), 
            jaarmax_as='none')
        return df
        
    def prepare_bui_his(self, df_his, df_bui, bui_locations='auto', bui_locations_aantal=10):
        """
        Prepare parameters from bui- and his-file for plotting purposes
        
        Parameters
        ----------
        his_file : str
            name of his-file to query (e.g: 'reachseg', 'calcpnt', 'struc')
        location : str
            location to query in his-file
        parameter : str
            parameter to query in his-file
        his_folder : str
            path to folder containing the his_file
        df_bui : 
        
        bui_locations : str or list
            welke bui_locations worden gebruikt om een selectie te maken in de
            bui-file, if 'bui_locations' is 'auto', dan worden de eerste x locations gebruikt
            (waar x = 'bui_locations_aantal')    
        bui_locations_aantal : int
            aantal locations mee te nemen tijdens plotten wanneer 'auto' is 
            opgegeven voor parameter 'bui_locations' (default: 10)
        
        Returns
        -------
        df_his : pandas.DataFrame
            timeseries containing all available timesteps in his-file
        df_bui_sel : pandas.DataFrame
            timeseries containing selection of bui-file, aligning with his-file
        start_his : datetime
            first datetime step of his-file
        end_his : datetime
            last datetime step of his-file
        df_bui_std : float
            standard deviation of timeseries selection bui-file
        df_his_std : float
            standard deviation of timeseries his-hile
        """
      
        start_his  = df_his.index[0]
        end_his    = df_his.index[-1]    
        df_bui_sel = df_bui.loc[start_his-pd.DateOffset(1):end_his+pd.DateOffset(1)]
        if df_bui_sel.values.size == 0:
            raise ValueError("""
            cannot slice bui-file, seems time-period does not align with his-file
            time-period his-file: {0} - {1}
            time-period bui-file: {2} - {3}    
            """.format(df_his.index[0], df_his.index[-1], df_bui.index[0], df_bui.index[-1]))  
            
    #     # create dummy waarden voor df_bui_sel
    #     for loc in df_bui_sel.columns:
    #         df_bui_sel.loc[df_bui_sel[loc] == 0,loc] = df_bui_sel[loc].apply(lambda x: np.random.normal(0,1))   
         
        if bui_locations == 'auto':
            df_bui_sel = df_bui_sel.iloc[:, 0:bui_locations_aantal]
        if isinstance(bui_locations, list):
            df_bui_sel = df_bui_sel.loc[:, bui_locations]

        df_his_std = np.std(df_his.values)
        df_bui_std = np.std(df_bui_sel.values)
        if df_bui_std == 0.:
            df_bui_std = 0.5
        if df_his_std == 0.:
            df_his_std = 0.5 
        
        return df_bui_sel, start_his, end_his, df_bui_std, df_his_std
        
    def plot_bui_his(self, df_his, df_bui_sel, start_his, end_his, df_bui_std, df_his_std, his_file, parameter, location, out_folder, savefigure):
        fig, ax1 = plt.subplots(figsize=(8,6))
        ax2 = ax1.twinx()

        # AXIS 1 :: his-file
        ax1.plot(df_his.index, df_his.values,color='#BFD600',marker='o',lw=4,label=parameter)
        ax1.set_xlim(start_his,end_his)
        ax1.set_ylabel(parameter)
        ax1.tick_params(labelbottom='on',labeltop='off', labelright="off",labelleft='on')
        ax1.set_ylabel(parameter,rotation=90)
        ax1.set_yticks(np.linspace(ax1.get_ybound()[0]-(df_his_std/2), ax1.get_ybound()[1]+df_his_std, 5))
        ax1.grid(True, axis='y')
        leg=ax1.legend(bbox_to_anchor=(0, 0.02),loc=3,prop={'size':10},ncol=5)
        leg.draw_frame(False)

        # AXIS 2 :: bui-file, width=barwidth,
        colors = [ cm.Greys(x) for x in np.linspace(0.2, 1.0, len(df_bui_sel.columns)) ]
        for y_arr, label, color in zip(df_bui_sel.values.T, df_bui_sel.columns, colors):
            ax2.plot(df_bui_sel.index, y_arr, label='P.{0} (mm)'.format(label), lw=1.5,color=color)
            ax2.fill_between(df_bui_sel.index, 0, y_arr, color=color,alpha=0.05)
        ax2_ylim = ax2.get_ylim()[::-1]
        bottom = max(max(0,ax2_ylim[0]),max(df_bui_std,ax2_ylim[1]))
        top = min(max(0,ax2_ylim[0]),max(df_bui_std,ax2_ylim[1]))
        ax2.set_ylim(top=top, bottom=bottom)
        ax2.set_xlim(start_his,end_his)
        ax2.tick_params(labelbottom='off',labeltop='on', labelright="on",labelleft='off')
        ax2.set_ylabel('Neerslag (mm)',rotation=90)
        ax2.set_yticks(np.linspace(0, ax2.get_ybound()[1]+df_bui_std, 5))
        leg=ax2.legend(bbox_to_anchor=(1.52, 0.02),loc=4,prop={'size':10},ncol=1)
        leg.draw_frame(False)

        # fix zorder
        ax1.set_zorder(ax2.get_zorder()+1) # put ax1 in front of ax2 
        ax1.patch.set_visible(False) # hide the 'canvas'
        #ax2.patch.set_visible(False) # hide the 'canvas'

        plt.title('location: '+location)
        plt.tight_layout()
        if savefigure == False:            
            plt.show()
            return
        else:   
            his_file = "".join(re.findall("[A-Za-z0-9]", his_file))
            location = "".join(re.findall("[A-Za-z0-9]", location))
            parameter = "".join(re.findall("[A-Za-z0-9]", parameter))
            path = os.path.join(out_folder,'{0}_{1}_{2}'.format(his_file,location,parameter))
            #print(path)
            plt.savefig(path, dpi=100, bbox_inches='tight')
            plt.close(fig) 
            return
        
    def table_bui_his(self, df_his, df_bui_sel, savetable=False, his_file='', his_parameter='', his_location='', out_folder=''):
        """
        write table from combined his-file and bui-file
        
        Parameters
        ----------
        df_his : pandas.DataFrame
        df_bui_sel : pandas.DataFrame
        his_file : str
        his_parameter : str
        his_location : str
        out_folder : str
        
        Returns
        -------
        df_bui_his : pandas.DataFrame
        """
        # include new index level on column
        df_bui_sel = pd.concat([df_bui_sel], keys=['Precipitation (mm)'], names=['parameter'], axis=1)
        # add column description
        df_bui_sel.columns.levels[1].name='location'
        # reorder levels of bui-file
        df_bui_sel = df_bui_sel.reorder_levels(['location','parameter'], axis=1)
        # concatenate both dataframes
        df_bui_his = pd.concat((df_his,df_bui_sel), axis=1, join='outer')
        # save to csv
        if savetable==True:
            his_file = "".join(re.findall("[A-Za-z0-9]", his_file))
            his_location = "".join(re.findall("[A-Za-z0-9]", his_location))
            his_parameter = "".join(re.findall("[A-Za-z0-9]", his_parameter))
            path = os.path.join(out_folder,'{0}_{1}_{2}.csv'.format(his_file,his_location,his_parameter))
            #print(path)
            df_bui_his.to_csv(path)
            return
        else:
            return df_bui_his

        
    def EnsembleRunner(self, shp_file, bui_file, his_folder, out_folder, 
                       shp_hiskey, shp_locationkey, shp_parameterkey, savefigure=True,
                       bui_locations='auto', bui_locations_aantal=10, savetable=True):
        
        """
        bui_file = r'input_data\plausibiliteits-validatie\P798.bui'
        his_folder = r'input_data\plausibiliteits-validatie'
        shp_file = r'input_data\plausibiliteits-validatie\plaus_locations.shp'
        bui_locations = 'auto'
        bui_locations_number = 10
        his_key = 'his_file'
        location_key = 'locations'
        parameter_key = 'parameters'
        out_folder = 
        savefigure = True
        """
        print('start ensemble runner')
        gdf = gpd.read_file(shp_file)
        print('read shp-file')
        df_bui = bui_reader.read_bui(bui_file)
        print('read bui-file')
        progress_bar = tqdm(gdf.T)
        for idx in progress_bar:        
            row = gdf.iloc[idx,:]
            progress_bar.set_description("location %s" % row[shp_locationkey].ljust(21))
            his_file = row[shp_hiskey]
            location = row[shp_locationkey]
            parameter = row[shp_parameterkey]
            
            # read his-file
            df_his = self.read_his_series(his_file, location, parameter, his_folder)
            
            # prepare files for plotting
            df_bui_sel, start_his, end_his, df_bui_std, df_his_std = self.prepare_bui_his(
                df_his, df_bui, 
                bui_locations=bui_locations, 
                bui_locations_aantal=bui_locations_aantal)
            
            # plot the figure
            self.plot_bui_his(df_his, df_bui_sel, start_his, end_his, 
                            df_bui_std, df_his_std, his_file, parameter, 
                            location, out_folder, savefigure)
        return (print('done'))
