'''
This is the main entry point for the Sinbad library. Use the various 
connect*(...) methods to instantiate a data source. See the full
documentation for more details on usage.
'''

from jsonpath_rw import parse
from zipfile import ZipFile, BadZipfile
import urllib.parse
import random
import json
import io
import os
import sys

import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

import sinbad.cacher as C
import sinbad.describe as D
import sinbad.util as U
import sinbad.prefs

from sinbad import plugin_csv
from sinbad import plugin_json
from sinbad import plugin_satori
from sinbad import plugin_xml

from sinbad.sinbad_error import *
from sinbad.dot_printer import Dot_Printer
from sinbad.prefs import get_pref
from sinbad.comm import register_load, register_sample, register_fetch

from collections import OrderedDict


class Data_Source:
    
    __predefined_plugins = [ { "name" : "JSON (built-in)", 
                               "type-ext" : "json",
                               "data-infer" : plugin_json.JSON_Infer(),
                               "data-factory" : plugin_json.JSON_Data_Factory },
                            { "name" : "XML (lxml)", 
                               "type-ext" : "xml",
                               "data-infer" : plugin_xml.XML_Infer(),
                               "data-factory" : plugin_xml.XML_Data_Factory },
                            { "name" : "CSV (built-in)",
                               "type-ext" : "csv",
                               "data-infer" : plugin_csv.CSV_Infer(),
                               "data-factory" : plugin_csv.CSV_Data_Factory },
                            { "name" : "TSV (built-in)",
                               "type-ext" : "tsv",
                               "data-infer" : plugin_csv.CSV_Infer(delim = '\t'),
                               "data-factory" : plugin_csv.CSV_Data_Factory },
                            { "name" : "Satori",
                               "type-ext" : "satori",
                               "data-infer" : plugin_satori.Satori_Infer(),
                               "data-factory" : plugin_satori.Satori_Data_Factory}
                        ]
    
    plugins = __predefined_plugins


    @staticmethod
    def preferences(**kw_args):
        sinbad.prefs.preferences(**kw_args)

    
    @staticmethod
    def connect(path, format = None):
        if format is None:  # infer it...
            for p in Data_Source.plugins:
                if p["data-infer"].matched_by(path):
                    return Data_Source(path, path, p["type-ext"], p)
            raise SinbadError('could not infer data format for {}'.format(path))
        else:
            type_ext = format.lower()
            for p in Data_Source.plugins:
                if p["type-ext"] == type_ext:
                    return Data_Source(path, path, type_ext, p)
    
            raise SinbadError("no data source plugin for type {}".format(type_ext))
            
        
    @staticmethod
    def connect_load(path, format = None):
        ds = Data_Source.connect(path, format = format)
        return ds.load()

    @staticmethod
    def connect_as(type_ext, path):
        return Data_Source.connect(path, format = type_ext)    
    
    @staticmethod
    def connect_load_as(type_ext, path):
        return Data_Source.connect_load(path, format = type_ext) 
    
    @staticmethod
    def connect_gui(format = None):
        root = tk.Tk()
        root.withdraw()
        U.tk_to_front(root)
        
        file_path = filedialog.askopenfilename()
        file_path = os.path.abspath(file_path)
        messagebox.showinfo("Selected file path", file_path + "\nSelect and copy the file path above for use with connect()")
        root.destroy()

        return Data_Source.connect(file_path, format=format)

    
    @staticmethod
    def connect_gui_as(type_ext):
        return Data_Source.connect_gui(format = type_ext)
    
        
    @staticmethod
    def connect_using(spec_path):
        return load_spec(U.create_input(spec_path))   
    
    
    @staticmethod
    def connect_load_using(spec_path):
        ds = load_spec(U.create_input(spec_path))
        return ds.load()


    def clear_cache(self = None):
        '''
        If invoked as a static method, deletes the default cache directory.
        If invoked on a Data_Source object, deletes its cache directory.
        '''
        if not self:
            C.default_cacher().clear_cache()
        else:
            return self.cacher.clear_cache()


    # constructor --------------------------------------------------------
    def __init__(self, name, path, typeExt, plugin):
        '''
        Rather than directly invoking this constructor, one should use 
        Data_Source.connect...() to instantiate objects of this class
        '''
        
        self.cacher = C.default_cacher()

        self.name = name
        self.path = path
        self.format_type = typeExt
        self.info_url = None
        self.info_text = None
        
        self.__connected = path and True
        self.__load_ready = False
        self.__loaded = False
        
        self.__random_index = None   # this is so that .fetch_random() actually returns the same position, until .load() is called again
        
        self.data_infer = plugin["data-infer"]
        self.data_factory = plugin["data-factory"]()
        self.data_obj = None
        self.is_sampled = False    # keeps track of whether self.data_obj is a sample of the actual data
        
        
        self.option_settings = {}  # these are generic options for Data_Source, the data_factory 
                                   # also maintains its own set of options (see plugin_base.py)
        
        # params are connection-related parameters, either in a query string or filling in part of the path 
        self.params = {} # keeps track of *all* parameters information available for this data source
        self.param_values = {} # keeps track of the values of the supplied parameters



    # pre-load() stuff -------------------------------------------------
    
    def has_data(self):
        return self.__connected and self.__loaded


    def get_full_path_url(self):
        if not self.__ready_to_load():
            raise SinbadError("Cannot finalize path: not ready to load")
        
        full_path = self.path
        
        # add query parameters to the URL
        param_keys = [k for k in self.param_values]  
        param_keys.sort()  # so that the URL doesn't differ, forcing a cache refresh unnecessarily because of reordering of dictionary keys
        query_params = OrderedDict()
        for k in param_keys:
            v = self.param_values.get(k)
            p = self.params.get(k)
            if not p or p.type == QUERY_PARAM:
                query_params[k] = v
        query_param_str = urllib.parse.urlencode(query_params)
        if query_param_str:
            full_path = full_path + "?" + query_param_str
        
        # fill in substitutions of path params
        for k, v in self.param_values.items():
            p = self.params.get(k)
            if p and p.type == PATH_PARAM:
                full_path = full_path.replace("@{" + k + "}", v)
        
        return full_path


    def __missing_params(self):
        missing = []
        for k, p in self.params.items():
            if p.required and not self.param_values.get(k):
                missing.append(k)
        return missing


    def __ready_to_load(self):
        self.__load_ready = self.__load_ready or len(self.__missing_params()) == 0        
        return self.__load_ready


    # load() variants --------------------------------------------------

    def load(self, force_reload = False):
        if not self.__connected: raise SinbadError("not __connected {}".format(self.path))
        if not self.__ready_to_load(): raise SinbadError("not ready to load; missing params: {}".format(self.__missing_params()))
        
        subtag = "main"
    
        full_path = self.get_full_path_url()
        stale_data = self.cacher.is_stale(full_path, subtag)
        
        if self.__loaded and not (stale_data or force_reload or self.is_sampled):
            self.__random_index = None   # this is so that .fetch_random() actually returns the same position, until .load() is called again
            return self
        
        # only share usage if permitted in preferences and if loading something that's not already been previously loaded and cached
        share_usage = get_pref("share_usage") \
                        and not self.cacher.cache_entry_for(full_path, subtag)
        if share_usage: usage_info = self.prep_usage_info()
        
        zfp, fp = (None, None)
        d = None
        try:
            d = Dot_Printer("Loading the data (this may take a moment)")
            d.start()
            
            resolved_path = self.cacher.resolve_path(full_path, subtag)
            if resolved_path == full_path:   # wasn't cached - loading it directly
                fp, real_name, enc = U.raw_create_input(resolved_path)
                if fp:
                    byts = fp.read()
                    fp = io.BytesIO(byts)
            else:
                fp = U.create_input(resolved_path)
                real_name = self.cacher.lookup_entry_data(full_path, "real-name")
                enc = self.cacher.lookup_entry_data(full_path, "enc")
            
            if fp and U.smells_like_zip(full_path) \
                    or (real_name and U.smells_like_zip(real_name)):
                try:
                    zf = ZipFile(fp)
                    members = zf.namelist()
                    
                    if 'file-entry' not in self.option_settings and len(members) is 1:
                        self.option_settings['file-entry'] = members[0]
                    
                    if 'file-entry' in self.option_settings and \
                            self.option_settings['file-entry'] in members:
                        
                        fe_value = self.option_settings['file-entry']
                        fe_subtag = "file-entry:{}".format(fe_value)
                        
                        entry_cached_path = self.cacher.resolve_path(full_path, fe_subtag)
                        if entry_cached_path:
                            zfp = U.create_input(entry_cached_path)                        
                        else: # not in the cache
                            enc = None
                            zfp = zf.open(fe_value)
                            if not self.cacher.add_to_cache(full_path, fe_subtag, zfp):
                                #print("something went wrong caching zip file-entry", file=sys.stderr)
                                zfp = zf.open(fe_value)
                            else:
                                zfp.close()
                                entry_cached_path = self.cacher.resolve_path(full_path, fe_subtag)
                                zfp = U.create_input(entry_cached_path)
    
                    else:
                        raise SinbadError("Specify a file-entry from the ZIP file: {}".format(members))
                
                except BadZipfile:
                    raise SinbadError("ZIP Failed: " + full_path)
                
            
            if not self.data_infer.matched_by(self.path):  # because options is only valid after matchedBy has been invoked
                self.data_infer.matched_by(full_path) 
            for k, v in self.data_infer.options.items():
                self.data_factory.set_option(k, v)
                
            self.data_obj = self.data_factory.load_data(zfp if zfp else fp if fp else resolved_path, enc)
            self.is_sampled = False
            
            self.__loaded = True
            self.__random_index = None   # this is so that .fetch_random() actually returns the same position, until .load() is called again
        finally:
            if d: d.stop()
            if zfp: zfp.close()
            if fp and hasattr(fp, 'close'): fp.close()
            if share_usage:
                if self.__loaded and self.data_obj: usage_info['status'] = 'success'
                else: usage_info['status'] = 'failure'
                register_load(usage_info)
            
        return self
    

    def load_sample(self, max_elts = 25, random_seed = None, force_reload = False):
        '''
        Load and then sample from all available data. See sample_data().
        The sampled data is cached. To reload the entire data and
        resample it, rather than using a previously-cached sample,
        use force_reload=True.
        '''
        #
        # look for cache subtag:   "sample:<max-elts>" in the cache
        # if  not there, or if stale, or if force_reload is True:
        #     load()
        #     sample the loaded data
        #     cache the sample (serialized as json)
        #     return the sample
        # otherwise
        #     load the cached sample (unserialize as json)
        #     return it
        #

        if not self.__connected: raise SinbadError("not __connected {}".format(self.path))
        if not self.__ready_to_load(): raise SinbadError("not ready to load; missing params...")
        
        full_path = self.get_full_path_url()
        
        if 'file-entry' in self.option_settings:
            fe_value = self.option_settings['file-entry']
            subtag = "sample:{}-{}_{}".format(fe_value, max_elts, random_seed)
        else:
            subtag = "sample:{}_{}".format(max_elts, random_seed)
            
        sample_path = self.cacher.resolve_path(full_path, subtag)
        if not sample_path or force_reload:
            self.load(force_reload = force_reload);
            if self.__loaded:
                sampled = self.sample_data(self.data_obj, max_elts, random_seed=random_seed)
                fp = io.BytesIO(json.dumps(sampled).encode()) 
                self.cacher.add_to_cache(full_path, subtag, fp)
                self.data_obj = sampled
                self.is_sampled = True
                if get_pref("share_usage"):
                    usage_info = self.prep_usage_info(False)
                    usage_info['sample_amt'] = max_elts
                    usage_info['sample_seed'] = random_seed
                    register_sample(usage_info)
        else: # sample seems to be cached
            fp = U.create_input(sample_path) 
            self.data_obj = json.loads(fp.read().decode(errors='ignore'))
            self.is_sampled = True
            self.__loaded = True    # copy these two lines because .load() didn't get called on this path of execution
            self.__random_index = None   # this is so that .fetch_random() actually returns the same position, until .load() is called again
        
        return self
    

    def load_fresh_sample(self, max_elts = 25, random_seed = None):
        '''
        Reload the entire data and resample it, rather than using the cached
        sample.
        '''
        return self.load_sample(max_elts = max_elts, random_seed = random_seed, force_reload = True)
    


    # fetch() variants ------------------------------------------------
    ### 
    def fetch_all(self):
        '''
        Return all available data.
        '''
        if not self.has_data():
            raise SinbadError("no data available - make sure you called load()")
        return self.data_obj


    def fetch(self, *field_paths, base_path = None, select = None):
        '''
        Returns data identified by field_paths, starting a base_path if it
        is supplied. 
        
        If the data element being fetched is a list, then it is returned
        as a list, unless select is an integer, in which case only the
        element at the 'select'ed position is returned. If select is the
        string 'random', then a random position in the list is returned.
        
        Note that if multiple 'random' fetch()es are performed, the ones after
        the first fetch() will select the same position as the first one (in
        order to maintain consistency of the fetch()ed data). If one really
        wants to have a fresh, random element selected, invoke the load() 
        method each time before fetch().
        '''
        data = self.fetch_all()
        
        if get_pref("share_usage"):
            usage_info = self.prep_usage_info(False)
            usage_info['field_paths'] = ",".join(field_paths)
            usage_info['base_path']   = base_path
            usage_info['select']      = str(select)
            usage_info['got_data']    = data and len(data) > 0
            register_fetch(usage_info)
        
        if len(field_paths) is 0:
            collected = data
        else:
            collected = []
            
            if base_path is None:  # see if it can be extracted as a common prefix of the field_paths
                base_path, field_paths = U.extract_base_path(field_paths)
            # note: if base_path is '', then we specifically assume it's not wanted to be inferred
            if base_path is '': base_path = None
                
            if base_path:      
                base_path = self.__patch_jsonpath_path(base_path, data)
                data = parse(base_path).find(data)
            
            if not isinstance(data, list):
                data = [data]   # so the for loop below works
            
            parsed_paths = None
            field_names = None
    
            for match in data:  # each record of the list is handled as a match
                if parsed_paths is None:
                    parsed_paths = []
                    field_names = []
                    for field_path in field_paths:
                        field_path = self.__patch_jsonpath_path(field_path, match)
                        parsed_paths.append(parse(field_path))

                        pieces = field_path.split(".")
                        field_name = pieces.pop()    # TODO: could end up with [...] at end of field names
                        while field_name in field_names and len(pieces) > 0:
                            field_name = pieces.pop() + "-" + field_name
                        field_names.append(field_name)
                
                d = {}
                for fp, fn in zip(parsed_paths, field_names):
                    fv = fp.find(match)   # field value extracted from this match
                    if not fv or fv == []:
                        raise SinbadError("No data found for field: {}".format(fn))
                    elif len(fv) == 1:
                        fv_result = fv[0].value
                    else:
                        fv_result = [v.value for v in fv]
                        
                    if len(parsed_paths) == 1: d = fv_result
                    else: d[fn] = fv_result
                        
                collected.append(d)
            
            collected = U.collapse_lists(collected)
            
            if len(collected) == 1:
                only_one = collected[0]
                if len(field_paths) == 1 and field_names[0] in only_one:
                    collected = only_one[field_names[0]]
                else:
                    collected = only_one
            
        if select and isinstance(select, str) and select.lower() == 'random' and isinstance(collected, list):
            if not self.__random_index:
                self.__random_index = random.randrange(len(collected))
            select = self.__random_index
        
        if type(select) == int and isinstance(collected, list):
            return collected[select]
        else:
            return collected
        
        
    # positional fetch()es
    
    def fetch_random(self, *field_paths, base_path = None):
        return self.__post_process(self.fetch(*field_paths, base_path = base_path, select = "random"), *field_paths)
    
    def fetch_first(self, *field_paths, base_path = None):
        return self.fetch_ith(0, *field_paths, base_path = base_path)

    def fetch_second(self, *field_paths, base_path = None):
        return self.fetch_ith(1, *field_paths, base_path = base_path)

    def fetch_third(self, *field_paths, base_path = None):
        return self.fetch_ith(2, *field_paths, base_path = base_path)

    def fetch_ith(self, i, *field_paths, base_path = None):
        return self.__post_process(self.fetch(*field_paths, base_path = base_path, select = i), *field_paths)
    
    
    # fetch()es with conversion + position
    
    def fetch_float(self, field_path, select = None):
        stuff = self.fetch(field_path, select = select)
        if isinstance(stuff, list):
            return [float(v) for v in stuff]
        else:
            return float(stuff)

    def fetch_first_float(self, field_path):
        return self.fetch_float(field_path, select=0)
    
    def fetch_ith_float(self, i, field_path):
        return self.fetch_float(field_path, select=i)

    def fetch_random_float(self, field_path):
        return self.fetch_float(field_path, select="random")

    
    def fetch_int(self, field_path, select = None):
        stuff = self.fetch(field_path, select = select)
        if isinstance(stuff, list):
            return [int(v) for v in stuff]
        else:
            return int(stuff)

    def fetch_first_int(self, field_path):
        return self.fetch_int(field_path, select=0)
    
    def fetch_ith_int(self, i, field_path):
        return self.fetch_int(field_path, select=i)

    def fetch_random_int(self, field_path):
        return self.fetch_int(field_path, select="random")
    

    # sampling -------------------------------------------------------------

    def sample_data(self, obj, max_elts, random_seed = None):
        '''
        Randomly samples up to 'max_elts' number of elements from any lists
        that are in the given JSON-like data object. Note that the object is
        recursively traversed, so all lists and sublists are sampled as well.
        '''
        if random_seed:
            random.seed(random_seed)
        
        if isinstance(obj, list):
            if len(obj) > max_elts:  # need to sample down
                obj = [ obj[i] for i in sorted(random.sample(range(len(obj)), max_elts)) ]
            
            obj = [self.sample_data(v, max_elts) for v in obj]  # sample inner data
        elif isinstance(obj, dict):
            obj = { k : self.sample_data(v, max_elts) for k, v in obj.items() }
                
        return obj


    def description(self):
        if not self.has_data():
            raise ValueError("no data available - make sure you called load()")
        
        return D.describe(self.data_obj)
    
    
    def print_description(self, verbose=False):
        print("-----")
        
        url_path = self.get_full_path_url() if self.__ready_to_load() else self.path
        
        if self.name and self.name is not self.path:
            print("Data Source: {}\nURL: {}".format(self.name, url_path))
        else:
            print("Data Source: {}".format(url_path))
        if "file-entry" in self.option_settings:
            print("   (Zip file entry: {})".format(self.option_settings.get("file-entry")))
        if verbose and self.format_type:
            print("Format: {}".format(self.format_type))

        if self.info_text or self.info_url: print()
        if self.info_text: print(self.info_text)  
        if self.info_url: print("(See {} for more information about this data.)".format(self.info_url))
            
        param_keys = [k for k in self.params]
        if len(param_keys) > 0:
            param_keys.sort()
            print("\nThe following (connection) parameters may/must be set on this data source:")
            
            for pkey in param_keys:
                prm = self.params[pkey]
                p_val = self.param_values.get(pkey)
                desc = prm.description
                req =  prm.required
                val_str = "not set" if not p_val else "currently set to: '{}'".format(p_val)
                desc_str = " {}".format(desc) if desc else ""
                req_str = " [*required]" if req else ""
                print("   - {} ({}){}{}".format(pkey, val_str, desc_str, req_str))
            
        opt_keys = self.data_factory.get_options()
        if verbose and len(opt_keys) > 0:
            opt_keys.sort()
            print("\nThe following options are available for this data source format:")
            
            for okey in opt_keys:
                oval = self.data_factory.get_option(okey)
                val_str = " (currently set to: '{}')".format(oval) if oval else ""
                print("   - {}{}".format(okey, val_str))
            
        if self.has_data():
            print("\nThe following data is available:")        
            print(self.description())
        else:
            print("\n*** Data not loaded *** ... use .load()\n")    
    


    
    # informational methods ------------------------------------------------

    def has_fields(self, *field_names, base_path = None):
        '''
        Determines if all the given field names/paths are available in the
        data
        '''
        if not self.has_data():
            raise SinbadError("no data available - make sure you called load()")

        for f in field_names:
            try:
                data = self.fetch(f, base_path = base_path, select = 0)
                if not data: return False
            except SinbadError:
                return False
        
        return True

#         top_level_fields = [f for f in field_names if "/" not in f]
#         field_names = [f for f in field_names if f not in top_level_fields]
#         # field_names keeps the left-overs remaining to be checked...
#         
#         while top_level_fields or field_names:
#             available = self.field_list(base_path = base_path)
#             if not all([f in available for f in top_level_fields]):
#                 return False
#             
#             top_level_fields = [f for f in field_names if "/" not in f]
#             field_names = [f for f in field_names if f not in top_level_fields]
#             
#         return True


    def field_list(self, base_path = None):
        '''
        Returns a list of the available top-level fields that can be fetched.
        If base_path is provided, returns a list of the available fields at 
        the element in the data identified by base_path. 
        '''
        if not self.has_data():
            raise SinbadError("no data available - make sure you called load()")

        if not base_path:
            data = self.fetch()
        else:
            data = self.fetch(base_path)
            
        while isinstance(data, list) and len(data) > 0:
            data = data[0]
            
        if isinstance(data, dict):
            return [k for k in data]
        else:
            return []
        
        
    def data_length(self, base_path = None):
        '''
        Produces the number of elements available in the top-level data 
        (or at the element identified by base_path) if the data element is
        a list.
        '''
        if not self.has_data():
            raise SinbadError("no data available - make sure you called load()")

        if not base_path:
            data = self.fetch()
        else:
            data = self.fetch(base_path)

        if isinstance(data, list):
            return len(data)
        else:
            return 0



    # various options management methods ------------------------------------
    
    def set_cache_timeout(self, value):
        '''Set the cache delay to the given value in seconds '''
        if value > 0:
            value = value * 1000   # convert to milliseconds
        self.cacher = self.cacher.update_timeout(value)
        return self
    
    def set_cache_directory(self, path):
        '''Set the cache directory for this Data_Source (only)'''
        self.cacher = self.cacher.updateDirectory(path)
        return self

    def cache_directory(self):
        '''Return the main cache directory for this Data_Source'''
        return self.cacher.cache_directory
    
    def set_option(self, name, value):
        if name.lower() == "file-entry":
            self.option_settings['file-entry'] = value
        else:
            self.data_factory.set_option(name, value)
        return self
    
    def set_options(self, opts):
        for k in opts:
            self.set_option(k, opts[k])
        return self

    def set_param(self, name, value):
        if name and value:
            self.param_values[name] = value
        return self
    
    def set_params(self, prms):
        for k in prms:
            self.set_param(k, prms[k])
        return self

    def __add_param__(self, param):   # a 'protected' method - used by load_spec()
        if param:
            self.params[param.key] = param
        return self
    
    
    
    # export ------------------------------------------------------------
    def export(self, fp = None):
        '''
        Exports a JSON-like object describing this Data_Source (in the format
        used for specification files).
        
        If a file-like object or file path is provided, the specification
        is saved to the file.
        '''
        spec = OrderedDict()
        if self.path: spec["path"] = self.path
        if self.name: spec["name"] = self.name
        if self.format_type: spec["format"] = self.format_type
        if self.info_url: spec["infourl"] = self.info_url
        if self.info_text: spec["description"] = self.info_text
        
        cache_spec = OrderedDict()
        cache_spec["timeout"] = self.cacher.cache_expiration / 1000
        if self.cacher.cache_directory is not C.__DEFAULT_CACHE_DIR__:
            cache_spec["directory"] = self.cacher.cache_directory
        spec["cache"] = cache_spec
        
        opt_list = []
        if self.option_settings:
            for k, v in self.option_settings.items():
                opt_list.append({ "name" : k, "value" : v})
        if self.data_factory:
            for opt in self.data_factory.get_options():
                v = self.data_factory.get_option(opt)
                if v:
                    opt_list.append({ "name" : opt, "value" : v})
        spec["options"] = opt_list
        
        param_list = []
        for k, p in self.params.items():
            param_list.append( p.export(self.param_values.get(k, None)) )
        for k, v in self.param_values.items():
            if k not in self.params:
                prm = Param(k, "query")
                param_list.append( prm.export(v) )
        spec["params"] = param_list
        
        if fp:
            if hasattr(fp, 'write'):  # file-like object?
                json.dump(spec, fp, indent=2)
            else:
                with open(fp, 'w') as fpp:
                    json.dump(spec, fpp, indent=2)
        
        return spec


    # usage reporting----------------------------------------------------
    def prep_usage_info(self, include_options = True):
        '''Prepares a dictionary of usage information to be sent to the server'''
        usage_info = {}
        
        usage_info['full_url'] = self.get_full_path_url()
        usage_info['format_type'] = self.format_type
        usage_info['file_entry'] = self.option_settings.get('file-entry')
        
        if include_options:
            usage_info['data_options'] = json.dumps( { k : self.data_factory.get_option(k) 
                                                      for k in self.data_factory.get_options() })
        
        return usage_info



    # other stuff -------------------------------------------------------
    def __patch_jsonpath_path(self, orig_pth, data):
        '''
        Replace '/'s with '.'s  and add '[*]'s as required by jsonpath_rw
        '''
        pth = orig_pth.replace("/", ".")
        splits = pth.split(".")
        if not splits:
            return pth
        
        fixed_pieces = []
        cur_data = data
        
        #print("data: {}".format(data) [:200])
        
        if isinstance(data, list):
            fixed_pieces.append("$[*]")
            cur_data = parse("$[*]").find(cur_data)[0].value
            
        for piece in splits:
            #print("piece: {}  fixed_pieces: {}  data: {}".format(piece, fixed_pieces, cur_data) [:300])
            found = parse(piece).find(cur_data)
            if not found or len(found) < 1:
                raise SinbadError("Could not process field path: {}".format(orig_pth))
            cur_data = found[0].value
                            
            if isinstance(cur_data, list) and len(cur_data) > 1 and not piece.endswith("]"):
                fixed_pieces.append(piece + "[*]")
                cur_data = cur_data[0]
            else:
                fixed_pieces.append(piece)
        
        #print("done: {}".format(fixed_pieces))
        return ".".join(fixed_pieces)       


    def __post_process(self, result, *field_paths):
        if isinstance(result, dict) and len(result.keys()) == 1:  # unwrap singleton dictionary fields
            for first_key in result: break
            return result[first_key]           
        else:
            return result



### ----------------------------------------------------------------------
# just an alias in case people want to use camelCase 
DataSource = Data_Source






### ----------------------------------------------------------------------
PATH_PARAM = "path"
QUERY_PARAM = "query"

class Param:
    '''
    Maintains information about parameters for a data source. There are
    two types: path and query. Query parameters are incorporated into the
    URL when the data is retrieved. Path parameters are used to substitute
    for  "... @{NAME} ..." placeholders in the URL that is built to 
    retrieve the data.
    '''

    def __init__(self, key, type, description = None, required = False):
        self.key = key
        self.type = type
        self.description = description
        self.required = required

    def export(self, value = None):
        '''Produce a JSON-like encoding of this Param object'''
        
        m = { "key" : self.key, "type" : self.type, "required" : self.required }
        if self.description:
            m["description"] = self.description
        if value:
            m["value"] = value
        return m
    



### ----------------------------------------------------------------------
def load_spec(fp):
    '''
    Loads a specification file from the given file-like object and
    instantiates and prepares a Data_Source object based on that.
    '''
    spec = json.load(fp)
    if not spec.get("path"):
        raise SinbadError("Invalid specification file")
    
    path = spec["path"]
    if spec["format"]:
        ds = Data_Source.connect(path, format = spec["format"])
    else:
        ds = Data_Source.connect(path)
        
    ds.name = spec.get("name")
    ds.info_text = spec.get("description")
    ds.info_url = spec.get("infourl")
    
    if "cache" in spec:
        c = spec["cache"]
        if "timeout" in c:
            ds.set_cache_timeout(c["timeout"])
        if "directory" in c:
            ds.set_cache_directory(c["directory"])

    if "params" in spec:
        param_list = spec["params"]
        for d in param_list:
            p = Param(d["key"], d["type"], d.get("description"), d.get("required", False))
            ds.__add_param__(p)
            if d.get("value"):
                ds.set_param(d["key"], d["value"])
    
    if "options" in spec:
        for opt in spec["options"]:
            ds.set_option(opt["name"], opt["value"])
    
    return ds
