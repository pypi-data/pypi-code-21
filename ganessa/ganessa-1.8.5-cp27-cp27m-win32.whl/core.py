# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function, absolute_import)
#****g* ganessa.sim&th/About
# PURPOSE
#   The module ganessa.sim (resp. ganessa.th) provides a Python interface 
#   to Picwin32.dll and Ganessa_SIM.dll (resp. Ganessa_TH.dll) kernels. 
#   It will be extended as needed.
#
#   The module name ganessa.sim&th is used for items availble both 
#   in .sim and .th environments
# INSTALLATION
#   pip install ganessa
#
#   numpy must be installed in version >= 1.7; pip will handle it.
#
#   The package expects the simulation kernel .dll to be found either 
#   in the %PATH environment variable (either name)
#   or in one of the sub folders of Program Files folder (x86 under Windows 7):
#   * "Safege/Ganessa_<lang>/Ganessa_xx" (xx = SIM or TH) or
#   * "Gfi Progiciels/Piccolo6_<lang>/Picwin32.dll" or 
#   * "Gfi Progiciels/Picalor6_<lang>/Picwin32.dll" or 
#   * "Adelior/Piccolo5_<lang>/Picwin32.dll"
#   in either drive D: or C:
# USE
#   Syntax:
#   * import ganessa.sim as pic   (or ganessa.th for Picalor)
#   * pic.cmdfile('my file.dat')
#   Or:
#   * from ganessa.sim import *
#   * cmdfile('my file.dat')
#
#   the import will perform the following initialisation tasks:
#   * locate Ganessa_xx.dll or Picwin32.dll kernel
#   * initialise it
#   * locate result.bin in a working subdirectory
#   * bind termination to ctrl+Z
# CONTENT
#   The package provides the following content:
#   * constants for calling API functions
#   * iterators for browsing objects and selections
#   * functions for loading .bin file
#   * functions for executing command files / command strings / running simulations
#   * functions for catching simulation errors and retrieving unstable items
#   * functions for retrieving individual objects attributes
#   * functions for retrieving table entries and object count
#   * functions for retrieving result or measurements time series
#   * functions for retrieving min / max / avg values for all objects
#
# REMARKS
#   * Most of the functions are getter. A few direct setter functions are provided
#     (setbranchattr, setdensity, defcalind, *SHL functions). The general purpose
#     addcmd(w), cmd, execute and cmdfile can be used for all other settings.
#   * Commands (passed to cmd, execute, cmdfile) should be built in the language 
#     (idiom) of the current version. getkeyword, modulekeyword, attrkeyword allow
#     to retrieve a given keyword in the current idiom; gencmd(w) allow to build a
#     command line in the current idiom.
#   * Any suggestion for extending / improving can be mailed to: piccolo@safege.fr
#
# HISTORY
#   The history of the package is:
#   * 1.0.3: plotmesx png takes care of measurement type
#   * 1.0.4: added demand getter for a demand code or for all
#   * 1.0.5: added Windows 7 paths 'program files (x86)';
#            added option to get TS by measurement step 'tsvalbymts';
#            added 'refdate' : retireval of REFDATE
#   * 1.0.6: correction to the grid adjustment in plotmes (util)
#   * 1.0.7: getMinMax can be called with a selection name
#   * 1.0.8: save function
#   * 1.0.9: SimulationError exception catching + save(identical to MMI);
#            requires numpy 1.8.1
#   * 1.1.0: same as 1.0.9 but requires only numpy 1.7.1
#   * 1.1.1: minor change to codewinfile=winstr
#   * 1.1.2: added 'execute' for multiple commands as strings (\n managed as a separator)
#   * 1.1.3: (141104) disable useoffset for Y axes in 'util.plotmes'
#   * 1.1.4: (141118) handling Picwin32.dll provided by GFI after 18-11-2014 (best 03-12-2014)
#   * 1.1.5: (141205) handling ts < ms in tsvalbymts
#   * 1.1.6: (150127) nodexyz added + bugfix in attrs documentation
#   * 1.1.7: (150309) minor grammatical changes
#   * 1.2.0: (150507) change in folder search order (ws7 priority) + language - OK with Picwin32 151203
#   * 1.2.1: (150527) Picalor enabled  as ganessa.th + density and SHL management;
#            (150603) added 'meanattr';
#            (150610) added 'addSHLtype'
#   * 1.2.2: (150709) bug fix calls select* from Selected
#   * 1.2.3: (150812) bug fix: return value of browseWQ; getall
#   * 1.2.4: (150910) constants added (WQ, Inverse Pb) + demandcodes
#   * 1.2.5: (150922) utils: tuning of plotmes subtitle fontsize for large titles
#                      + constants (MOD, NOD ...) + 'areas' function
#   * 1.2.6: (151128) added tsdemand and tsdemandlen, tsdevice and tsdevicelen;
#                     added tables (material, area etc.) access;
#                     utils: added list2file
#   * 1.3.0: (151202) added support for compatibility with Picwin32 12/2014, 12/2015 and Ganessa;
#            (151206) addl constants (BRA, DYN, RSV);
#            (151218) reviewed compatibility with Picwin32 (2015+ -> Piccolo6), (2014 -> Piccolo5)
#   * 1.3.1: (160108) header, footer and suffix optional args for utils.list2file;
#            (160113) added memory allocation error exception (inverse module)
#   * 1.3.2: (160118) added retrieval of problematic devices;
#            (160126) added 'H' tank attribute in util.plotmes(x)
#   * 1.3.3: (160226) added getindex, tankattrs, linkattr and linkattrs
#   * 1.3.4: (160301) added constants for inverse pb;
#            (160309) added inverse simulation summary;
#            (160318) added added nxxxxattr and nxxxxatrs function for getting attributes by index;
#            (160325) added file quote as needed in save function;
#            (160329) corrected doc (selectlen/select);
#            (160405) corrected doc, added linkXYZV;
#            (160408) utils: strloc, strf3loc
#   * 1.3.5: (160410) added init(folder)
#   * 1.3.6: (160511) added 'symmetric_node' (Ganessa_TH);
#            (160531) reviewed compatibility with dll versions since 2014.
#   * 1.3.7: (160622) added OpenFileMMI classes: SelectModel, SelectFile, ExecStatus;
#            (160706) added 'dist2link'; added 'util.dist_to_poly' as pure python backup;
#                     OpenFileMMI uses simulation interface from caller, or None;
#                     changed all classes to new style;
#                     added 'len' method to 'Selected' and 'Elements'; added 'Graph'
#   * 1.4.0: (160715) setup changed to build whl from source files;
#            (160719) minor bug fix in util.plotmes - reuse same fig in non interactive mode
#   * 1.4.1: (160820) OpenFileMMI SelectFile with null extension; load error handling
#   * 1.4.2: (160830) added AUTO and QUAL storestep constants; minor fix in gencmd;
#                     added include_depth optional attribute to 'linkxyzv';
#            (160915) added version_2016b in the Picwin32 lookup table;
#            (160919) added SelectFolder in OpenFileMMI;
#            (160922) added setlinkattr as a synonym of setbranchattr;
#            (160927) intermediate API for Piccolo6 2016 B (dec-2016)
#   * 1.5.0: (161010) added 'getkeyword';
#            (161019) minor change in util.plotmes: 160719 patch reviewed for better output;
#            (161124) added 'stat_quantiles', 'stat_duration', and 'Dynamic_Stats'
#   * 1.5.1  (161212) bug fix on ts* functions without result file;
#                     added 'retry' optional argument to full_solveH
#   * 1.5.2  (170105) added folder= option in util.list2file
#            (170110) build with numpy 1.11.0 - compatible with
#   * 1.7.0  (170119) build with BIND(C) instead of DEC$ATTRIBUTE C, REFERENCE;
#                     required with ganessa_SIM > 170117 (renamed API functions);
#            (170125) added fixed_interval to tsdevice, now return float values
#   * 1.7.1  (170221) minor changes in util.Inifile (default encoding utf-8);
#                     switch to unicode_literals in sim&th, util and prot;
#            (170223) added compiled util.dist, util.dist_p_seg, util.dist_to_poly
#   * 1.7.2  (170228) added OpenFileMMI.setlanguage function (FR/US or UK);
#            (170304) fix getMinMax/getallminmax break in 1.7.0
#   * 1.7.3  (170313) added WQ, MOD and LNK constants; added DICT.END;
#                     added modulekeyword and attrkeyword;
#            (170331) added shearstr; match Piccolo 2017 --> NO !
#   * 1.7.4  (170407) added silent option to init;
#            (170424) added default '@safege.com' domain to util.envoi_msg
#   * 1.7.5  (170426) improved util.plotmes(x) for horizon > 24h;
#            (170512) added module 'multithread';
#            (170515) fix parent.inidir error in OpenFileMMI; added solveH
#   * 1.7.6  (170613) added constants (STATIC, QUA.VISUSTEP) and util.group;
#                     minor bug fix in Selected, GetMinMax and Dynamic_Stats;
#            (170618) added title to OpenFileMMI.SelectFile and SelectFolder;
#                     added util.pageplot;
#            (170620) replaced litteral symbols with attrkeyword();
#            (170627) match Piccolo 2017 (apr 2017);
#   * 1.7.7  (170705) added cwfold;
#            (170707) optional arg for sim&th.close(arg) and prot.close(arg);
#                     added C1 in util.plotmes for chlorine plots;
#   * 1.7.8pr1 (170808) doc update; upload to pypi
#   * 1.7.8  (170817) replaced IniFile with json/xml version
#   * 1.7.9pr1 (170824) prepared for Piccolo 2017b
#              (170830) added getunitcoef
#   * 1.8.0  (170907) sim.py split into core, core_sim, core_th; changed/fixed path lookup 
#            (170918) added resfile, raw_getcmdw, raw_stat_duration, raw_stat_quantiles
#   * 1.8.1  (171004) added util.update_package
#   * 1.8.2  (171016) added util.str2uni (tries utf8 the cp1252 - reverse from unistr)
#            (171018) minor bug fix for util.update_package 
#            (171103) added sort.HeapSort class and Graph.dtree
#   * 1.8.3  (171109) added error msg when OpenFileMMI is imported before sim or th
#            (171110) fix _pyganutl import broken in 1.8.0 (util.dist, util.dist_to_poly)
#            (171114) added multithread.MultiProc class
#   * 1.8.4  (171120) bug fix / changed multithread.MultiProc.run return values as 3 lists
#   * 1.8.5  (171120) added util.plot_close to avoid Fatal Python error at exit
#            (171128) added linkbbox and util.gbool 
#****
#****g* ganessa.sim&th/Compatibility
# PURPOSE
#   The installation of pyganessa is compatible with several versions of Picwin32.dll
#  (regular Piccolo / Picalor). Missing functions in older versions should NOT be called.
# HISTORY
#   *  2014  -> 141203 Piccolo5 -- release 2014
#   * (2015a -> 151217 Piccolo6 & Picalor6 -- release 2015 (unstable)) - discarded
#   *  2015  -> 160121 Piccolo6 -- release 2015 sp1
#   *  2016  -> 160419 Piccolo6 & Picalor6 -- release 2016
#   *  2016a -> 160930 Piccolo6 release 2016b (incomplete; compatible with 1.4.2)
#   *  2016b -> 161216 Piccolo6 & Picalor6 -- release 2016b (1.5.0 - 1.5.2)
#   *  2017  -> 170627 Piccolo6 & Picalor6 -- release 2017  (1.7.7 - 1.7.8)
#   *  2017b -> 1709xx Piccolo6 & Picalor6 -- release 2017b (1.8.0 - )
# REMARK
#   pyganessa is compatible with matching or newer versions of Ganessa_SIM/Ganessa_TH.dll only;
#   except a compatibility break on 170117.
#****

import atexit
import numbers
from collections import Counter, OrderedDict

from ganessa.util import winstr, quotefilename, dist_to_poly
from ganessa import __version__ as _version
from ganessa._getdll import _LookupDomainModule
from ganessa.sort import HeapSort

# import the keywords back from the importer module
_caller = _LookupDomainModule().module
_fresult, _lang  = _caller._fresult, _caller._lang
_dll_api, _dll_name = _caller._dll_api, _caller._dll_name

_dll_version = 0
# functions not defined when older dll are used
_fn_undefined = []

#****g* ganessa.sim&th/Constants
# DESCRIPTION
#   Several categories of constants are available:
#   * constants defining a type of element: see BRANCH or LINK, NODE, RESERVOIR or TANK
#   * constants defining a command module: M.COM or M.ROOT, M.GEN, M.SIM etc.
#   * constants defining a command within a module: M.SIM.EXEC
#   * keywords
#
#****
#****g* ganessa.sim&th/Functions
# DESCRIPTION
#   Functions available to ganessa.sim and ganessa.th
#****
#****g* ganessa.sim&th/Iterators
# DESCRIPTION
#   Iterators available to ganessa.sim and ganessa.th
#****
#****g* ganessa.sim&th/Classes
# DESCRIPTION
#   Classes available to ganessa.sim and ganessa.th
#****
#****c* Constants/BRANCH, LINK, NODE, NOEUD, TANK, RESERVOIR, RSV
# DESCRIPTION
#   Those constants allow to select one of the three types of model elements:
#   * LINK or BRANCH: branches elements such as pipes, pumps, valves
#   * NODE or NOEUD
#   * TANK or RESERVOIR or or RSV
# REMARK
#   M.LNK, M.NOD and M.RSV are object constants for calling BRANCH, NODE and RESERVOIR modules
#****
LINK = BRANCH = ARC = 1
NODE = NOEUD = 2
TANK = RESERVOIR = RSV = 3

# Class for the dictionary tree for keywords by modules
#****c* Constants/M, NONE
# DESCRIPTION
#   The M class provide a dictionnary tree for modules. It provides a
#   hierarchical naming of the commands by modules, for building
#   language-independant commands using  gencmd, gencmdw, _gencmdw functions.
# SYNTAX
#   One of the following:
#   * M.MODULE_SYMBOLIC_NAME
#   * M.MODULE_SYMBOLIC_NAME.COMMAND__SYMBOLIC_NAME or
#   * M.MODULE_SYMBOLIC_NAME..NONE or M.NONE or M.VOID
# CONTENT
#   The available MODULE_SYMBOLIC_NAME are:
#
#   ROOT: modules names: BRA, NOD, RSV, DYN, MOD, SIM, QUA, MES, LAB, FIR, INV, OPT.
#   They can be used in three forms, as first argument for the functions above:
#   * M.ROOT.SIM or M.SIM.ROOT: equals the index of the module name
#   * M.SIM: can be used in gencmd and gencmdw only as first argument
#
#   GEN: general purpose commands:
#   * LOAD: load a binary file
#   * OPEN and CLOSE: open and close an output file
#   * QUIT: the quit command
#   * READ: read a command language or data file
#     |html <br>example: <i>gencmd(M.GEN, M.GEN.OPEN, DICT.EXPORT, 'filename.txt')</i>
#   * EXPORT, SAVE: export or save to a (previously opened) file
#   * IMPORT: import attributes for a type of element from a file
#   * FIND: command for retrieving a given period or instant
#   * MESSAGE: writes a message to the console
#   * DEFPARAM, DEFVAR: define a positional parameter (%1 ... %9) or variable
#   * UNIT: redefine units name and coef
#   * EOF: the end-of-file command
#   LNK: link commands and submodules, including link types (.PIPE .PUMP .NRV .PRV .PSV .FCV .TCV etc.)
#
#   NOD: node commands and submodules:
#   * CONS: demand acquisition submodule
#   * COEF, AREA: demand coefficient by demand type and area
#   * TOPO: topograpy submodule
#   RSV: reservoir command and submodules:
#   * CHAR: characteristics
#   * LEVEL: initial level acquisition submodule
#   MES: measurement commands:
#   * SMOOTH: allow to define the smoothing interval
#   SIM: simulation commands:
#   * FILE: define a result file name
#   * EXEC: runs the simulation
#   QUA: Water quality module commands
#
# REMARK
#   The above codes are not exhaustive. Please refer to the script.
#****
class _CST(object):
    def __init__(self, cst):
        self.ROOT = cst
        self.NONE = -1
class M(object):
    NONE = VOID = -1
    GEN = _CST(0)
    GEN.CLOSE = 13
    GEN.CMPT = GEN.COMPAT = 65
    GEN.DEFP = GEN.DEFPARAM = 51  # DefParam
    GEN.DEFV = GEN.DEFVAR = 66  # defvar
    GEN.ECHO = 16
    GEN.EOF = 3
    GEN.EXPT = GEN.EXPORT = 39  # Export
    GEN.FIND = 18  # Find (instant)
    GEN.IMPT = GEN.IMPORT = 48
    GEN.INIT = 6
    GEN.LOAD = 17  # Load file.bin
    GEN.MESG = GEN.MESSAGE = 45  # Message
    GEN.OPEN = 12
    GEN.PATH = 23  # Path
    GEN.QUIT = 2
    GEN.READ = 5
    GEN.SAVE = 4
    GEN.STOP = 69 # stop-on error
    GEN.UNIT = 22
    GEN.WORD = GEN.WORDING = 52  # Libelle

    COM = _CST(1)   # COMMAND root level
    ROOT = COM
    BRA = _CST(2)
    ARC = BRA
    LNK = BRA

    BRA.BEND = 28
    BRA.BOOST = 8
    BRA.CUST = 24           # Picalor
    BRA.DENSITY = 18
    BRA.DIAM = 27
    BRA.DIAPH = 4
    BRA.ENVP = 23           # Picalor
    BRA.GPV = BRA.PRBR = 14
    BRA.HLEQ = 9
    BRA.FCV = BRA.FCTV = 7
    BRA.HEAT = 16           # Picalor
    BRA.MANV = 6
    BRA.MAT = 15
    BRA.NRV = BRA.CHECKV = BRA.CV = 3
    BRA.PIPE = 1
    BRA.PRV = 12
    BRA.PSV = 13
    BRA.PUMP = 2
    BRA.SHLT = 32
    BRA.SING = BRA.SHL= 33
    BRA.SST = 19
    BRA.TCV = BRA.THRV = 20
    BRA.VISC = 17

    NOD = _CST(3)
    NOD.AREA = 14 # demand coef by area
    NOD.CONS = 2
    NOD.COEF = 3  # demand coef by code
    NOD.CSMP = 8 # pressure dependant demand
    NOD.INIT = 24
    NOD.P0 = 9
    NOD.P1 = 10
    NOD.TOPO = 1

    RSV = _CST(4)
    TNK = RSV
    RSV.CHAR = 1
    RSV.FEED = 3
    RSV.LEVEL = 2
    RSV.OUT = 4

    DYN = _CST(5)  # dynam
    DYN.CTRL = DYN.REGU = 5
    DYN.CTRL_ENT = 8
    DYN.DATA = 1
    DYN.DSTEP = 3
    DYN.NSTEP = 2


    MOD = _CST(7)  # Modification
    MOD.ADD = 4
    MOD.ALLOC = 15
    MOD.CLOSE = 8
    MOD.DEL = 1
    MOD.DIV = 3
    MOD.INSERT = 13
    MOD.MERGE = 10
    MOD.MULT = 2
    MOD.OPEN = 7
    MOD.PURGE = 17
    MOD.REPLACE = 6
    MOD.REVERSE = 12
    MOD.SPLIT = 11

    SIM = _CST(8)
    SIM.CANCEL = SIM.ANNULER = 13
    SIM.EXEC = 1
    SIM.FILE = 25
    SIM.IVER = SIM.IVERB = 8
    SIM.STOP_DYN = 52
    SIM.STOP_ON = 51

    QUA = _CST(10)
    WQ = QUA
    QUA.AGE = 8
    QUA.ALTC = 40
    QUA.CLEAR = QUA.CLEAN = 5
    QUA.CONTINUE = QUA.CONT = QUA.STEP = 13
    QUA.CORROSION = QUA.CORR = 29
    QUA.DECAY = QUA.CONST = 6
    QUA.EXEC = 3
    QUA.FILE = QUA.NODEFILE = 18
    QUA.FILELINK = QUA.LINKFILE = 32
    QUA.INIT = 17
    QUA.INITRSV = 31
    QUA.IVERC = QUA.KOPT = 19
    QUA.ORDER = QUA.KINEXP = 39
    QUA.POLNOE = QUA.POL = 2
    QUA.POLRSV = 7
    QUA.REGIME = 4
    QUA.RESTIMINI = 43
    QUA.SAVESTATE = 42
    QUA.STORSTEPNODE = 12
    QUA.STORSTEPLINK = 33
    QUA.VISUSTART = 9
    QUA.VISUEND = 24
    QUA.VISUSTEP = 10

    MES = _CST(15)
    MES.SMOOTH = 6
    LAB = _CST(16)
    FIR = _CST(19)

    INV = _CST(20)
    INV.BFACT = 11
    INV.CONS = INV.DEMAND = 13
    INV.DTSMOOTH = 7
    INV.EXEC = 8
    INV.FTOL = 32
    INV.INIT = 29
    INV.KMAT = 18
    INV.SHL = 26
    INV.NITER = 2
    INV.PARAM = 6
    INV.RMAT = 12
    INV.TSTART = INV.TDEB = INV.TBEG = 4
    INV.TEND = INV.TFIN = 5
    INV.TYPE = INV.METHOD = 1
    INV.WEIGHT = 24
    INV.ZMES = 23
    INV.ZTNK = 28

    OPT = _CST(21)
    OPT.CIL = 1
    OPT.CIN = 2
    OPT.CIT = 3
    OPT.WQINIT = 7

# Build M.ROOT data from M.x.ROOT
for attr, val in M.__dict__.items():
    if attr[0:2] == '__' : continue
    if attr in  ('ROOT', 'COM', 'NONE', 'VOID') : continue
    setattr(M.ROOT, attr, val.ROOT)

# Class for the isolated keywords
#****c* Constants/DICT
# DESCRIPTION
#   The DICT class provide a dictionnary tree for keywords
# SYNTAX
#   DICT.SYMBOLIC_NAME
# CONTENT
#   * FULLPER: extended simulation (ENCHAINE in French)
#   * EXPORT
#   * INSTANT
#****
class DICT(object):
    AND = 11
    AUTO = 5
    AVERAGE = AVG = 76
    BINARY = 54
    BY = PAR = 114
    COMMA = VIRGULE = 122
    SEMICOMMA = POINTVIRGULE = CSV = 123
    DATA = 28
    DCF = TCB = 171
    DISTANCE = 155
    DYNAM = 75
    END = 9
    EXPORT  = 92
    FILE = 8
    FNODE = TONODE = 168
    FULLPER = 91  # Full-period = enchaine
    INSTANT = 97
    INODE = FROMNODE = 167
    INVERS = REVERSE = 106
    ON = 32
    OFF = 33
    PATH = PARCOURS = 157
    STATIC = PERMANENT = 74
    TEXT = 65
    TO = 10
    TREE = 90

class SIMERR(object):
    SIMERR = 1024
    ISOL = 2
    SLOW_CV = 4
    UNSTABLE = 6
    FCTAPP = 8
    DIVERGE = 10
    STRUCT = 12
    MEMALLOC = 16

#****k* Iterators/Elements
# SYNTAX
#   for id in Elements(typelt):
# ARGUMENT
#   int typelt: type element constants LINK, NODE, TANK
# RESULT
#   string id: id of each element of the given type in turn
#****
class Elements(object):
    def __init__(self, typelt):
        if isinstance(typelt, numbers.Number):
            self.type = typelt
            self.nbmax = _dll_api.nbobjects(self.type)
        self.index = 1
    def __iter__(self):
        return self
    def next(self):
        if self.index > self.nbmax:
            raise StopIteration
        (elem, ls) = _dll_api.getid(self.type, self.index)
        self.index += 1
        return elem[0:ls]
    def len(self):
        return self.nbmax
#****k* Iterators/Branches, Links
# SYNTAX
#   * for id in Branches():
#   * for id in Links():
# RESULT
#   string id: returns each branch id in turn
# REMARK
#   Branches and Links are synonyms
#****
#****k* Iterators/Nodes
# SYNTAX
#   for id in Nodes():
# RESULT
#   Returns each node id in turn
#****
#****k* Iterators/Tanks, Reservoirs
# SYNTAX
#   * for id in Tanks():
#   * for id in Reservoirs():
# RESULT
#   string id: returns each reservoir id in turn
#****
# Iterators for browsing model elements

class Nodes(Elements):
    def __init__(self):
        Elements.__init__(self, NODE)

class Branches(Elements):
    def __init__(self):
        Elements.__init__(self, BRANCH)

class Links(Elements):
    def __init__(self):
        Elements.__init__(self, LINK)

class Reservoirs(Elements):
    def __init__(self):
        Elements.__init__(self, RESERVOIR)

class Tanks(Elements):
    def __init__(self):
        Elements.__init__(self, TANK)

def _ret_errstat(*args):
    return -1

#****f* Functions/setbatchmode
# SYNTAX
#   oldmode = setbatchmode(mode)
# ARGUMENT
#   int mode: batch mode to activate
# RESULT
#   int oldmode: batch mode that was in effect
# REMARK
#   Defaults to 1 (True)
#****
try:
    setbatchmode = _dll_api.batchmode
except AttributeError:
    setbatchmode = _dll_api.setbatchmode


#****f* Functions/init
# SYNTAX
#   init([folder])
# ARGUMENT
#   str folder: optional folder name where journal and work files will be created
# DESCRIPTION
#   Initialises the ganessa simulation/command language engine.
# REMARKS
#   - Starting with version 1.3.5, a session should be started by calling init() or init(folder).
#     however for compatibility with previous releases where init was called at import time,
#     init is automatically called at 1st call of cmd, cmdfile, execute, load, loadbin
#   - A session should be terminated by calling quit() or typing <Ctrl>+Z
# HISTORY
#   * introduced in 1.3.5
#****
def init(folder= None, silent= False):
    global _dll_version
    if _dll_version:
        return
        # return _dll_version
    # Initialisation of ganessa
    if folder is None or not folder:
        _dll_version = _dll_api.inipic()
    else:
        try:
            _dll_version = _dll_api.inipicfld(folder)
        except AttributeError:
            _dll_version = _dll_api.inipic()
            _fn_undefined.append('init(folder)')

    # 2 places to check : here and pyGanSim.f90 (inipic)
    if _dll_version < 0:
        jj = -_dll_version
        aa, mm, jj = jj/10000, (jj/100) % 100, jj%100
        comment = 'DLL {:s} too old: {:02d}-{:02d}-{:02d}\n'.format(_dll_name, jj, mm, aa)
        print(comment)
        raise ImportError(comment)
    else:
        print('\t* pyganessa:', _version, '-', _dll_name + ':', _dll_version, _lang,'*')
    _precmode = setbatchmode(1)
    if silent:
        _dll_api.gencmd(M.SIM.ROOT, M.SIM.IVER, M.NONE, '-9')
        _istat = _dll_api.commit(0)

#****f* Functions/dll_version
# SYNTAX
#   yymmdd = dll_version()
# RESULT
#   int yymmdd: dll version
# HISTORY
#   introduced in 1.8.0 (170907)
#****
def dll_version():
    '''Returns the version of the dll (after init)'''
    return _dll_version

#****f* Functions/quit, close
# SYNTAX
#   ret = quit([True])
# ARGUMENT
#   optional bool verbose: if set to True, a message is printed. 
#   Defaults to False.
# RESULT
#   text ret: text string telling that he module has been unloaded.
#   Terminates the ganessa session and unloads the module ganessa.sim&th
# REMARKS
#   - quit() is automatically called when quitting with <Ctrl>+Z
#   - close() is a synonym for quit()
#   - A session should be terminated by calling quit() or typing <Ctrl>+Z
#   - sys.exit() automatically trigers quit()
#****
def _close(*args):
    global _dll_api, _dll_version
    if _dll_version:
        try:
            text = 'Ganessa unloaded.'
            _dll_api.closepic()
            # _dll_version = 0
            del _dll_api
        except NameError:
            text = 'Ganessa already unloaded...'
    else:
        text = 'Ganessa was not loaded!'
    if args and args[0]:
        print (text)
    return text
# Register closepic function for proper exit
atexit.register(_close)
quit = _close
close = _close

#****f* Functions/cwfold
# SYNTAX
#   ret = cwfold(folder)
# ARGUMENT
#   str folder: folder name where journal (piccolo.jnl) and work files will be created
# RESULT
#   bool ret: True if folder exists; False otherwise
# HISTORY
#   introduced in 1.7.7 (170705)
#****
try:
    cwfold = _dll_api.cwfold
except AttributeError:
    _fn_undefined.append('cwfold(folder)')
    cwfold = lambda x: False

#****f* Functions/setlang
# SYNTAX
#   oldlang = setlang(new_lang)
# ARGUMENT
#   str new_lang: one of 'English', 'French', 'Spanish'
# RESULT
#   str old_lang: previous language
# DESCRIPTION
#   Modifiy the current command language to new_lang (console version and macros only).
#   If the language name is misspelled, it will be ignored withour raising an error.
# HISTORY
#   introduced in 1.8.0 (170912)
#****
def setlang(new_lang):
    kwl = '_LANG_'
    old_lang = getvar(kwl)
    if len(new_lang) > 2:
        for lg in ('english', 'french', 'spanish'):
            if lg.startswith(new_lang.lower()):
                cmd(kwl + ' ' + new_lang)
                break
    return old_lang
    
# Execution error management
#****f* Functions/useExceptions, GanessaError, SimulationError
# SYNTAX
#   * oldstat = useExceptions([status])
#   * try: ... except GanessaError:
#   * try: ... except SimulationError [as exc]:
# ARGUMENTS
#   bool status: if True, errors will raise exceptions
# RESULT
#   * bool oldstat: previous error handling mode
#   * exception exc: excetion object. The attribute exc.reason will provide
#     additional information on the origin of error
# DESCRIPTION
#   SimulationError is a derived class of GanessaError.
#   The simulation error subtypes are the following:
#   * SIMERR.ISOL: Isolated nodes
#   * SIMERR.SLOW_CV: Slow convergence (convergence not obtained within max iteration count)
#   * SIMERR.UNSTABLE: Unstability (flip between 2 or more equilibrium points)
#   * SIMERR.FCTAPP: Equipment(s) or storage(s) do not operate properly;
#     they can be retrieved with the Unstable() iterator
#   * SIMERR.DIVERGE: Divergence (convergence error increase)
#   * SIMERR.STRUCT: Structural inconsistency
#   * SIMERR.MEMALLOC: Memory allocation error (WQ or inverse problem)
# REMARK
#   Defaults to False: errors do not raise 'GanessaError' exceptions. If set to True,
#   errors raise exceptions with a string name giving the error message and a int reason
#   giving the type of exception.
#****
class GanessaError(Exception):
    def __init__(self, number, reason, text):
        self.number = number
        self.reason = reason
        self.text = text
    def __str__(self):
        return _dll_name + ' ERROR : ({:d}) : {:s}'.format(self.number, self.text)

class SimulationError(GanessaError):
    # Build SimulationError constants from SIMERR
    ISOL = SIMERR.ISOL
    SLOW_CV = SIMERR.SLOW_CV
    UNSTABLE = SIMERR.UNSTABLE
    FCTAPP = SIMERR.FCTAPP
    DIVERGE = SIMERR.DIVERGE
    STRUCT = SIMERR.STRUCT
    MEMALLOC = SIMERR.MEMALLOC
    def __str__(self):
        sreason = {SIMERR.ISOL: 'Isolated nodes',
                   SIMERR.SLOW_CV: 'Slow convergence',
                   SIMERR.UNSTABLE: 'Instability',
                   SIMERR.FCTAPP: 'Equipment or storage do not operate properly',
                   SIMERR.DIVERGE: 'Divergence',
                   SIMERR.STRUCT: 'Structural inconsistency',
                   SIMERR.MEMALLOC: 'Memory allocation error'}.get(self.reason, 'Unknown')
        detail = 'Hydraulic Simulation Error ({:d}) : {:s}\n{:s}'
        return detail.format(self.reason, sreason, GanessaError.__str__(self))

_ganessa_raise_exceptions = False
def useExceptions(enable= True):
    global _ganessa_raise_exceptions
    _ganessa_raise_exceptions = enable

def _checkExceptions(inum, istat, text= ''):
    if _ganessa_raise_exceptions and istat:
        stat = abs(istat)
        SIM_ERR = SIMERR.SIMERR
        if stat & SIM_ERR:     # simulation error code
            raise SimulationError(inum, stat^SIM_ERR, text)
        elif istat > 0:
            raise GanessaError(inum, istat, text)
        else:
            print ('WARNING: ({:d})'.format(inum), text, 'status=', str(istat))

# Execute a command, a set of commands, a command file
#****f* Functions/cmd, addcmdw, execute, cmdfile
# SYNTAX
#   * istat = cmd(scmd)
#   * istat = cmdfile(fname [, args])
#   * istat = addcmdw(scmd)
#   * istat = execute(scmd1 [ ..., scmdn][, dbg= True])
# ARGUMENTS
#   * string scmd: command line to be executed
#   * string fname: data/command file name to be read/executed
#   * string args: optional argument(s) to the command file, as one single string
#   * string scmd1: command line(s) to be executed ('\n' is handled as a command delimiter)
#   * string scmdn: optional command lines(s) to be executed (same as scmd1)
#   * boolean dbg: optional, makes commands to be echoed in the log file.
# RESULT
#   int istat: error status (0 if OK)
# REMARKS
#   - cmd executes the given command
#   - cmdfile reads/executes the commands from the file.
#   - addcmdw pushes the command onto the command stack.
#   - execute pushes the given commands on the stack and executes them
#
#   If an error occurs while reading a file or nested files, the execution stops.
#   If the useException mode is set, the error will raise a GanessaError
#****
addcmdw = _dll_api.addcmd
def cmd(scmd):
    if not _dll_version: init()
    istat = _dll_api.cmd(winstr(scmd))
    _checkExceptions(1, istat, 'Syntax error in command: ' + scmd)
    return istat

def cmdfile(fname, *args):
    if not _dll_version: init()
    istat = _dll_api.cmdfile(winstr(fname), *args)
    _checkExceptions(8, istat, 'Syntax error in file: ' + fname)
    return istat

def execute(*args, **kwargs):
    '''Executes a tuple of commands in turn
    Handles multiple commands separated with \n as well'''
    if not _dll_version: init()
    try:
        dbg = kwargs['dbg']
    except KeyError:
        dbg = False

    if dbg: _dll_api.gencmd(M.GEN.ROOT, M.GEN.ECHO, DICT.ON)
    for arg in args:
        for cmdline in arg.split('\n'):
            if cmdline: _dll_api.addcmd(cmdline)
    if dbg: _dll_api.gencmd(M.GEN.ROOT, M.GEN.ECHO, DICT.OFF)
    istat = _dll_api.commit(0)
    _checkExceptions(4, istat, 'Multiple Commands execution error!')
    return istat

# Execute a command, a set of commands, a command file
#****f* Functions/gencmd, gencmdw, _gencmdw
# PURPOSE
#   Those fuctions allow to generate a language independant command line
#   based upon the keywords id of a module and its commands (see M).
# SYNTAX
#   * istat =  gencmd (module, icmd, [word, scmd, extmode])
#   * istat =  gencmdw(module, icmd, [word, scmd, extmode])
#   * istat = _gencmdw(module, icmd, [word, scmd, extmode])
# ARGUMENTS
#   * module: constant id for the module
#   * icmd:   constant id for the command in the module (or NONE)
#   * word:   constant id for a keyword (or NONE) (optional)
#   * scmd:   additional string (optional)
#   * extmode: if set to 1, the command is appended to the previous one (optional)
#   * string scmd: command line to be executed
# RESULT
#   int istat: error status (0 if OK)
# REMARKS
#   - gencmd builds and executes the given command
#   - gencmdw and _gencmdw build the command and push it onto the command stack
#   - gencmd and gencmdw allow a more flexible entry of the first 2 arguments
#   - If the useException mode is set, an error will raise a GanessaError
#   - raw_gencmdw is an exported version of _gencmdw
# EXAMPLES
#   The following are equivalent:
#   * istat = _gencmdw(M.SIM.ROOT, M.SIM.EXEC, DICT.FULLPER)
#   * istat = gencmdw(M.SIM, "EXEC", DICT.FULLPER)
#   The following are equivalent:
#   * istat = _gencmdw(M.SIM.ROOT, M.SIM.EXEC, scmd="15:30")
#   * istat = gencmdw(M.SIM, "EXEC", scmd="15:30")
# HISTORY
#   1.8.0 (170908): added raw_gencmdw
#****
# Wrapping for 'gencmd': allow the class name as arg1 and if so the attribute name as arg2
_gencmdw = _dll_api.gencmd
raw_gencmdw = _dll_api.gencmd
def gencmdw(module, cmde, *args, **kwargs):
    if not _dll_version: init()
    if isinstance(module, numbers.Number):
        modul = module
    else:
        modul = module.ROOT
    if isinstance(cmde, numbers.Number):
        attr = cmde
    else:
        try:
            attr = getattr(modul, cmde.upper())
        except:
            attr = M.NONE
            print ('Command or keyword not recognised:', repr(cmde), '\n')
    _dll_api.gencmd(modul, attr, *args, **kwargs)

def gencmd(modul, cmde, *args, **kwargs):
    gencmdw(modul, cmde, *args, **kwargs)
    istat =  _dll_api.commit(0)
    _checkExceptions(3, istat, 'Syntax error in command: ')
    return istat

#****f* Functions/getkeyword, modulekeyword, attrkeyword
# PURPOSE
#   Get keyword or command name by index  - for building
#   command language independant functions
# SYNTAX
#   * sret = getkeyword(code)
#   * sret = modulekeyword(module, submodule)
#   * sret = attrkeyword(attr)
# ARGUMENTS
#   * code: int code of the keyword (>0) or global command (<0)
#   * module: int code of the module (<0 for the submodule alone)
#   * submodule: int code of the module (0 for the module alone)
#   * attr: int code of the attribute
# RESULT
#   str sret: trimmed value of the keyword or global command or module submodule
#         (null string if the code or module/submodule is not recognised)
# HISTORY
#   * getkeyword introduced in 1.4.2 (161010)
#   * modulekeyword and attrkeyword intoduced in 1.7.3 (170313)
#****
try:
    _getkeyword = _dll_api.keyword
except AttributeError:
    _getkeyword = lambda code : (0, '')
    _fn_undefined.append('getkeyword')
def getkeyword(code):
    nret, sret = _getkeyword(code)
    return sret[:nret]
try:
    _modulekeyword = _dll_api.modulekeyword
except AttributeError:
    _modulekeyword = lambda m, sm : (0, '')
    _fn_undefined.append('modulekeyword')
def modulekeyword(module, submodule):
    nret, sret = _modulekeyword(module, submodule)
    return sret[:nret]
try:
    attrkeyword = _dll_api.attrkeyword
except AttributeError:
    attrkeyword = lambda code : { 5:'NI', 6:'NF', 60:'ZN'}.get(code, '#')
    _fn_undefined.append('attrkeyword')

#****f* Functions/commit
# PURPOSE
#   Executes all the commands available on the stack (first in, first executed)
# SYNTAX
#   istat = commit()
# RESULT
#   int istat: error status (0 if OK)
# REMARK
#   If an error occurs, the remaining part of the stack is cleared
#****
def commit(*args):
    istat = _dll_api.commit(*args)
    _checkExceptions(2, istat, 'Command language execution error!')
    return istat

#****f* Functions/reset
# PURPOSE
#   Clears (removes) all model objects
# SYNTAX
#   istat = reset()
# RESULT
#   int istat: error status (0 if OK)
#****
def reset():
    if not _dll_version: init()
    nbn = _dll_api.nbobjects(NODE)
    _dll_api.addcmd(' /* before system reset: nb of nodes: ' + str(nbn))
    # COMM INIT
    _dll_api.gencmd(M.COM.ROOT, M.NONE)
    _dll_api.gencmd(M.GEN.ROOT, M.GEN.INIT, extmode= True)
    return _dll_api.commit(0)

#****f* Functions/loadbin
# PURPOSE
#   Clears (removes) all model objects and loads a binary file
# SYNTAX
#   istat = loadbin(fname)
# ARGUMENT
#   string fname: binary data/result file name to be loaded
# RESULT
#   int istat: error status (0 if OK)
# REMARKS
#   - The current model is discarded before the new one is loaded.
#   - If the file content is not a Piccolo binary file an error occurs.
#   - Binary result files also contain all data describing the model.
#****
def loadbin(fname):
    if not _dll_version: init()
    _dll_api.gencmd(M.GEN.ROOT, M.GEN.LOAD, scmd= winstr(quotefilename(fname)))
    istat = _dll_api.commit(0)
    _checkExceptions(16, istat, 'Error loading binfile: ')
    return istat

#****f* Functions/loadres
# PURPOSE
#   Loads the default binary result file.
# SYNTAX
#   istat = loadres()
# RESULT
#   int istat: error status (0 if OK)
# REMARK
#   The current model is discarded before the data corresponding to
#   the last simulation making use of the default result file is loaded.
#****
def loadres():
    if _fresult:
        return loadbin(_fresult)
    else:
        print(' *** Result file not found !')
        return 1

#****f* Functions/resfile
# PURPOSE
#   Returns the name of the default binary result file.
# SYNTAX
#   name = resfile()
# RESULT
#   str name: file name or '' if undefined
# HISTORY
#   Introduced in version 1.8.0 (170919)
#****
def resfile():
    return _fresult

#****f* Functions/nbobjects
# PURPOSE
#   Returns the number of model elements in the given type
# SYNTAX
#   nb = nbobjects(typelt)
# ARGUMENT
#   int typelt: type of element (LINK, NODE, TANK)
# RESULT
#   int nb: number of element in that type
#****
nbobjects = _dll_api.nbobjects

#****f* Functions/selectlen, select
# PURPOSE
#   * selectlen returns the number and type of model elements in the given selection
#   * select: returns the index vector, number and type of elements in the selection
# SYNTAX
#   * nb, typelt = selectlen(sname)
#   * vect_idx, nb, typelt = select(sname)
# ARGUMENT
#   string sname: name of selection
# RESULT
#   * int nb: number of element in that selection
#   * int typelt: type of element of that selection
#   * int vect_idx[]: index vector of elements in the selection
#****
try:
    selectlen = _dll_api.getselectlen
    _select = _dll_api.getselect
except AttributeError:
    selectlen = _dll_api.selectlen
    _select = _dll_api.select
def select(sname):
    nb, typelt = selectlen(sname)
    return (_select(nb), nb, typelt)

#****k* Iterators/Selected
# SYNTAX
#   for id, typelt in Selected(sname):
# ARGUMENT
#   string sname: name of a selection
# RESULT
#   Returns the id and type of each element in the selection in turn:
#   * string id: id of the next element in the selection
#   * int type: element type (the same for all ids)
#****
# Iterators for browsing model elements
class Selected(object):
    def __init__(self, sname):
        self.nbmax, self.type = selectlen(sname)
        if self.nbmax > 0:
            self.select = _select(self.nbmax)
        self.index = 0
    def __iter__(self):
        return self
    def next(self):
        if self.index >= self.nbmax:
            if self.nbmax > 0: 
                del self.select
                self.nbmax = 0
            raise StopIteration
        numelt = self.select[self.index]
        elem, ls = _dll_api.getid(self.type, numelt)
        self.index += 1
        return (elem[0:ls], self.type)
    def len(self):
        return self.nbmax

#****f* Functions/linkattr, nodeattr, tankattr, linkattrs, nodeattrs, tankattrs, attr, attrs, meanattr
# PURPOSE
#   * linkattr, nodeattr, rsvattr, attr: return numerical attributes
#     of a given element by id
#   * linkattrs, nodeattrs, attrs: return text attributes of a
#     given element by id
#   * meanattr: return mean attribute of from and to nodes given by branch id
# SYNTAX
#   * val = linkattr(id, attr)
#   * val = nodeattr(id, attr)
#   * val = tankattr(id, attr)
#   * txt = linkattrs(id, attr)
#   * txt = nodeattrs(id, attr)
#   * txt = tankattrs(id, attr)
#   * val = attr[typelt](id, attr)
#   * txt, sz = attrs(typelt, id, attr)
#   * val = meanattr(id, attr)
# ARGUMENTS
#   * string id: id of element
#   * string attr: attribute (data or result) for which value is requested
#   * int typelt: type of element
# RESULT
#   * float val: value of the numerical attribute (0. if not available)
#   * string txt: value of the text attribute (empty string '' if
#     undefined or not available)
#   * int sz: length of the returned string
# REMARKS
#   * Numerical attributes are returned converted in the actual unit system.
#   * Reservoir text attributes are identical to the underlying node id
#   * meanattr requires version 2016 or higher of Piccolo/Ganessa dll
#   * branchattr, rsvattr and branchattrs are synonyms for linkattr, tankattr and linkattrs
#****
nodeattr = _dll_api.nodeattr
linkattr = _dll_api.branchattr
tankattr = _dll_api.rsvattr
branchattr = _dll_api.branchattr
rsvattr = _dll_api.rsvattr
attr = {LINK: _dll_api.branchattr,
        NODE: _dll_api.nodeattr,
        TANK: _dll_api.rsvattr}
attrs = _dll_api.strattr

def linkattrs(eid, attr):
    sval, n = _dll_api.strattr(LINK, eid, attr)
    return sval[0:n] if n > 0 else ''
branchattrs = linkattrs

def nodeattrs(eid, attr):
    sval, n = _dll_api.strattr(NODE, eid, attr)
    return sval[0:n] if n > 0 else ''

def tankattrs(eid, attr):
    sval, n = _dll_api.strattr(TANK, eid, attr)
    return sval[0:n] if n > 0 else ''

try:
    meanattr = _dll_api.nodemeanattr
except AttributeError:
    meanattr = lambda sid, sattr : 0.0
    _fn_undefined.append('meanattr')

#****f* Functions/shearstr
# PURPOSE
#   Returns the shear stress associated with a velocity for the given pipe
# SYNTAX
#   val, grad = shearstr(id, v)
# ARGUMENTS
#   * string id: id of element
#   * float v: velocity for which value is requested
# RESULT
#   * float val: value of the shear stress
#   * float grad: value of ds/dv
# REMARKS
#   * val is not defined if id is not a pipe
#   * requires Piccolo 2017
# HISTORY
#   * 31.03.2017: function created (1.7.3)
#****
try:
    shearstr = _dll_api.shearstr
except AttributeError:
    shearstr = lambda sid, val : (0.0, 0.0)
    _fn_undefined.append('shearstr')

#****f* Functions/nlinkattr, nnodeattr, ntankattr, nlinkattrs, nnodeattrs, ntankattrs, nattr, nattrs
# PURPOSE
#   * nlinkattr, nnodeattr, nrsvattr, nattr: return numerical attributes
#     of a given element by index
#   * nlinkattrs, nnodeattrs, nattrs: return text attributes of a
#     given element by index
# SYNTAX
#   * val = nlinkattr(num, attr)
#   * val = nnodeattr(num, attr)
#   * val = ntankattr(num, attr)
#   * txt = nlinkattrs(num, attr)
#   * txt = nnodeattrs(num, attr)
#   * txt = ntankattrs(num, attr)
#   * val = nattr[typelt](num, attr)
#   * txt, sz = nattrs(typelt, num, attr)
# ARGUMENTS
#   * string num: index of element (stating at 1)
#   * string id_or_num: id or index of element
#   * string attr: attribute (data or result) for which value is requested
#   * int typelt: type of element
# RESULT
#   * float val: value of the numerical attribute (0. if not available)
#   * string txt: value of the text attribute (empty string '' if
#     undefined or not available)
#   * int sz: length of the returned string
# REMARKS
#   * Numerical attributes are returned converted in the actual unit system.
#   * Tank text attributes are identical to the underlying node id
#****
try:
    nnodeattr = _dll_api.nnodeattr
    nlinkattr = _dll_api.nlinkattr
    ntankattr = _dll_api.ntankattr
    nattrs = _dll_api.nstrattr
except AttributeError:
    _fn_undefined.extend(['nnodeattr', 'nlinkattr', 'ntankattr', 'nxxxattrs'])
    ntankattr = nlinkattr = nnodeattr = lambda num, attr : 0.0
    nattrs = lambda typ, num, attr : ''

nattr = {LINK: nlinkattr,
         NODE: nnodeattr,
         TANK: ntankattr}

def nlinkattrs(num, attr):
    sval, n = nattrs(LINK, num, attr)
    return sval[0:n] if n > 0 else ''
branchattrs = linkattrs

def nnodeattrs(num, attr):
    sval, n = nattrs(NODE, num, attr)
    return sval[0:n] if n > 0 else ''

def ntankattrs(num, attr):
    sval, n = nattrs(TANK, num, attr)
    return sval[0:n] if n > 0 else ''

#****f* Functions/getdemandbycode, getcodedemandinit, nextcodedemand
# PURPOSE
#   * getdemandbycode: returns demand for a given node and consumer code by id
#   * getcodedemandinit: initialises and returns the number of pairs
# SYNTAX
#   * demand, istat = getdemandbycode(id, code)
#   * nbpairs = getcodedemandinit(id)
#   * code, demand, codelen = nextcodedemand()
# ARGUMENTS
#   * string id: id of node
#   * string code: code for which demand value is requested
#   * int nbpairs: number of demand, csm pairs for the node
# RESULT
#   * float demand: value of the demand (0 if not available)
#   * int istat: return code (0= 0K -1= unknown code 1= unknown node 3= dll too old)
#   * int nbpairs: number of code, demand pairs for the node
#   * string code: demand code
#   * int codelen: length of code string
# REMARKS
#   * these functions require version 2016 or higher of the Piccolo/Ganessa dll
#   * If the GanSim Dll is too old those function will not return data
#   * See also the Demands(id) iterator
#****
try:
    getdemandbycode = _dll_api.getdemandnodebycode
    getcodedemandinit = _dll_api.getcodedemandinit
    nextcodedemand = _dll_api.nextcodedemand
except AttributeError:
    getcodedemandinit = _ret_errstat
    _fn_undefined.append('Demands')
    _fn_undefined.append('demand by node getter')

#getcodedemandall = _dll_api.getcodedemandall
#****k* Iterators/Demands
# SYNTAX
#   for code, csm in Demands(node_id):
# ARGUMENT
#   string node_id: id of node
# RESULT
#   Returns each demand code and nominal value for the node in turn:
#   * string code: demand code
#   * float csm: demand value for this code
# REMARK
#   * requires version 2016 or higher of Piccolo/Ganessa dll
#****
# Iterators for browsing demand codes and values for a given node
class Demands(object):
    def __init__(self, node_id):
        self.nb, self.szcod = getcodedemandinit(node_id)
        if self.nb < 0:
            raise GanessaError(8, 0, 'The version of ' + _dll_name +
                                ' does not support this feature')
    def __iter__(self):
        return self
    def next(self):
        if self.nb == 0:
            raise StopIteration
        self.nb -= 1
        code, csm, n = _dll_api.nextcodedemand()
        return (code[0:n], csm) if n > 0 else ('', 0.0)

#****f* Functions/getcodescount, nextcode
# PURPOSE
#   * getcodescount: returns count of used demand codes
#   * nextcode: returns the list of used codes with node count
# SYNTAX
#   * ncodes = getcodescount(used_only)
#   * code, demand, count, nbchar  = nextcode()
# ARGUMENTS
#   * bool used_only: if True, only codes associated with at least
#     one node will be returned
# RESULT
#   * int ncodes: number of codes to be returned
#   * str code: demand codes
#   * float demand: total nominal demand for the code
#   * int count: node count
#   * int nbchar: nb of chars in the demand code string
# REMARKS
#   * these functions require version 2016 or higher of Piccolo/Ganessa dll
#   * If the GanSim Dll is too old those function will not return data
#   * See also the Demands(id) iterator
#****
try:
    getcodescount = _dll_api.getcodescount
    nextcode = _dll_api.nextcodecsmnodecount
except AttributeError:
    _fn_undefined.append('DemandCodes')
    _fn_undefined.append('demand codes table getter')
    getcodescount = _ret_errstat

#****k* Iterators/DemandCodes
# SYNTAX
#   for code, demand, nodecount in DemandCodes():
# RESULT
#   Returns each demand code and node count in turn:
#   * string code: demand code
#   * float demand: total demand value for the code
#   * int count: node count associated with the code
# REMARK
#   * DemandCodes requires version 2016 or higher of Piccolo/Ganessa dll
# HISTORY
#   Added 11/09/2015
#****
# Iterators for browsing demand codes and values for a given node
class DemandCodes(object):
    '''Iterator for demand codes, total nominal demand and node count
    Added 150911'''
    def __init__(self, used_only=False):
        self.used_only = used_only
        self.nbc = getcodescount(used_only)
    def __iter__(self):
        return self
    def next(self):
        if self.nbc <= 0:
            raise StopIteration
        self.nbc -= 1
        code, csm, nbn, lnc = _dll_api.nextcodecsmnodecount()
        return (code[0:lnc], csm, nbn) if lnc > 0 else ('', 0.0, 0)

#****k* Iterators/Table
# SYNTAX
#   for item, objcount in Table(table, typelt):
# ARGUMENTS
#   * string table: requested table (2 char symbol or table name)
#   * int typelt: type of element (LINK or NODE), if table is ZN or ZP.
#     Defaults to LINK.
# RESULT
#   Returns each table entry and associated object count in turn:
#   * string item: table entry
#   * int objcount: node count associated with the code
# REMARK
#   * Table requires version 2015/12 or higher of Piccolo/Ganessa dll
#****
try:
    tablecount = _dll_api.tablecount
except AttributeError:
    _fn_undefined.append('Table')
    _fn_undefined.append('table entries getter')
    tablecount = _ret_errstat

class Table(object):
    '''Iterator for area, area2, material, nominald diameter etc. tables'''
    def __init__(self, table, typelt= LINK):
        self.table = table
        self.nbitems = tablecount(table, typelt)
    def __iter__(self):
        return self
    def next(self):
        if self.nbitems <= 0:
            raise StopIteration
        self.nbitems -= 1
        item, objcount, ln = _dll_api.nexttableentry()
        return (item[0:ln], objcount) if ln > 0 else ('', -1)

#****f* Functions/areas
# PURPOSE
#   * return areas associated with nodes/links
# SYNTAX
#   * area = areas(typelt, attr)
# ARGUMENTS
#   * int typelt: type of object (NODE or LINK)
#   * str attr (optional): area attribute to be returned (ZN or ZP). Default to 'ZN'
# RESULT
#   * counter area: dictionary of node/link counts by area
#   * str code: demand codes
# REMARKS
#   * The functions also return names
#   * See also the Demands(id) iterator
#****
def areas(typelt, attr= ''):
    areas = Counter()
    if typelt not in (NODE, LINK):
        return areas
    if not attr:
        attr = attrkeyword(60)      # ZN
    for i in range(1, _dll_api.nbobjects(typelt) + 1):
        item, n = _dll_api.nstrattr(typelt, i, attr)
        if n > 0:
            areas[item[0:n]] += 1
    return areas

#****f* Functions/getid
# PURPOSE
#   Returns the id of an element by type and index
# SYNTAX
#   id = getid(typelt, numelt)
# ARGUMENTS
#   * int typelt: type of element
#   * int numelt: index of element
# RESULT
#   string id: id of the element
# REMARKS
#   * Internal index starts with 1
#   * Internal index of an element may change after a simulation or
#     a modification of the model.
#****
def getid(typelt, numelt):
    eid, n = _dll_api.getid(typelt, numelt)
    return eid[0:n] if n > 0 else ''

#****f* Functions/getindex
# SYNTAX
#   num = getindex(typelt, id)
# ARGUMENT
#   int typelt: type of element
#   string id: ID of element
# RESULT
#   int num: index of element ID (starting at pos 1)
# HISTORY
#   new in 1.3.3
#****
try:
    getindex = _dll_api.geteltindex
except AttributeError:
    _fn_undefined.append('getindex')
    getindex = _ret_errstat

#****f* Functions/extrnodes
# PURPOSE
#   Returns the from and to node (indexes) form branch index
# SYNTAX
#   i_from, i_to = extrnodes(i_branch)
# ARGUMENTS
#   * int i_branch: index of the branch
# RESULT
#   * int i_from: index of from node
#   * int i_to:   index of to node
# REMARKS
#   * Internal indexes start with 1
#   * Internal index of an element may change after a simulation
#     or a modification of the model.
#****
extrnodes = _dll_api.extrnodes

#****f* Functions/linkXYZV, branchXYZV
# PURPOSE
#   Returns the XYZ polyline representing a link, and eventually
#   an additional node attribute
# SYNTAX
#   * vec_x, vec_y, vec_z, vec_v, len = linkXYZV(id, [attr], [include_depth])
# ARGUMENTS
#   * string id: id of element
#   * string attr: optional attribute for which value is requested
#   * bool include_depth: optional attribute, defaults to False
# RESULT
#   * int len: number of points for the polyline
#   * double[] vec_x, vec_y: vector of coordinates
#   * float[] vec_z: vector of interpolated elevations (minus depth if include_depth= True)
#   * float[] vec_v: vector of interpolated attribute
# HISTORY
#   optional argument include_depth introduced in 1.4.2 (160908)
# REMARKS
#   * Z and V are interpolated from initial and final nodes
#   * if attribute is missing or not recognised vec_v is null.
#   * if the link has no vertice, len=2 and the function returns values
#     from ending nodes
#   * if the id does not exists the return value is (None, None, None, None, 0)
#   * branchXYZV is a synonym of linkXYZV.
#****
try:
    _linkxyzdv = _dll_api.branchxyzdv
except AttributeError:
    _linkxyzdv = _dll_api.branchxyzv
    _fn_undefined.append('linkXYZV(use_depth= True)')

def linkXYZV(sid, sattr= '--', include_depth= False):
    nbval = _dll_api.branchxylen(sid)
    if nbval > 0:
        _func = _linkxyzdv if include_depth else _dll_api.branchxyzv
        return _func(sid, sattr, nbval)
    else:
        return (None, None, None, None, 0)
branchXYZV = linkXYZV

#****f* Functions/linkbbox
# PURPOSE
#   Returns the link bounding box
# SYNTAX
#   * xmin, xmax, ymin, ymax, num = linkbbox(id)
# ARGUMENTS
#   * string id: id of element
# RESULT
#   * int num: link internal number (0 if not found)
#   * double xmin, xmax, ymin, ymax: bounding box
# HISTORY
#   Created in 1.8.5 (171128)
#****
try:
    linkbbox = _dll_api.bbox
except AttributeError:
    def linkbbox(sid):
        nbval = _dll_api.branchxylen(sid)
        if nbval > 0:
            x, y, _z, _v, np = _dll_api.branchxyzv(sid, '--', nbval)
            return np.amin(x), np. amax(x), np.amin(y), np. amax(y), np
        else:
            return (0., 0., 0., 0., 0)

#****f* Functions/nodeXYZ
# PURPOSE
#   Returns the XYZ coordinates and depth of a node
# SYNTAX
#   * x, y, z, dz = nodeXYZ(id)
# ARGUMENTS
#   * string id: id of element
# RESULT
#   * double x, y: coordinates
#   * float z, dz: elevation and depth
# REMARKS
#   * nodeXYZ requires version 2016 or higher of Piccolo/Ganessa dll
#   * if the id does not exists the return value is (None, None, None, None)
#   * In most cases dz is 0.0
#****
try:
    nodeXYZ = _dll_api.nodexyz
except AttributeError:
    _fn_undefined.append('nodeXYZ')
    nodeXYZ = lambda sid : (0.0, 0.0, 0.0, 0.0)

#****f* Functions/dist2link
# PURPOSE
#   Returns the distance and curvilinear abcissae of a point from the given link
# SYNTAX
#   * d, s1, s2 = dist2link(id, x, y)
# ARGUMENTS
#   * string id: id of link element
#   * double x, y: coordinates of the point
# RESULT
#   * double d: distance of the point to the link polyline
#   * double s1, s2: curvilinear distance of the projection from each extremity
# HISTORY
#   introduced in 1.3.7 (160706)
# REMARKS
#   * dist2link requires version 2016b or higher of Piccolo/Ganessa dll;
#     if not a pure python calculation is made using linkXYZV
#   * the polyline length is s1 + s2;
#     s1= 0 or s2= 0 when the point projection is outside the polyline
#   * if the id does not exists the return value is (-1, -1, -1)
#****
try:
    dist2link = _dll_api.distlink
except AttributeError:
    # _fn_undefined.append('dist2link')
    def dist2link(sid, x, y):
        xs, ys, _zs, _vs, nseg = linkXYZV(sid)
        if nseg:
            return dist_to_poly(x, y, nseg, xs, ys)
        else:
            return -1, -1, -1

#****f* Functions/getvar, getunitname, getunitcoef
# PURPOSE
#   Returns the value of a Piccolo expression or variable
# SYNTAX
#   * str_val = getvar(expression)
#   * str_val = getunitname(attr)
#   * coef = getunitcoef(attr)
# ARGUMENTS
#   * string expression: the expression or variable to be returned
#   * string attr: attribute
# RESULT
#   * string str_val: a string containing the expected value
#   * float coef: a float giving the unit coefficient / internal units
# REMARKS
#   * Unit coefficient of a given attribute can also be returned with
#     the adequate getvar('unite.'+attr).
#   * The unit coefficient is the number of internal units per user units:
#     1 (user unit) = coef (internal unit).
#   Internal units are SI units excepted:
#   * diameter and roughness:  mm
#   * pressure: mwc
#   * concentrations: mg/l (or ppm)
#   * consumed mass (D1): g
# EXAMPLE
#    If the user flow unit is 'l/s', since internal flow unit is 'm3/s',
#    getunitcoef('Q') returns 0.001 
#****
def getvar(varname):
    sval, slen = _dll_api.getvar(varname)
    return sval[:slen]

def getunitname(attr):
    sval, slen = _dll_api.getunit(attr)
    return sval[:slen]

try:
    getunitcoef = _dll_api.getunitval
except AttributeError:
    def getunitcoef(attr):
        sunit = modulekeyword(M.GEN.ROOT, M.GEN.UNIT)
        scoef = getvar(sunit + '.' + attr)
        return float(scoef)
        
#****f* Functions/getall
# PURPOSE
#   * getall returns the value for all objects of the given type
#     for all objects of the given type
# SYNTAX
#   * vect = getall(typelt, attr)
# ARGUMENTS
#   * int typelt: type of element (LINK, NODE, TANK)
#   * string attr: attribute (result) for which value is requested
# RESULT
#   * float[] vect: vector of values
# REMARKS
#   getall(typelt, attr): when typelt =1 (links), attr can be either a regular attribute
#   ('Q', 'V', 'D', etc.) or a node-based attribute such as 'P:M' for mean pressure,
#   'P:G' for geometric mean, 'P:N' for min and 'p:X' for max.
#****
def getall(typelt, sattr):
    nbval = _dll_api.nbobjects(typelt)
    if nbval > 0:
        return _dll_api.getall(typelt, sattr, nbval)
    else:
        return None

#****k* Iterators/Unstable
# PURPOSE
#   Provide access to the list of elements which status cannot be determined
#   thus causing a simulation not converge.
# SYNTAX
#   for item, typelt in Unstable():
# ARGUMENTS
#   none
# RESULT
#   Returns each unstable element in turn:
#   * string item: element ID
#   * int typelt: element type
# REMARK
#   * Unstable requires version 2016 (160118) or higher of Piccolo/Ganessa dll
# HISTORY
#   new in 1.3.2
#****
try:
    unstablecount = _dll_api.unstablecount
except AttributeError:
    _fn_undefined.append('Unstable')
    _fn_undefined.append('unstable getter')
    unstablecount = _ret_errstat

class Unstable(object):
    '''Iterator ustable items during a simulation'''
    def __init__(self):
        self.nbitems = unstablecount()
    def __iter__(self):
        return self
    def next(self):
        if self.nbitems <= 0:
            raise StopIteration
        self.nbitems -= 1
        item, typelt, ln = _dll_api.nextunstableentry()
        return (item[0:ln], typelt) if ln > 0 else ('', 0)

#****f* Functions/save, savemodel
# SYNTAX
#   * istat = save(fname [, version])
#   * istat = savemodel(fname [, version])
# ARGUMENTS
#   * string fname: file name to save to
#   * string version: optional version string "x.yz" for writing compatible file format,
#     for text file only.
# RESULT
#   int istat: error status (0 if OK)
# REMARKS
#   * 'save' uses the same procedure as Piccolo MMI.
#   * 'savemodel' is pure python and produces the same hydraulic content;
#     exotic options and cost data are not saved.
#   * If filename ends with '.bin' then data is saved as binary. Otherwise data is
#     saved as text (.dat mode) file.
#   * If the useException mode is set, any error will raise GanessaError exception.
#****
def _save_kw_command():
    # SAVE TEXT COMM
    _dll_api.gencmd(M.GEN.ROOT, M.GEN.SAVE, DICT.TEXT)
    _dll_api.gencmd(M.COM.ROOT, M.NONE, extmode= 1)

def save(fname, version= ''):
    return _dll_api.savefile(fname, version)

def savemodel(fname, version= None):
    # First close opened file if any
    _dll_api.gencmd(M.COM.ROOT, M.NONE)
    _dll_api.gencmd(M.GEN.ROOT, M.GEN.CLOSE)

    fwq = winstr(quotefilename(fname))
    if fname.lower().strip('"\'').endswith('.bin'):
        _dll_api.gencmd(M.GEN.ROOT, M.GEN.OPEN, DICT.BINARY, fwq)
        _dll_api.gencmd(M.GEN.ROOT, M.GEN.SAVE, DICT.DATA)
    else:
        if version:
            _dll_api.gencmd(M.GEN.ROOT, M.GEN.COMPAT, M.NONE, version)
        _dll_api.gencmd(M.GEN.ROOT, M.GEN.OPEN, DICT.DATA, fwq)
        for module in ('NOD', 'BRA', 'RSV', 'DYN', 'LAB', 'MES', 'SIM'):
            _dll_api.gencmd(M.GEN.ROOT, M.GEN.SAVE)
            _dll_api.gencmd(getattr(M.ROOT, module), M.NONE, extmode= 1)
        # singularities and wording
        _save_kw_command()
        _dll_api.gencmd(M.GEN.ROOT, M.GEN.SAVE)
        _dll_api.gencmd(-M.BRA.ROOT, M.BRA.SING, extmode= 1)
        _save_kw_command()
        _dll_api.gencmd(M.GEN.ROOT, M.GEN.SAVE)
        _dll_api.gencmd(M.GEN.ROOT, M.GEN.WORDING, extmode= 1)
        _save_kw_command()
        # Quality at the end, in case option not available
        _dll_api.gencmd(M.GEN.ROOT, M.GEN.SAVE)
        _dll_api.gencmd(M.QUA.ROOT, M.NONE, extmode= 1)
        # _dll_api.gencmd(M.GEN.ROOT, M.GEN.EOF, extmode= 1)
    # Close and commit
    _dll_api.gencmd(M.GEN.ROOT, M.GEN.CLOSE)
    istat = _dll_api.commit(0)
    if _ganessa_raise_exceptions and istat:
        raise GanessaError(9, istat, 'Error while saving model')
    return istat

#****f* Functions/addSHLtype, addSHL, updateSHL, delSHL
# PURPOSE
#   * addSHLtype: Add / modify a single head losses (SHL) from the SHL table
#   * addSHL, updateSHL, delSHL: Add / modify / delete single head losses (SHL)
#     objects for a given pipe
# SYNTAX
#   * istat = addSHLtype(shltype, values [, comment])
#   * istat = addSHL(id, shltype, nb)
#   * istat = updateSHL(id, shltype, nb)
#   * istat = delSHL(id [, shltype])
# ARGUMENTS
#   * string shltype: type of shl to be added/modified
#   * float values: direct and reverse SHL coefficients
#   * string comment: long name of the SHL type
#   * string id: id of pipe
#   * int nb: number of SHL of type shltype to be added / updated with
# RESULT
#   int istat: error status (0 if OK)
# COMMENTS
#   If shltype is not given or is '' for delSHL then all SHL are removed from pipe.
# REMARK
#   * these functions require version 2015/12 or higher of Piccolo/Ganessa dll
#****
try:
    def addSHLtype(shltype, values, comment=' '):
        _dll_api.addshlentry(shltype, values, comment)
    addSHL = _dll_api.addsingleshl
    updateSHL = _dll_api.updatesingleshl
    def delSHL(sid, shlid=''):
        _dll_api.removeshl(sid, shlid)
except AttributeError:
    _fn_undefined.append('SHL getter and setter')
    addSHLtype = _ret_errstat
    updateSHL = _ret_errstat
    delSHL = _ret_errstat

#****f* Functions/setlinkattr, setbranchattr
# SYNTAX
#   * istat = setlinkattr(id, attr, val)
#   * istat = setbranchattr(id, attr, val)
# ARGUMENTS
#   * string id: id of element
#   * string attr: attribute (data or result) to be set to val
#   * float val: new value for attr
# RESULT
#   int istat: error status:
#   * 0 if OK
#   * 1 if the attribute is not defined for the type of link
#   * -1 if the attribute is not recognised
#   * -2 if the link does not exist
# REMARKS
#   * setbranchattr requires version 2015/12 or higher of Piccolo/Ganessa dll
#   * setlinkattr is a synonym that has been introduced as 22/09/2016
#****
try:
    setbranchattr =  _dll_api.setbranchattrbyid
except AttributeError:
    _fn_undefined.append('setbranchattr')
    setbranchattr = _ret_errstat
setlinkattr = setbranchattr

#****o* Classes/Graph, extrnodes, adjlinks, adjnodes, propagate, dtree
# SYNTAX
#   graph = Graph()
# METHODS
#   * from_n, to_n = graph.extrnodes(alink): returns the from and to nodes of alink
#   * linkset = graph.adjlinks(anode): returns links adjacent to anode as a set
#   * nodeset = graph.adjnodes(anode): returns nodes adjacent to anode as a set
#   * plist = graph.oriented_links(anode): returns a list of (link, index) tuples
#   * slinks, snodes = graph.propagate(anode [, maxlen= -1]):
#     returns the sets of links and nodes connected to 'anode' by a path of max length 'maxlen'
#   * dtree, slinks = graph.dtree(anode [, maxlen= -1]): returns a tree as an ordered dict
# ARGUMENTS
#   * alink, anode: link, node ID
# RESULT
#   * set linkset: set of adjacent links ID
#   * set nodeset: set of adjacent nodes ID
#   * plist: list of tuples (ID alink, int idx) where idx is the index 
#     of the other node in graph.edges[alink] (graph.edges[alink][1-idx] == anode).
#   * sets slinks, snodes: sets of links and nodes ID.
#   * OrderedDict dtree: ordered dict where key are node IDs, values are a link ID
#     and a depth integer value. The link allows to connect the node.
# REMARK
#   first key, value returned by dtree is the root node, and ('', 0)
# HISTORY
#   * new in 1.3.7 (160706)
#   * reviewed 1.7.6 (170620): use attrkeyword() for IN and FN
#   * reviewed 1.8.2 (171103): added graph.dtree
#   * reviewed 1.8.5 (171128): updated dtree, added graph.adjnodes
#****
class Graph(object):
    '''Dual node/link representation for in depth propagation'''  
    def __init__(self):
        KWNI = attrkeyword(5)   # initial node
        KWNF = attrkeyword(6)   # final node
        self.nodes = {n:set() for n in Nodes()}
        self.edges = {a:(linkattrs(a, KWNI), linkattrs(a, KWNF)) for a in Links()}
        for a, nn in self.edges.viewitems():
            for n in nn:
                self._addtonode(n, a)

    def extrnodes(self, alink):
        return self.edges[alink]

    def adjlinks(self, anode):
        return self.nodes[anode]
    
    def adjnodes(self, anode):
        '''Returns the other nodes of the links connected to anode'''
        return {self.edges[a][1 if anode == self.edges[a][0] else 0]
                        for a in self.nodes[anode]}
        
    def oriented_links(self, anode):
        '''Returns the links and the indice for the other node'''
        return [(a, 1 if anode == self.edges[a][0] else 0) 
                        for a in self.nodes[anode]]

    def _addtonode(self, n, a):
        try:
            self.nodes[n].add(a)
        except KeyError:
            self.nodes[n] = {a}

    def add(self, link, nodes):
        if isinstance(link, basestring) and isinstance(nodes, tuple):
            self.edges[link] = nodes
            for n in nodes:
                self._addtonode(n, link)

    def remove(self, link):
        for n in self.edges[link]:
            self.nodes[n].remove(link)  # discard for error tolerance
        del self.edges[link]

    def propagate(self, rootnode, maxlen= -1):
        '''Finds links / nodes connected to the root up to the given depth'''
        edges = set()
        nodes = {rootnode}
        border_nodes = {rootnode}
        while maxlen and border_nodes:
            maxlen -= 1
            border_edges = set()
            for n in border_nodes:
                border_edges.update(self.nodes[n])
            edges.update(border_edges)
            border_nodes = {n for a in border_edges for n in self.edges[a] if n not in border_nodes}
            nodes.update(border_nodes)
        return edges, nodes

    def dtree(self, rootnode, maxlen= -1):
        '''Build a tree from rootnode as an OrderedDict'''
        border_nodes = HeapSort()
        border_nodes.push((rootnode, ''), 0)
        nodes = OrderedDict()
        edges = set()
        while len(border_nodes):
            (n, an), cumlen = border_nodes.pop()
            nodes[n] = an, cumlen
            if cumlen == maxlen:
                continue
            for a, k in self.oriented_links(n):
                edges.add(a)
                nk = self.edges[a][k]
                if nk not in nodes:
                    border_nodes.update_if_lower((nk, a), cumlen + 1)
        return nodes, edges

### Print functions not available due to obsolete version of dll ###

if _fn_undefined:
    print('Warning: the following functions and iterators are not compatible with this version of', _dll_name, ':')
    nuf, duf = len(_fn_undefined), 5
    for k in range(0, nuf, duf):
        print('   ', ', '.join(_fn_undefined[k:min(k+duf,nuf)]))
    del nuf, duf

#**#**f* Functions/getcluster
# PURPOSE
#   Computes and returns the index of the nearest node in the selection,
#   as cumulated path relative to the given attribute.
# SYNTAX
#   vec_idx = getcluster(sname [, attr] [, copybuf])
# ARGUMENTS
#   * string sname: name of selection
#   * string attr (optional): attribute used for weighing links (expected L, XX, YY, ZZ, RH/HD).
#     Defaults to RH/HD
#   * string copybuf (optional): the result is also copied on node attribute copybuf.
#     Valid arguments are '', 'XX', 'YY' or 'ZZ'.
# RESULT
#   int vec_idx[]: vector of the nearest root node. 0 means that the node is not
#   connected to the root selection.
# HISTORY
#   introduced and aborted in 1.3.3
# REMARK
#   if sname is a link or tank selection, it is converted to a node selection.
#****
#try:
#    _tmp = _dll_api.getcluster
#except AttributeError:
#    print('getcluster function not defined in this version of', _dll_name)
#    getcluster = _ret_errstat
#else:
#    def getcluster(sname, attr= ' ', copybuf= ' '):
#        return _dll_api.getcluster(sname, attr, copybuf.upper(), _dll_api.nbobjects(NODE))
