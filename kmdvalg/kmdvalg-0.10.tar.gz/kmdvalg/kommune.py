# -*- coding: utf-8 -*-
import os.path
import numpy as np
import datetime
import bokeh.models as bm

def check_isnotebook():
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            # Jupyter notebook or qtconsole
            return True
        elif shell == 'TerminalInteractiveShell':
            # Terminal running IPython
            return False
        else:
            # Other type (?)
            return False
    except NameError:
         # Probably standard Python interpreter
        return False


class data:
    def __init__(self,):
        pass

    def get_kommuner(self):
        import requests
        from bs4 import BeautifulSoup

        # Get the page
        r = requests.get('https://www.kmdvalg.dk/Main/Home/KV')
        # Make soup
        soup = BeautifulSoup(r.text, "html.parser")

        # Get kommune items
        kmd_list_items = soup.find("div", {"class": "col-sm-12 content-block kmd-list-items"})
        
        # Find lists in kommune
        kmd_list_items_group = kmd_list_items.find_all("div", {"class": "list-group"})

        # Loop over letter in groups
        kommuner = []
        kommuner_links = {}
        for group in kmd_list_items_group:
            list_group_item = group.find("div", {"class": "list-group-item"})
            group_links = group.find_all('a')
            for link in group_links:
                #print(list_group_item.text, link.text)
                kommuner.append([list_group_item.text.strip(), link.text.strip(), link['href']])
                kommuner_links[link.text.strip()] = link['href']

        self.kommuner = kommuner
        self.kommuner_links = kommuner_links
    
    def get_kommune_dic(self, kommune=None):
        from bs4 import BeautifulSoup
        import requests

        # Check if exists
        if not hasattr(self, 'kommuner_links'):
            self.get_kommuner()

        # Get link
        link = self.kommuner_links[kommune]
        # Get the page
        r = requests.get(link)
        # Make soup
        soup = BeautifulSoup(r.text, "html.parser")

        # Get columns with data
        col_xs_6_list = soup.find_all("td", {"class": "col-xs-6"})
        for i, col_xs_6 in enumerate(col_xs_6_list):
            if "Antal stemmeberettigede" in col_xs_6.text:
                Antal_stemmeberettigede = [col_xs_6.text, int(col_xs_6.findNext('td').text.replace(".", ""))]
            if "Afstemningsomr" in col_xs_6.text:
                Afstemningsomr = [col_xs_6.text, int(col_xs_6.findNext('td').text)]
            if "I alt gyldige stemmer" in col_xs_6.text:
                I_alt_gyldige_stemmer = [col_xs_6.text, int(col_xs_6.findNext('td').text.replace(".", ""))]
            if "I alt afgivne stemmer" in col_xs_6.text:
                I_alt_afgivne_stemmer = [col_xs_6.text, int(col_xs_6.findNext('td').text.replace(".", ""))]

        # Calculate vote percentage
        stemme_pct = ["Stemme pct.", round(I_alt_afgivne_stemmer[-1] / Antal_stemmeberettigede[-1] *100, 2)]
        # Make dictionary with data
        d = {
            'kommune' : ["Kommune", kommune],
            'Antal_stemmeberettigede' : Antal_stemmeberettigede,
            'Afstemningsomr' : Afstemningsomr,
            'I_alt_gyldige_stemmer' : I_alt_gyldige_stemmer,
            'I_alt_afgivne_stemmer' : I_alt_afgivne_stemmer,
            'stemme_pct' : stemme_pct
        }

        return d

    def get_kommuner_df(self, n=None, make=False):
        import pandas as pd

        # If file exists
        df_file = "Valg2017_kommune.pkl"

        if os.path.isfile(df_file) and not make:
            print("Kommune data exists. Reading it.")
            df = pd.read_pickle(df_file)
        else:
            print("Kommune data missing. Creating it.")
            # Collect
            kommune_list = []
            Antal_stemmeberettigede_list = []
            Afstemningsomr_list = []
            I_alt_gyldige_stemmer_list = []
            I_alt_afgivne_stemmer_list = []
            stemme_pct_list = []

            # Loop over kommuner
            if n:
                kommuner = self.kommuner[:n]
            else:
                kommuner = self.kommuner
            for kommune in kommuner:
                print("Reading for:", kommune)
                # Get kommune
                kommune_dic = self.get_kommune_dic(kommune[1])
                # Append to lists
                kommune_list.append(kommune_dic['kommune'][-1])
                Antal_stemmeberettigede_list.append(kommune_dic['Antal_stemmeberettigede'][-1])
                Afstemningsomr_list.append(kommune_dic['Afstemningsomr'][-1])
                I_alt_gyldige_stemmer_list.append(kommune_dic['I_alt_gyldige_stemmer'][-1])
                I_alt_afgivne_stemmer_list.append(kommune_dic['I_alt_afgivne_stemmer'][-1])
                stemme_pct_list.append(kommune_dic['stemme_pct'][-1])
            
            # Make dictionary to pandas
            d = {
                'Kommune' : kommune_list,
                'Stemmeberettigede' : Antal_stemmeberettigede_list,
                'Afstemningsomr' :Afstemningsomr_list,
                'Gyldige_stemmer' : I_alt_gyldige_stemmer_list,
                'Afgivne_stemmer' : I_alt_afgivne_stemmer_list,
                'stemme_pct' : stemme_pct_list
            }
            # Create
            df = pd.DataFrame.from_dict(d)
            # Re-order
            df = df[['Kommune', 'Stemmeberettigede', 'Afstemningsomr', 'Gyldige_stemmer', 'Afgivne_stemmer', 'stemme_pct']]
            # Store
            df.to_pickle(df_file)

        return df
    
class kmap:
    # Data fra https://download.kortforsyningen.dk
    # "Indeholder data fra Styrelsen for Dataforsyning og Effektivisering”
    # Navnet på datasættet(ene): Digdag (Kommunal)
    # Tidspunkt, hvor datasættet(ene) er hentet hos myndigheden, eller om der er tale om en datatjeneste. : 2017/12/03
    def __init__(self, make=False):
        import pickle

        # If file exists
        dic_file = "Kommune.pkl"
        if os.path.isfile(dic_file) and not make:
            print("Kommune shapefile exists. Reading it.")
            with open(dic_file, 'rb') as f:
                self.kdic = pickle.load(f)
        # Create it
        else:
            print("Kommune shapefile missing. Creating it.")
            import shapefile
            myshp = open("Kommune.shp", "rb")
            mydbf = open("Kommune.dbf", "rb")
            sf = shapefile.Reader(shp=myshp, dbf=mydbf)
            sf_list = list(sf.shapeRecords())
            print('number of shapes imported:',len(sf.shapes()) )

            kommune_date_min = datetime.datetime.strptime('2006-01-01', '%Y-%m-%d')
            # From: https://chrishavlin.wordpress.com/2016/11/16/shapefiles-tutorial/
            # First loop to check time
            sel_kommuner = []
            sel_times = []
            for i, shape in enumerate(sf_list):
                # Get date string and store
                kommune_date_str = shape.record[3]
                # Get time object
                kommune_date = datetime.datetime.strptime(kommune_date_str, '%Y-%m-%d')
                # Skip if shape time is less than minimum date
                if kommune_date < kommune_date_min:
                    continue
                # Get kommune
                kdata = shape.record[1]
                if isinstance(kdata, (bytes, bytearray)):
                    kommune = kdata.decode("latin-1")
                else:
                    kommune = kdata
                kommune = kommune.split(" Kommune")[0]
                # Test kommune exists
                if kommune not in sel_kommuner:
                    sel_kommuner.append(kommune)
                    sel_times.append(kommune_date)
                else:
                    index = sel_kommuner.index(kommune)
                    prev_time = sel_times[index]
                    # Replace
                    if kommune_date > prev_time:
                        sel_times[index] = kommune_date

            # Loop again
            # Collect
            kommuner_list = []
            kommune_dates_list = []
            x_lon_list = []
            y_lat_list = []
            stemme_pct_list = []
            self.kdic = {}

            j = 0
            for i, shape in enumerate(sf_list):
                # Get kommune
                kdata = shape.record[1]
                if isinstance(kdata, (bytes, bytearray)):
                    kommune = kdata.decode("latin-1")
                else:
                    kommune = kdata
                kommune = kommune.split(" Kommune")[0]
                # Get date string and store
                kommune_date_str = shape.record[3]
                # Get time object
                kommune_date = datetime.datetime.strptime(kommune_date_str, '%Y-%m-%d')
                if kommune in sel_kommuner:
                    index = sel_kommuner.index(kommune)
                    prev_time = sel_times[index]
                    # If time matches from before
                    if kommune_date == prev_time:
                        npoints=len(shape.shape.points) # total points
                        nparts = len(shape.shape.parts) # total parts
                        if nparts == 1:
                            x_lon = np.zeros((len(shape.shape.points),1))
                            y_lat = np.zeros((len(shape.shape.points),1))
                            for ip in range(len(shape.shape.points)):
                                x_lon[ip] = shape.shape.points[ip][0]
                                y_lat[ip] = shape.shape.points[ip][1]
                            # Collect
                            kommuner_list.append(kommune)
                            kommune_dates_list.append(kommune_date_str)
                            x_lon_list.append(x_lon)
                            y_lat_list.append(y_lat)
                            # Add to counter
                            j += 1

                        else: # loop over parts of each shape, plot separately
                            for ip in range(nparts): # loop over parts, plot separately
                                i0=shape.shape.parts[ip]
                                if ip < nparts-1:
                                    i1 = shape.shape.parts[ip+1]-1
                                else:
                                    i1 = npoints

                                seg=shape.shape.points[i0:i1+1]
                                x_lon = np.zeros((len(seg),1))
                                y_lat = np.zeros((len(seg),1))
                                for ip in range(len(seg)):
                                    x_lon[ip] = seg[ip][0]
                                    y_lat[ip] = seg[ip][1]
                                # Collect
                                kommuner_list.append(kommune)
                                kommune_dates_list.append(kommune_date_str)
                                x_lon_list.append(x_lon)
                                y_lat_list.append(y_lat)
                            # Add to counter
                            j += 1
            # Print
            print('number of shapes stored:', j )
            # Store all kommuner
            self.kdic['kommuner'] = kommuner_list
            self.kdic['x_lon'] = x_lon_list
            self.kdic['y_lat'] = y_lat_list
            self.kdic['kommuner_dates'] = kommune_dates_list
            # Save
            with open(dic_file, 'wb') as f:
                pickle.dump(self.kdic, f, pickle.HIGHEST_PROTOCOL)

    def make_map_source(self, df=None):
        # Test if there exists data
        if type(df) != type(None):
            # Make copy of dict
            kdic = self.kdic.copy()
            # Collect
            stemme_pct_list = []
            # Loop through dic
            for i, kommune in enumerate(kdic['kommuner']):
                #kommune_date = kdic['kommuner_dates'][i]
                #print(kommune.replace("Aa", "Å"))
                if kommune in df['Kommune'].values:
                    stemme_pct = df.loc[df['Kommune'] == kommune, 'stemme_pct'].iloc[0]
                    stemme_pct_list.append(stemme_pct)
                # If s is added
                elif kommune[:-1] in df['Kommune'].values:
                    stemme_pct = df.loc[df['Kommune'] == kommune[:-1], 'stemme_pct'].iloc[0]
                    stemme_pct_list.append(stemme_pct)
                elif kommune+"s" in df['Kommune'].values:
                    stemme_pct = df.loc[df['Kommune'] == kommune+"s", 'stemme_pct'].iloc[0]
                    stemme_pct_list.append(stemme_pct)
                elif kommune.replace("Å", "Aa").replace("å", "aa").replace("Høje Taastrup","Høje-Taastrup") in df['Kommune'].values:
                    stemme_pct = df.loc[df['Kommune'] == kommune.replace("Å", "Aa").replace("å", "aa").replace("Høje Taastrup","Høje-Taastrup"), 'stemme_pct'].iloc[0]
                    stemme_pct_list.append(stemme_pct)
                else:
                    #print(kommune, "Not found")
                    stemme_pct_list.append(None)
            # append
            kdic['stemme_pct'] = stemme_pct_list
            # Create data
            self.source = bm.ColumnDataSource(data=kdic)
            
        else:
            print("Making source from map")
            self.source = bm.ColumnDataSource(data=self.kdic)

    def get_map(self):
        import bokeh.plotting as bplt

        wheel_zoom = bm.WheelZoomTool()
        self.hover = bm.HoverTool(tooltips=[
            ("Navn", "@kommuner"),
            #("(Long, Lat)", "($x, $y)"),
            ("Dato", "@kommuner_dates"),
            ("stemme pct", "@stemme_pct %"),
            ])
        self.hover.point_policy = "follow_mouse"
        tools = [bm.PanTool(), bm.BoxZoomTool(), wheel_zoom, bm.SaveTool(), bm.ResetTool(), bm.UndoTool(), bm.RedoTool(), bm.CrosshairTool(), self.hover]
        fig = bplt.figure(title="Test", tools=tools, x_axis_location=None, y_axis_location=None, match_aspect=True)
        # Activate scrool
        fig.toolbar.active_scroll = wheel_zoom
        # Remove grid lines
        fig.grid.grid_line_color = None

        # Check if source exists
        if not hasattr(self, 'source'):
            self.make_map_source()

        # Plot
        fig.patches(xs='x_lon', ys='y_lat', source=self.source, line_color="firebrick")
          #fill_color={'field': 'rate', 'transform': color_mapper},
          #fill_alpha=0.7, line_color="white", line_width=0.5)

        return fig