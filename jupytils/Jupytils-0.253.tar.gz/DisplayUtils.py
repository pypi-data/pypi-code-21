import numpy as np
#import pylab as pl
#from matplotlib.colors import ListedColormap
#from sklearn import neighbors, datasets
import matplotlib.pyplot as plt
import pandas as pd
from IPython.display import HTML
import os
import glob;
import re;
#plt.style.use('fivethirtyeight') # Good looking plots
pd.set_option('display.max_columns', None) # Display any number of columns
import platform
import matplotlib
from sklearn import neighbors, datasets, cluster, preprocessing, decomposition
from sklearn.decomposition import PCA
from Features import prepareDF
from matplotlib import colors
import inspect
import re;
import json;
import datetime

if (platform == "Windows"):
    from win32com.client import Dispatch
    from win32com.client.gencache import EnsureDispatch
    from win32com.client import constants
    from IPython.display import IFrame

np.set_printoptions(precision=2, linewidth=1000)

matplotlib.rcParams['lines.linewidth'] = 1
matplotlib.rcParams['lines.color'] = 'r'

#=======================================================================================
def Excel2Html(file, overwrite=True, show=True, leaveItOpen = True, 
                   width="100%", length="400px"):
    f = file.replace("/", "\\");
    #xl = Dispatch('Excel.Application')
    xl = EnsureDispatch ("Excel.Application")
    cwd=os.getcwd() + "\\" + f
    ext = cwd.split(".")[-1]
    nef=cwd.replace(ext, "html")
    nhtml = file.replace(ext, "html")

    fileOpenNow = False;
#    if (not os.path.exists(cwd)):
#        display("File " + cwd + " not found");
#        return;
#    else:
#       try:
#           f = open(cwd, "r+");
#           f.close();
#       except:
#           fileOpenNow =True;
    print (cwd, nef, nhtml, fileOpenNow)
           
    wb=xl.Workbooks.Open(cwd)
    xl.Visible = True #-- optional
    if os.path.exists(nef):
        os.remove(nef)
    wb.SaveAs(nef, constants.xlHtml)
    wb.Close()
#    if (fileOpenNow or leaveItOpen):
    wb=xl.Workbooks.Open(cwd)
    del xl;
    if (show):
        display(IFrame(nhtml, width, length))    

#=======================================================================================
# EXAMPLE USE
# graph a function 
# graphFunction(lambda x: x ** 3, 0,10)
#
# graphFunction('x', 0,1, "r", "$x$", "$z$", "", '.') #, 'o', "sada")
# graphFunction('1/(1+np.exp(-x))', -6,6, "g", "$x$", "$z$", "",'.',"$z=\\frac{1}{1+e^{-\\theta^{T} x}}$") #, 'o', "sada")
# graphFunction(lambda x: log(x), 0,6, "b", "$x$", "$z$", "",'.',"$log(x)$") #, 'o', "sada")

def graphFunction(formula, xmin, xmax, c=None, xlabel= None, ylabel=None, title=None, marker=None, 
                    label=None, legend=True, legendLoc=2):
    x = np.linspace(xmin, xmax, 100)
    if ( callable(formula)):
        y = np.apply_along_axis(formula, 0, x)
        #print ("Evaluating Function", str(formula), y)
    elif (type(formula) == str):
        y = eval(formula)
        #print ("Evaluating", formula, y)
    else:
        y = formula

    #return 
    label = label if label else str(formula);
    plt.plot(x, y, c=c, marker=marker, label=label, linewidth=1)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title (title, fontsize = 15)
    fs = 20 if (label.find("$") > 0) else 15
    plt.legend(fontsize=15, loc=legendLoc) if ( legend) else None;

'''
=======================================================================================
Convenient class A to manage and display matrices

# Example Usage
a= A(('1 7 2 3. 5 5 6 6 7 8.' * 3 +";") * 4, "A")
#a.a = a.a.T # create transpose
a.l          # display latex version of the matrix
=======================================================================================
'''
from IPython.display import display, Math, Latex
import numpy as np
import re
class LA:
    print_width = 120;

    def dtype(self):
        return "A"

    def __init__(self, s = "", name ="\_"):
        self.type = "ClassA"

        if ( type(s) is np.ndarray or type(s) is np.matrix):
            self.a = np.matrix(s)
        #if ( type(s) is np.ndarray or type(s) is np.matrix):

        if ( type(s) is str):
            self.a = A.setM(s)
        elif ( type(s) is list ):
            self.a = np.array(s) #[None]
        self.name = name;

    @staticmethod
    def setM( str = None):
        str = str.replace("[", "")
        str = str.replace("]", "")
        ss = str.split(';')
        r = None;
        for i,s in enumerate(ss):
            s = s.strip();
            if ( len(s) <= 0):
                continue;
            a = A.setA(s)
            r = a if i == 0 else np.vstack((r,a))

        return np.matrix(r)

    @staticmethod
    def setA(s = None):
        if (s == None):
            return []
        s = s.replace(",", " ")
        a = s.split()
        try:
            a = list(map(int, a))
        except:
            a = list(map(float, a))

        a = np.array(a)
        return a

    def p(self):
        np.set_printoptions(precision=2, linewidth=180)
        print ("shape=", self.a.shape, " name:", self.name)
        s = str(self.a)
        s = s.replace('[', '')
        s = s.replace(']', '')

        s =  "[" + s + "]"
        return s

    def pr(self,output=True, noName=False):
        np.set_printoptions(precision=2, linewidth=180)
        m = self.a;

        dim = self.name + "_{" + " \\times ".join(map(str, (m.shape) )) + "} = ";
        lhs = "" if noName  else dim;

        s = str(m)
        s = s.replace('[', '')
        s = s.replace(']', '')
        s = s.replace('\n', '\\\\\\\\<NEW-LINE>')
        s = re.sub( '\s+', ' ', s ).strip()
        s = s.replace('<NEW-LINE>', "\n")
        s = re.sub('\n\s+', '', s)
        s = s.replace(' ', ' & ')
        s = lhs + "\\begin{bmatrix}\n" + s + "\n\\end{bmatrix}"
        #print self.a
        if ( output):
            display(Math(s))
        return s;

    @staticmethod
    def M(m, name="", call_display=True, showdim=True, precision=4):
        np.set_printoptions(precision=precision, linewidth=180)
        name = name + " =" if name != "" else ""
        dim = "";
        if (showdim):
            dim = " \\times ".join(map(str, (m.shape) )) ;
        s = str(m)
        s = s.replace('[', '')
        s = s.replace(']', '')
        s = s.replace('\n', '\\\\\\\\<NEW-LINE>')
        s = re.sub( '\s+', ' ', s ).strip()
        s = s.replace('<NEW-LINE>', "\n")
        s = re.sub('\n\s+', '', s)
        s = s.replace(' ', ' & ')
        s = name + "\\begin{bmatrix}\n" + s + "\n\\end{bmatrix}" +  dim + "\n"
        #print self.a
        if ( call_display):
            display(Math(s))
        return s;


    #Display thr matrix
    @staticmethod
    def display(*M):
        s = ""
        for m in M:
            s+= LA.M(m, call_display=False, showdim=False);
        display(Math(s))

    def d(self):
        self.display(self.a, self.name)
        return self.a

    # Returns Latex information
    @property
    def T(self):
        return A(self.a.T)

    # Returns Latex information
    @property
    def l(self, output=True):
        np.set_printoptions(precision=2, linewidth=180)
        name = self.name + " =" if self.name != "" else ""
        dim = " \\times ".join(map(str, (self.a.shape) )) ;
        s = str(self.a)
        s = s.replace('[', '')
        s = s.replace(']', '')
        s = s.replace('\n', '\\\\\\\\<NEW-LINE>')
        s = re.sub( '\s+', ' ', s ).strip()
        s = s.replace('<NEW-LINE>', "\n")
        s = re.sub('\n\s+', '', s)
        s = s.replace(' ', ' & ')
        s = name + "\\begin{bmatrix}\n" + s + "\n\\end{bmatrix}" +  dim + "\n"
        #print self.a
        #if (output): display(Math(s))
        return s;

    def __str__(self):
        return self.p()

    def __add__(self, o):
        if (type(o) is int):
            r = self.a + 3
        else:
            r = np.add(self.a, o.a)
        ret = A(r)
        return ret


    def __mul__(self, o):
        if (type(o) == A ):
            r = self.a * o.a
        else:
            r = self.a * o.a
        ret = A(r)
        return ret

def formatContentDELETEIT(c):       
    c1 = str(c).lower().strip()
    g=[k.lower().strip() for k in "complete, finished, success, Yes".split(",") ]
    r=[k.lower().strip() for k in "error, err, failed, no".split(",") ]
    y=[k.lower().strip() for k in "pending, ongoing, current".split(",") ]
    s = ""
    if (c1 in g):
         s = "bgcolor=lightgreen";
    elif (c1 in r):
         s = "bgcolor=#FFAEAE";
    elif (c1 in y):
         s = "bgcolor=lightyellow";
        
    return "<td " + s + ">" + str(c) + "</td>"
    
#if not os.path.exists("temp"):
#    os.mkdir("temp")

#Lets Clean up before we start
[os.unlink(f) for f in glob.glob("./temp/*.png")]
    
def PCAPlot(dfL, predictColumn, s =10):
    predictColumnIdx = predictColumn+'_idx'
    
    ny = dfL[predictColumn]
    df = prepareDF(dfL, makeCopy=True)
    df = df.drop(predictColumn, axis=1)
    pca= PCA(n_components= 2)
    pca.fit(df)
    nX = pca.transform(df)
    
    le = preprocessing.LabelEncoder()
    labels = le.fit_transform(ny)
    le.classes_
    
    nDf = pd.DataFrame(nX)
    nDf[predictColumn] = ny;
    nDf[predictColumnIdx] = labels;
    
    c="r,g,b,c,m,y,k,w".split(",")
    
    for i,j in enumerate(le.classes_):
        dd = nDf[nDf[predictColumnIdx] == i]
        ll = str(le.classes_[i]);
        lb = ll + ":" + str(i) if ( ll != str(i)) else str(ll);
        #print( i,j )
        #plt.scatter(dd[[0]], dd[[1]], s=40, c=dd[predictColumnIdx].apply(lambda x:c[x]));
        plt.scatter(dd[[0]], dd[[1]], s=40, c=dd[predictColumnIdx].apply(lambda x:c[x%len(c)]), label=lb);
    
    plt.legend();

    return nDf;


#
# x must be in percentages of use - otherwise convert to percentages before this call
#
def plotPercentHist(x, bins=10, rangeI=(0.0,1.0)):
    h, be = np.histogram(x,bins=bins,range=rangeI, normed=True)
    plt.bar(be[:-1],h*100,width=be[1])
    plt.xticks(be);
    return h,be

#def pltBar(x, labels=None, bottom=None):
   #x = x.value_counts()
#plt.bar(x, range(0, len(x)), bottom=bottom);
    #if (labels is None):
    #labels = range(0,len(x));
    #plt.xticks(labels);

import math
import StatUtils
def plthist(x, y=None, bins='auto', alpha=0.75, title=None, grid = True, xlabel=None, 
            ylabel=None, label=None, axis=None, subplot=None, 
            facecolor=None, ablines=[], legend=False,
            low=None, high=None,  
           ):
    c='brygcmykw';
    if(subplot):
        plt.subplot(subplot)
        
    N, bins, patches = plt.hist(x, bins=bins, alpha=alpha, label=label, facecolor=facecolor)

    if (low is not None and high is None ):
        high = math.inf
    if (high is not None and low is None):
        low = -math.inf
    if(low is not None and high is not None ):
        ca=plt.gca()
        w = min(high, max(x)) - max(low, min(x));
        l = max(low, min(x))
        
        hm = max(N)/4
        rect = plt.Rectangle( (l,0), w,hm, alpha=.6, facecolor='y')
        ca.add_patch(rect)
        
        rx, ry = rect.get_xy()
        cx = rx + rect.get_width()/2.0
        cy = ry + rect.get_height()/2.0
        r = StatUtils.NormProb(x, low,high) * 100
        r1 = "Prob: {0:0.0f}-{1:0.0f} : {2:0.2f}%".format(low, high,r)
        plt.annotate(str(r1), (cx, cy), color='w', weight='bold', fontsize=8, ha='center', va='center')
        
    #print(low, high)    
        
        
    if(grid is not None): plt.grid(grid)
    if(xlabel is not None): plt.xlabel(xlabel)
    if(ylabel is not None): plt.ylabel(ylabel)
    if(axis is not None):  plt.axis(axis)
    if(title is not None): plt.title(title)
    
    for i,f in enumerate(ablines):
        try:
            methodToCall = getattr(x, f)
            v = methodToCall();
            #plt.axvline(v, color='b', linestyle='dashed', linewidth=2, )
            lab = f + " : " + "{0:0.2f}".format(v)
            lab = f
            plt.axvline(v,  color=c[i%len(c)], linestyle='dashed', linewidth=1, label=lab)
            #plt.text(v+.1, 75, lab ,rotation=90)
            #plt.annotate(lab, xy=(v, 1), xytext=(v, 75),arrowprops=dict(facecolor='black', shrink=0.05),)
            
        except:
            print("Method '{}' not found".format(f))
            
    if (legend):
        leg=plt.legend(loc='best', frameon=1)    

'''
=======================================================================================
Print analysis on the Pandas dataframe
=======================================================================================
'''
def searchDF(df, s="", cols=[], maxRows=10):
    rows=[]    
    for i, r in df.iterrows():
        for j, c in r.iteritems():
            if (len(cols) > 0 and not c in cols):
                break;
            if ( str(c).find(s) >= 0):
                maxRows = maxRows -1;
                rows.append(i)
                break;
        if (maxRows ==0):
            break
    df1 = df.iloc[rows];
    return df1;
    

def colTypesDF(df):
    dfTypes=pd.DataFrame(df.dtypes)
    dfTypes=dfTypes.transpose()
    cols=[];
    for i, c in enumerate(dfTypes.columns):
        nc = (str(c) + "\n\t(" + str(dfTypes.iloc[0][i])+")")
        cols.append(nc);
    return cols;

def getFileName(df,idx):
    c = df.columns[idx];
    c=re.sub(r'[\s+?\']', '', str(c))
    prefix = hex(id(df)) + "-"+c;
    figName1 = "temp/"+ prefix + ".png";    
    
    if not os.path.exists("temp"):
        os.mkdir("temp")
    
    return figName1;    

def isAnyDataPoint(t):  
    for k in t:
        if not np.isnan(k):
            return True;
    return False;
    
def createIcon(df,idx):
    t = df.iloc[:,idx]

    scale=7;
    figName1 = getFileName(df,idx)

    if (os.path.exists(figName1)):
        return figName1;

    k = "hist"
    if (df.dtypes[idx] == object or str(df.dtypes[idx]).find("date") >= 0 ):
        u=len(t.unique());
        if (u>100):
            return None;
        else:
            t = t.value_counts();
            k = "bar";
    if not isAnyDataPoint(t):  
       return None;
               
    #print ("N= " , df.columns[idx]);
    ax=t.plot(kind=k, figsize=(1*scale, 0.5*scale), grid=True);
    ax.get_xaxis().set_visible(True)
    ax.get_yaxis().set_visible(True)
    ax.set_frame_on(False)
    fig = ax.get_figure()
    fig.savefig(figName1,  transparent=True);
        
    plt.close();
        
    return figName1;


def getDesc(df, idx):
    t = df.iloc[:,idx].describe(include='all')

    out = "";
    for ii,jj in enumerate(t):
        if ( str(type(jj)).find('float') >=0):
           val = "{0:0.2f}".format(jj) 
        else:
           val = str(jj)
        tval = "<td>{} : {} </td>".format(t.index[ii] , val)
        
        #if (df.dtypes[idx] == object or str(df.dtypes[idx]).find("date") >= 0 ):
        if (ii == 4):
            out += "</tr><tr>"+tval
        else:
            out += tval;

    out = "<table><tr>" + out + "</tr></table>";
    return out


def getIcons(df,h):
    h1="<tr><td align=center></td >";
    idx=0;
    for i, c in enumerate(df.columns):
        fig = None 
        try:
           fig = createIcon(df,idx);
        except:
           print ("Error while getting icon for ", c);
        if ( fig is None):
            h1 = h1 + "<td align=center></td>";
        else:
            
            #fig = "/files/" + fig;
            desc = getDesc(df, idx);
            h1 = h1 + '''
<td><a class='thumbnail' href='#thumb'>
<img src='{}' border=0 style='{{margins: 0;}}' width=64 height=64 /> 
<span><img src='{}' /><br />
{} {}
</span></a>'''.format(fig, fig, '', desc); #getDesc(df,idx);

            #h1 = h1 + "<td><a class='thumbnail' href='#thumb'><img src='" + fig;
            #h1 = h1 + "' border=0 style='{margins: 0;}' width=64 height=64 ";
            #h1 = h1 + "/> <span><img src='"+ fig + "' /><br /></span></a>";
#            h1 = h1 +"onmouseover='this.width=500;' onmouseout='this.width=64' >" 
                        
            h1 = h1 + "<br/>" + str(df.dtypes[i]) + "</td>";  
            
        idx=idx + 1;          
    h1 = h1 + "</tr>\n";
    idx = h.find("<tr");
    ret = h[:idx] +h1+h[idx:];
    return ret;    

def addDescribe(df,h):
    df1d= df.describe(include='all')
    hd = df1d.to_html();
    idx1 = hd.find("<tbody>") + 8;
    idx2 = hd.find("</tbody>");
    rep = hd[idx1:idx2] 
    rep = rep.replace("<tr>", "<tr bgcolor=#e6e6fa>",4)
    rep = rep.replace("<tr>", "<tr bgcolor=#dddddd>")
    rep = rep.replace("nan", "-")
    rep = rep.replace("NaN", "-")
    idx = h.find("<tr");
    ret = h[:idx] +rep+h[idx:];
    ret = ret.replace("<th>", "<th bgcolor=#e6e6fa>",4)
    ret = ret.replace("<th>", "<th bgcolor=#6495ed>")
   
    return ret;

def getHTMLTableRows(dff, startRow=0, maxRows = 5):
    
    startRow = startRow if startRow >=0 else 0;
    e = startRow + maxRows
    
    if (e > len(dff)):
        ddd=dff[-maxRows:]
    else:
        ddd=dff[startRow:e]

    vals = re.findall('<td>(.*?)</td>',  ddd.to_html(), flags=re.DOTALL|re.M|re.MULTILINE|re.IGNORECASE)
    idxs = [""] + (list(ddd.index) )

    
    #ret = '''"vals": {}; "idxs": {}'''.format(json.dumps(vals), json.dumps(idxs))
    ret = '''{{"vals": {}, "idxs": {}}}'''.format(json.dumps(vals), (idxs) )
    
    ret = ret.replace("'", '"')
    
    return ret

def getHTMLTableRowsFromSearch(dff, searchString=None, maxRows=10):
    searchString = str(searchString)
    if (searchString is None or len(str(searchString).strip()) < 0):
        return '';
    
    ddd = searchDF(dff, s=searchString, maxRows=maxRows)
    
    if(len(ddd) <= 0 ):
        return ''    
    return ddd.to_html()


def UpdateDataFrameFromHTML(html, dff=None):

    vals = re.findall('<td.*?>(.*?)</td>',  html, flags=re.DOTALL|re.M|re.MULTILINE|re.IGNORECASE)
    idxs = re.findall('<th.*?>(.*?)</th>',  html, flags=re.DOTALL|re.M|re.MULTILINE|re.IGNORECASE)
    rows = re.findall('<tr.*?>(.*?)</tr>',  html, flags=re.DOTALL|re.M|re.MULTILINE|re.IGNORECASE)


    nRows = len(rows)
    nCols = int(len(vals)/nRows)
    
    #print ("===> Reshaping", nRows, nCols);
    vals = np.array(vals).reshape(nRows, nCols)

    #print( vals, len(vals), nCols, nRows)

    dft = pd.DataFrame(vals)
    dft.index = idxs
    if (dff is None ):
        return dft
    
    dft.columns= dff.columns;
    dft.index  = dft.index.astype(dff.index)

    for i,dt in enumerate(dft.dtypes):
        if ( dt != dff.dtypes[i]):
            dft[dft.columns[i]] = dft[dft.columns[i]].astype(dff.dtypes[i])

    for i, r in dft.iterrows():
        dff.loc[i:i,:] = dft.loc[i:i,:]

navigation_buttons_common = '''
<script>
jQuery.fn.reverse = [].reverse;

function UpdateTableShowRows( tab_maxRows, tab_maxDisp, tableID, out) {
    if(out.length <=10)
        return
        
    o = JSON.parse(out.slice(1, -1))
    // console.log("==>" + out );
    // console.log("==>VALS\\n " + o.vals );
    // console.log("==>IDXX " + o.idxs + " ++" + tableID);

    if (o.idxs.length <=0)
        return;

    var i=0;
    trs = '{0} tr'.format(tableID)
    $(trs).find('th:first').each(function ()
    {
        $(this).text( o.idxs[i++]);
    });
    i=o.vals.length-1;
    tds = '{0} td'.format(tableID)
    $(tds).reverse().each(function ()
    {
        $(this).text(o.vals[i--]);
    });
    
}

function TableShowRows( gg, tab_maxRows, tab_maxDisp, tableID, dataframeName ) {
    g = Number.parseInt(gg)
    if (isNaN(g) ){
        alert("hmmmm value: "+ gg + " make no sense" )
        return '';
    }
    var kernel = Jupyter.notebook.kernel;    
    command = "getHTMLTableRows({0}, startRow={1}, maxRows={2})".format(dataframeName, g, tab_maxDisp )
    cb = UpdateTableShowRows.bind(null, tab_maxRows, tab_maxDisp, tableID)
    gu.callPython( command, cb) ;
//    console.log("Executing Command: " + command );
}

function PrevPage(tab_maxRows, tab_maxDisp, tableID, dataframeName ){
    last = $(tableID).find('th:last').text()

    g = Number.parseInt(last)
    
    if (isNaN(g) ){
        alert("hmmmm value: "+ last + " is not Integer - Cannot Navigate!!" )
        return '';
    }
    
    topRow=g-tab_maxDisp
    if(topRow < 0){
        return;
    }
    startRow = g - 2*tab_maxDisp +2
    
    
    command = "getHTMLTableRows({0}, startRow={1}, maxRows={2})".format(dataframeName, startRow, tab_maxDisp )
    cb = UpdateTableShowRows.bind(null, tab_maxRows, tab_maxDisp, tableID)
    gu.callPython( command, cb) ;
//    console.log("Executing Command: " + command );

}
function NextPage(tab_maxRows, tab_maxDisp, tableID, dataframeName ){
    last = $(tableID).find('th:last').text()

    g = Number.parseInt(last)
    if (isNaN(g) ){
        alert("hmmmm value: "+ last + " is not Integer - Cannot Navigate!!" )
        return '';
    }
    if(g >= tab_maxRows-1){
        return
    }
    command = "getHTMLTableRows({0}, startRow={1}, maxRows={2})".format(dataframeName, g , tab_maxDisp )
    cb = UpdateTableShowRows.bind(null, tab_maxRows, tab_maxDisp, tableID)
    gu.callPython( command, cb) ;
//    console.log("Executing Command: " + command );
}

function SaveDataFrameFromHTML(tableID, dataFrameVariable){
    ret = $(tableID).html()
    s = ret.indexOf('</thead>')
    if ( s< 0 ) return;
    s1 = ret.substr(s+10)
    ret = s1.replace(/\\n/g, '');
    //console.log(s, ret)
    cmd = "UpdateDataFrameFromHTML(r\'\'\'{0}\'\'\', {1})".format(ret,dataFrameVariable);
    gu.callPython(cmd)
}

function ShowSearchResults(resultsDIV, html){
    //console.log("===>GOT:" + html)
    html = html.trim()
    if ( html.startsWith("'") && html.endsWith("'") ){
        html = html.slice(1, -1);
    }
    $(resultsDIV).html("Search Results:<br/>" + html)
}
function SearchDataFrame(dataFrameVariable, tableID, tab_maxDisp){
    v1 = tableID +'_search'
    v2 = tableID +'_searchResults'
    
    
    s = $(v1).val()
    if (s.length <=0) {
        $(v2).html('')
        $(v2).css('')
        return
    }
    cb  = ShowSearchResults.bind(null, v2);
    cmd = "getHTMLTableRowsFromSearch({0}, searchString='{1}', maxRows={2})".format(dataFrameVariable,s, tab_maxDisp);
    //console.log(cmd)
    gu.callPython(cmd, cb)
}
</script>
'''

navigation_buttons = '''
<div style="display:block;height:20px">
<input type=button value='GO>>' onclick="TableShowRows( $('#<TABLE_ID>_goto').val(), NUMROWS, MAXDISP, '#<TABLE_ID>', 'DFF_PY_VAR_<TABLE_ID>' );">
<input id='<TABLE_ID>_goto' type=text value='9'  size=4 >
<input type=button value=' << ' onclick="PrevPage( NUMROWS, MAXDISP, '#<TABLE_ID>', 'DFF_PY_VAR_<TABLE_ID>' );">
<input type=button value=' >> ' onclick="NextPage( NUMROWS, MAXDISP, '#<TABLE_ID>', 'DFF_PY_VAR_<TABLE_ID>' );">

<input type=button value='Save' onclick="SaveDataFrameFromHTML('#<TABLE_ID>', 'DFF_PY_VAR_<TABLE_ID>');">
<input type=button value='Search >>' onclick="SearchDataFrame('DFF_PY_VAR_<TABLE_ID>', '#<TABLE_ID>', MAXDISP);">
<input id='<TABLE_ID>_search' type=text value=''" size=10>
</div>
''';

def displayDFs(dfs, maxrows = 6, startrow=0, showTypes = True, showIcons=True, tableID=None, showNav= True,
               search=None, cols=[],  showStats = False, editable=True, useMyStyle=True, donotDisplay=False ):
                   
    if ( type(dfs) !=list and type(dfs) != tuple):
        dfs = [dfs];
        
    otr = "<table style='vertical-align: top;'>" if (len(dfs) >1) else "<table wwidth=100% style='vertical-align: top;'><tr>"
    bg1="#ffffff";
    bg2="lightblue";
    bg = bg2;
    for i, nd in enumerate(dfs):
        if ( nd is None  ):
            otr += "<td> None</td><td>&nbsp;</td>"
            continue;
            
        bg = bg2 if ( bg == bg1 ) else bg1;
        dim = str(nd.shape[0]) + " rows x " + str(nd.shape[1]) + " columns";
        
        if(search):
            d =searchDF(nd,search,cols);
        else:
            if( startrow+maxrows > len(nd) ):
                d = nd[-maxrows:] 
            else:
                d = nd[startrow:startrow+maxrows] 
            
        if (showTypes):
            cols=colTypesDF(d);
            d.columns = cols
        h = d.to_html();
        #
        if(len(dfs) == 1):
            h = h.replace("<table ", "<table wwidth=100% ")
        #
        if (editable):
            h = h.replace("<td", "<td contenteditable ")
        #
        if (useMyStyle):
            h = h.replace("class='dataframe'", "class='ourTableStyle' ")
            h = h.replace('class="dataframe"', "class='ourTableStyle' ")
            h = h.replace('<table ', "<table cellpadding=0 cellspacing=0 ")
            #h = h.replace("border=", "border=")
        
            
        
        shIcons = showIcons; 
        if ( type(showIcons) ==list and type(showIcons) != tuple):
            shIcons = showIcons[i];

        if (shIcons and nd.shape[0] > 0):
            h = getIcons(nd,h);
        if (showStats and nd.shape[0] > 0):
            h = addDescribe(nd,h);
        
            
        if(showNav):
            if(tableID is None or len(dfs) > 1):
                dttm = str(int(datetime.datetime.now().timestamp()*1000) )
                tableID = "tableID_" + dttm 
                
                h = h.replace("<table ", "<table id='{}' ".format(tableID) )

            inspect.stack()[1][0].f_globals['DFF_PY_VAR_'+tableID] = nd

            op = '''<div id='tab_<TABLE_ID>' style='ddisplay:none;width:100%' >
            {}
            <div id='<TABLE_ID>_searchResults'></div>
            </div>'''.format(h + navigation_buttons)
            op = op.replace("<TABLE_ID>", tableID).replace('NUMROWS', str(len(nd))).replace('MAXDISP', str(maxrows) )
            h = op
        else:
            if(tableID):
                h = h.replace("<table ", "<table id='{}' ".format(tableID) )

    
        
        tabSep = "<td>&nbsp;</td>" if len(dfs) > 1 else "";
        otr += "<td style='text-align:left;' bgcolor=" + bg + ">" + dim + "<br>\n" + h + "</td>{}".format(tabSep)
    otr += "</tr></table>"
    if (not donotDisplay):
        display(HTML(otr))
        
    if (showNav):
        otr = otr +  navigation_buttons_common;
    return otr



