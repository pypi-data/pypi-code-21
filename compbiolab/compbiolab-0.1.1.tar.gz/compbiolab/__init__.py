import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import string

check = sns.__version__
check2 = check.split('.')
if int(check2[1]) <= 7:
    print('\x1b[4;30;41m'+'WARNING!!'+'\x1b[0m'+'\x1b[3;30;41m'+' The detected seaborn version installed is below 0.8.0! ('+str(check)+')\nSome utilities of the seaborn v0.8.0 are used in this module\n'+'\x1b[0m'+'\x1b[3;30;43m'+'UPGRADE SEABORN!'+'\x1b[0m')

color_default = ('#aa00ff','#FF8C00','#DC143C','#008B8B','#1E90FF','#FF1493','#4B0082','#FF69B4','#32CD32')
names_default = ('Serie 1', 'Serie 2', 'Serie 3', 'Serie 4', 'Serie 5', 'Serie 6', 'Serie 7', 'Serie 8', 'Serie 9')
palette_default = ((sns.blend_palette(('#FFFFFF', '#9966CC', '#9966CC', '#aa00ff'), n_colors=30, as_cmap=True)),(sns.blend_palette(('#FFFFFF', '#ffc57f','#ffc57f' ,'#FF8C00' ), n_colors=30, as_cmap=True)))
palette_default_r = ((sns.blend_palette(('#aa00ff', '#9966CC','#9966CC' ,'#FFFFFF' ), n_colors=30, as_cmap=True)),(sns.blend_palette(('#FF8C00', '#ffc57f','#ffc57f' ,'#FFFFFF' ), n_colors=30, as_cmap=True)))


def plot_dist(data, legend=True, names='default' , color='default', window_size=50, style='default', font_scale=2, figure_size=(20,10), title=False, x_label='nanoseconds', y_label=False, x_limits='default', y_limits='default', vertical_lines=False, horizontal_lines=False,  line_width=1, x_label_fontsize=18, y_label_fontsize=18, read_every=1):
    '''
        
        Plot one or more timeseries with flexible and multiple options for the CompBioLab.
        
        This function is intended to be used with data extracted from MD silulations, such as: distances, angles, dihedrals, rmsd, etc.
        
        This function can display the row data (window_size=1) or the mean calculated every window_size, and the deviation is displayed as a 'unit_traces' (check seaborn tsplot).
        
        The default values are only prepared to plot a maximum numbers of 9 timeseries, if you want to plot more than 9 (not recomended, because the plot will become crowded), modify the default parameters.
        
        If you experience some problem or you have any comment with this function --> miqueleg@gmail.com :p
        
        Parameters: ---------------------------------------------------------------------------------
        
        data: list, nested list or ndarray
        Data for the plot. This data is the Y values. Be aware that the NAN values can make your plots weird.
        Headers has not to be included in the array. Remove all strings from the data
        
        legend: boolean(True or False)
        Set legend to True to display a legend in the plot
        
        names: list of strings
        Set the names of the series displayed on the legend.
        The 'default' will show Serie 1, Serie 2, etc.
        
        color: list of strings
        List of the colors for the series. Seaborn, matplotlib and Hex formats are accepted.
        In general are not recomended to change the 'default' mode. The 'default' colors are cool!
        
        window_size: integer
        Width of the window of values that are used to calculate the mean in each position.
        If this value is higher, more noise are removed, but also more information.
        
        style: string or None
        Seaborn style used for the plot(nore information on the seaborn webpage).
        If 'default' is used, the style will be 'whitegrid'. Also, 'darkgrid' is recomended too.
        
        font_scale: integer
        Multiplying factor of fontsize of all letters on the plot.
        
        figure_size: list of two integers
        Dimensions of the resulting image.
        
        title: string or False
        Title that will be displayed.
        
        x_label: string of False
        Name of the X axis that will be displayed in the plot.
        
        y_label: string of False
        Name of the Y axis that will be displayed in the plot.
        
        x_limits: 'default' or list of two integers
        The 'default' mode will display the plot with tightened X axis limits that will change for each series.
        *This parameter cannot be 'default' if you use the horizontal_line parameter.
        
        y_limits: 'default' or list of two integers
        The 'default' mode will display the plot with tightened Y axis limits that will change for each timeseries.
        *This parameter cannot be 'default' if you use the vertical_line parameter.
        
        vertical_lines: False, integer or list of integers
        This paremeter will add a line (or multiple lines) parellel to the Y axis at the selected X position.
        *If this parameter is not False, then the y_limits parameter cannot be in 'default' mode.
        
        horizontal_lines: False, integer or list of integers
        This paremeter will add a line (or multiple lines) parellel to the X axis at the selected Y position.
        *If this parameter is not False, then the x_limits parameter cannot be in 'default' mode.
        
        line_width: integer or floating point
        Value that sets the width of the lines in the plot.
        
        x_label_fontsize: integer
        Value that sets the size of the font that makes the x_label parameter.
        
        y_label_fontsize: integer
        Value that sets the size of the font that makes the y_label parameter.
        
        read_every: integer or floating point
        Value that changes the values of the X axis to fit correctly with the time unit used.
        The default value is calibrated for cpptraj outputs in MD simulations written every 10000 steps (GALATEA),
        and readed every 1
        
        Returns: -------------------------------------------------------------------------------------------
        
        In jupyter-notebook (RECOMENDED!)
        put the command '%matplotlib inline' before this command to automatically display the output
        
        
        '''
    
    C = read_every*0.02
    
    #Function called as estimator in tsplot(seaborn), for 'removing sound'
    def rolling_mean(data, axis=0, WS=window_size):
        return pd.rolling_mean(data, WS, axis=1).mean(axis=axis)
    
    
    #Selecting the variables depending if they are 'default', str, or list(in a multiple plot)
    if color == 'default':
        color = color_default
    elif type(color) == str:
        color=[color, '0']
    
    if names == 'default':
        names = names_default
    elif type(names) == str:
        names=[names, '0']
    
    if style == 'default':
        style = 'whitegrid'
    
    
    #Applying variables that will appear always(specs)
    sns.set(font_scale=font_scale, rc={"lines.linewidth":line_width})
    plt.figure(figsize=figure_size)
    sns.set_style(style)



    #The if checking legend, is here because the legend depends on the 'condition' in the tsplot command.
    #The plots in the true has this condition and in the else, not.
    if legend == True:
    
    #Then, the correct tsplots are selected in the try/except, depending on the number of 'datas'
        try:
            sns.tsplot(data, time=np.array(range(len(data)))*C, estimator=rolling_mean, err_style='unit_traces', color=color[0], condition=names[0])
        
        except:
            lst = list(range(len(data)))
            for l in lst:
                sns.tsplot(data[l], time=np.array(range(len(data[l])))*C, estimator=rolling_mean, err_style='unit_traces', color=color[l], condition=names[l])
        plt.legend(loc='upper left', bbox_to_anchor=(1,1))



    elif legend == False:
    
        try:
            sns.tsplot(data, time=np.array(range(len(data)))*C, estimator=rolling_mean, err_style='unit_traces', color=color[0])
        
        except:
            lst = list(range(len(data)))
            for l in lst:
                sns.tsplot(data[l], time=np.array(range(len(data[l])))*C, estimator=rolling_mean, err_style='unit_traces', color=color[l])


    #Post-plotting modifications
    plt.axvline(color='k')
    plt.axhline(color='k')
    
    ##Applying variables that will not appear if they are in 'default'/False
    if title:
        plt.title(title)

    if x_label:
        plt.xlabel(x_label, fontsize=x_label_fontsize)
    
    if y_label:
        plt.ylabel(y_label, fontsize=y_label_fontsize)

    if x_limits != 'default':
        plt.xlim(x_limits)
    
    if y_limits != 'default':
        plt.ylim(y_limits)
    else:
        try:
            ymin = min([min(data),0])
            ymax = max(data)
        except:
            ymin = min([min([min(y) for y in data]),0])
            ymax = max([max(y) for y in data])
        plt.ylim(ymin,ymax)

    if vertical_lines:
        plt.vlines(vertical_lines, y_limits[0], y_limits[1])
    
    if horizontal_lines:
        plt.hlines(horizontal_lines,x_limits[0], x_limits[1])


#---------------------------------------------------------------------------------------------------------------

def read_pdb(pdb_path, header=False):
    '''
        This function returns a pandas.DataFrame object that contains the information if the .pdb.
        
        Arguments:
        
        - pdb_path: string with the file location
        
        - header: If header is True, you are saying that the PDB file has header that has to be ommited.
        
        Returns: pandas.DataFrame
        '''
    
    colspecs = [(0, 6), (6, 11), (12, 16), (16, 17), (17, 20), (21, 22), (22, 26),
                (26, 27), (30, 38), (38, 46), (46, 54), (54, 60), (60, 66), (76, 78),
                (78, 80)]
        
    names = ['ATOM', 'serial', 'name', 'altloc', 'resname', 'chainid', 'resid',
                 'icode', 'x', 'y', 'z', 'occupancy', 'tempfactor', 'element', 'charge']
            
    pdb = pd.read_fwf(pdb_path, names=names, colspecs=colspecs)
                
    if header:
        pdb = pdb[pdb[pdb['ATOM'] == 'ATOM'].index[0]:]

    return pdb


#---------------------------------------------------------------------------------------------------------------
def change_his(input_file, output_file, HIE=(), HID=()):
    '''
        Function that creates a new file with the provided changes from the HIS to HIE or HID.
        
        Arguments:
        
        - input_file: string with the input file location and name.
        
        - output_file: string with the output file locationand name.
        
        - output_file: string with the output file locationand name.
        
        - HIE: list of residues numbers that will be changed to from HIS to HIE. The list can be empty.
        
        - HID: list of residues numbers that will be changed to from HIS to HID. The list can be empty.
        
        Returns: nothing
        
        '''
    
    HIE = [str(x) for x in HIE]
    HID = [str(x) for x in HID]
    
    inp = open(input_file, 'r')
    out = open(output_file, 'w')
    i = 0
    for line in inp.readlines():
        i += 1
        try:
            if line.split()[4] in HIE:
                line = string.replace(line, 'HIS','HIE')
            elif line.split()[4] in HID:
                line = string.replace(line, 'HIS','HID')
            out.write(line)
        except:
            out.write(line)
    inp.close()
    out.close()


#---------------------------------------------------------------------------------------------------------------
def change_asp(input_file, output_file, ASH):
    '''
        Function that creates a new file with the provided changes from the ASP to ASH.
        
        Arguments:
        
        - input_file: string with the input file location and name.
        
        - output_file: string with the output file locationand name.
        
        - ASH: list of residues numbers that will be changed to from ASP to ASH.
        
        
        Returns: nothing
        
        '''
    
    ASH = [str(x) for x in ASH]
    
    inp = open(input_file, 'r')
    out = open(output_file, 'w')
    i = 0
    for line in inp.readlines():
        i += 1
        try:
            if line.split()[4] in ASH:
                line = string.replace(line, 'ASP','ASH')
            out.write(line)
        except:
            out.write(line)
    inp.close()
    out.close()


#---------------------------------------------------------------------------------------------------------------

def change_glu(input_file, output_file, GLH):
    '''
        Function that creates a new file with the provided changes from the GLU to GLH.
        
        Arguments:
        
        - input_file: string with the input file location and name.
        
        - output_file: string with the output file locationand name.
        
        - GLH: list of residues numbers that will be changed to from GLU to GLH.
        
        
        Returns: nothing
        
        '''
    
    GLH = [str(x) for x in GLH]
    
    inp = open(input_file, 'r')
    out = open(output_file, 'w')
    i = 0
    for line in inp.readlines():
        i += 1
        try:
            if line.split()[4] in GLH:
                line = string.replace(line, 'GLU','GLH')
            out.write(line)
        except:
            out.write(line)
    inp.close()
    out.close()
