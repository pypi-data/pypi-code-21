# -*- coding: iso-8859-1 -*-
from __future__ import (unicode_literals, print_function)
'''
Created on 6 juin 2016

@author: Jarrige_Pi

  160608 - added 'exts' optional arg to SelectModel, defaults to bin+dat+pic
  160629 - allow import as pi of same sim or th as importer
  160706 - reviewed ganessa.sim/th import
  160919 - added select folder
  170228 - added UK dialogs
  170515 - fix parent.inidir not defined 

MMI for Piccolo tools
'''

from Tkinter import W, E, StringVar
from tkFileDialog import askopenfilename, asksaveasfilename, askdirectory
import ttk
import os.path as OP

from ganessa.util import codewinfile, ascii
from ganessa._getdll import _LookupDomainModule
wc = codewinfile

# select which ganessa to import according to caller import
_caller = _LookupDomainModule()
pic = _caller.module
if pic is not None:
    pic.useExceptions()

class DialogTexts(dict):
    '''Class for handling locale dialog strings'''
    _alldlgtxt = {'file': ('Fichier', 'File'),
                  'folder': ('Dossier', 'Folder'),
                  'infile': ('Fichier d\'entrée', 'Input file'),
                  'outfile': ('Fichier de sortie', 'Output file'),
                  'model_file': ('Fichier modèle', 'Model file'),
                  'selfile:':('Fichier choisi :', 'Selected file:'),
                  'selfold:': ('Dossier choisi :', 'Selected folder:'),
                  'selfilfold:': ('Dossier/fichier choisi :', 'Selected folder/file'),
                  'def_file': ('Fichier par défaut', 'Default file'),
                  'spec_file': ('Fichier spécifique', 'Specific file'),
                  'sel_other_file':('Choisir un autre fichier', 'Select another file'),
                  'sel_other_fold': ('Choisir un autre dossier', 'Select another folder'),
                  'sel_other_fifold': ('Choisir un autre dossier/fichier',
                                       'Select another folder/file'),
                  'sel_file_proc': ('Choisir le fichier à traiter', 
                                    'Select the file to process'),
                  'sel_fifold': ('Choisir le dossier/fichier', 'Select a folder/file'),
                  'sel_fold': ('Choisir le dossier', 'Select a folder'),
                  'infile:': ('Fichier d\'entrée :', 'Input file:'),
                  'reading_file': ('Lecture du fichier en cours...', 'Reading file...'),
                  'error:': ('Erreur : ', 'Error: '),
                  'fnf_or_incompat': ('Fichier non trouvé ou incompatible',
                                     'File not found or incompatible file'),
                  'fil_not_load': ('Fichier non chargé', 'File not loaded'),
                  'pipecount:': ('Nombre de tronçons : ', 'Pipe count: '),
                  'nodecount:': ('Nombre de noeuds : ', 'Node count: '),
                  'exestat': ('Résultat de l\'exécution', 'Excution status')
                 }
    
    def __init__(self, lang):
        '''Sets the string table for the selected language'''
        lgidx = 0 if (lang.upper() == 'FR') else 1
        dlgtxt = {k:v[lgidx] for k, v in DialogTexts._alldlgtxt.items()}
        dict.__init__(self, dlgtxt)

dlg = DialogTexts('FR')

def setlanguage(lang= 'FR'):
    global dlg
    dlg = DialogTexts(lang)
    print(OP.basename(__file__),'language set to:', lang)

def updatefrom(item, inidir):
    if not inidir:
        inidir = getattr(item, 'inidir',  '')
    if not inidir:
        try:
            inidir = OP.dirname(item.getmodelname())
        except AttributeError:
            pass
    return inidir


class SelectModel(ttk.LabelFrame):
    '''Classe pour la selection et le chargement d'un modele'''
    
    def __init__(self, parent, nfic, exts= None, usedef= True):
        ttk.LabelFrame.__init__(self, parent)
        self.configure(text= dlg['model_file'], height= 95, padding= 6)
        self.parent = parent
        self.usedef = usedef
        self.v_ficmodel = StringVar()
        self.v_ficmodelsav = StringVar()
        if exts is None:
            self.exts = ('bin', 'dat', 'pic')
        elif isinstance(exts, tuple):
            self.exts = [ext.strip('.').lower() for ext in exts]
        else:
            self.exts = (exts.strip('.').lower(), )
        # fr_bin.grid_propagate(0)
        self.s_ficmodel = StringVar()
        if nfic:
            self.v_ficmodelsav.set(nfic)
            self.s_ficmodel.set('usr')
        else:
            self.s_ficmodel.set('def')
        self.extra_model_info = [None]

        # creates lb_info before call to _model_choice
        self.lb_choice = ttk.Label(self, text= dlg['selfile:'])
        self.val_choice = ttk.Label(self, textvariable= self.v_ficmodel, style='PS.TLabel')
        self.lb_info = ttk.Label(self, text= ' ', style='PS.TLabel')
        self._model_choice(load= False)
        self.rb_1= ttk.Radiobutton(self, text= dlg['def_file'], 
                    variable= self.s_ficmodel, 
                    value= 'def', command= self._model_choice)
        self.rb_2= ttk.Radiobutton(self, text= dlg['spec_file'], 
                    variable= self.s_ficmodel, 
                    value= 'usr', command= self._model_choice)
        self.bt = ttk.Button(self, text= dlg['sel_other_file'])
        
        self.rb_1.grid(row= 0, column= 0, sticky= W)
        self.rb_2.grid(row= 1, column= 0, sticky= W)
        self.bt.grid(row= 1, column= 1, sticky= W)
        self.lb_choice.grid(row= 2, column= 0, sticky= W)
        self.val_choice.grid(row= 2, column= 1, sticky= W+E)
        self.lb_info.grid(row= 3, column= 1, sticky= W)
        self.bt.configure(command= self._sel_fich_model)

        # fonction permettant de propager la recuperation du nom du modele
        def _getmodname():
            return self.v_ficmodel.get()
        parent.getmodelname = _getmodname
        # fonction à appeler par le parent en fin d'init
        def _loadmodel():
            self._model_choice(load= True)
        try:
            parent.finalise.append(_loadmodel)
        except AttributeError:
            parent.finalise = [_loadmodel]

    def _model_choice(self, load= True):
        parent = self.parent
        parent._clear_exe(all= True)
        nom = self.v_ficmodelsav.get()
        etat = self.s_ficmodel.get()
        if nom and etat == 'usr':
            parent.inidir = OP.dirname(nom)
        elif self.usedef:
            self.s_ficmodel.set('def')
            nom = pic._fresult if pic else 'UnknownDefaultFile.bin'
            parent.inidir = ''
        self.v_ficmodel.set(nom)
        print(ascii(dlg['infile:']), wc(nom))
        # updates the model info from the function list
        self.extra_model_info[0] = self.loadmodel if load else self._noloadmodel
        self.lb_info.configure(text= '\n'.join([f() for f in self.extra_model_info]))
        parent._bt_exe_state()

    def _sel_fich_model(self):
        self.parent._clear_exe(all=True)
        ft = [(dlg['file'] + ' ' + ext, '*.' + ext) for ext in self.exts]
        fich = askopenfilename(title= dlg['sel_file_proc'],
                               initialdir= getattr(self.parent, 'inidir',  ''),
                               filetypes= ft)
        if fich:
            self.v_ficmodelsav.set(fich)
            self.s_ficmodel.set('usr')
            self._model_choice()
    
    def getfilename(self):
        '''Returns the model filename'''
        return self.v_ficmodel.get()
    
    def loadmodel(self):
        '''Loads the model and returns size inf as a text string'''
        parent = self.parent
        nom = self.v_ficmodel.get()
        if OP.exists(nom) and pic is not None:
            parent.v1.set(dlg['reading_file'])
            parent.update()
            try:
                if OP.splitext(nom)[1].lower() == '.bin':
                    pic.loadbin(nom) 
                else:
                    pic.reset()
                    pic.cmdfile(nom)
            except pic.GanessaError as err:
                errtxt = '\n' + dlg['error:'] + str(err)
            else:
                errtxt = ''
            txt = dlg['pipecount:'] + str(pic.nbobjects(pic.LINK)) + ' - ' +\
                  dlg['nodecount:'] + str(pic.nbobjects(pic.NODE)) + errtxt
        else:
            txt = '***' + dlg['fnf_or_incompat'] + '***'
        parent.v1.set(txt)
        return txt
    
    def _noloadmodel(self):
        '''alternate version of loadmodel to be used before loading'''
        txt = dlg['fil_not_load']
        self.parent.v1.set(txt)
        return txt
    
    def add_extra_model_info(self, textfun):
        '''Register a function that returns a text string to be displayed as addl model info'''
        self.extra_model_info.append(textfun)


class SelectFile(ttk.LabelFrame) :
    # File frame
    # rev 160820: exts=None for a selection without extension
    # rev 170618: title= allow title redefinition
    def __init__(self, parent, nfic, exts, mode, title= '', post= None):
        ttk.LabelFrame.__init__(self, parent)
        if title:
            self.naturefic = title
        else:
            self.naturefic = dlg['outfile'] if mode == 'w' else dlg['infile']
        self.configure(text= self.naturefic, height= 80, padding= 6)
        self.parent = parent
        self.v_fich = StringVar()
        self.v_post = StringVar()
        self.post = post
        self.ask = askopenfilename if mode == 'r' else asksaveasfilename
        if exts is None or not exts:
            self.exts = None
        elif isinstance(exts, tuple):
            self.exts = [ext.strip('.').lower() for ext in exts]
        else:
            self.exts = (exts.strip('.').lower(), )
        # fr_out.grid_propagate(0)
        if nfic:
            self.v_fich.set(nfic)
        ttk.Label(self, text= dlg['selfilfold:']).grid(row= 2, column = 0, sticky= W)
        ttk.Button(self, text= dlg['sel_other_fifold'], 
                         command= self._sel_fich).grid(row= 1, column= 1, columnspan= 3, sticky= W)
        ttk.Label(self, textvariable= self.v_fich, style='PS.TLabel').grid(row= 2, column= 1, columnspan= 6, sticky= W+E)
        if post is not None:
            ttk.Label(self, textvariable= self.v_post, style='PS.TLabel').grid(row= 3, column= 1, sticky= W)
            self._post()
    
    # Choix du dossier et racine de fichier de sortie
    def _sel_fich(self):
        try:
            self.parent._clear_exe()
        except AttributeError:
            pass
        nom = self.v_fich.get()
        inidir = OP.dirname(nom)
        inidir = updatefrom(self.parent, inidir)
        inifil = OP.splitext(OP.basename(nom))[0]
        
        if self.exts is None:
            kwft = dict()
        else:
            kwft = { 'filetypes': [(dlg['file'] + ' ' + ext, '*.' + ext) for ext in self.exts]}
        fich = self.ask(title= dlg['sel_fifold'] + ' ' + self.naturefic,
                        initialdir= inidir, initialfile= inifil, **kwft )
        if fich:
            if not OP.splitext(fich)[1] and self.exts is not None:
                fich += '.' + self.exts[0]
            self.v_fich.set(fich)
            self._post()
    
    def getfilename(self):
        '''Returns the model filename'''
        return self.v_fich.get()

    def _post(self):
        if self.post is not None:
            nom = self.v_fich.get()
            txt = self.post(nom)
            self.v_post.set(txt)

class SelectFolder(ttk.LabelFrame) :
    # folder selector frame - 160919
    def __init__(self, parent, nfold, title= ''):
        ttk.LabelFrame.__init__(self, parent)
        self.naturefold = title if title else dlg['folder'] + ' '
        self.configure(text= self.naturefold, height= 80, padding= 6)
        self.parent = parent
        self.v_fold = StringVar()
        if nfold:
            self.v_fold.set(nfold)
        ttk.Label(self, text= dlg['selfold:']).grid(row= 2, column = 0, sticky= W)
        ttk.Button(self, text= dlg['sel_other_fold'], 
                         command= self._sel_fold).grid(row= 1, column= 1, columnspan= 3, sticky= W)
        ttk.Label(self, textvariable= self.v_fold, style='PS.TLabel').grid(row= 2, column= 1, columnspan= 6, sticky= W+E)
    
    # Choix du dossier et racine de fichier de sortie
    def _sel_fold(self):
        self.parent._clear_exe()
        inidir = self.v_fold.get()
        inidir = updatefrom(self.parent, inidir)
        fold = askdirectory(title= dlg['sel_fold'],
                            initialdir= inidir, mustexist= True)
        if fold:
            self.v_fold.set(fold)
    
    def getfoldername(self):
        '''Returns the folder'''
        return self.v_fold.get()
    def getfilename(self):
        '''Returns the folder'''
        return self.v_fold.get()


class ExecStatus(ttk.LabelFrame):
    def __init__(self, parent):
        ttk.LabelFrame.__init__(self, parent)
        self.configure(text= dlg['exestat'], height= 80, padding= 6)
        ttk.Label(self, textvariable= parent.v1).grid(row= 0, column= 0, sticky= W)
        ttk.Label(self, textvariable= parent.v2).grid(row= 1, column= 0, sticky= W)
        ttk.Label(self, textvariable= parent.v3).grid(row= 2, column= 0, sticky= W)
