
# [[file:~/Research/CFEDemands/Empirics/cfe_estimation.org::*Utility%20Functions][df_utils]]

# Tangled on Mon Oct 30 16:39:40 2017
import numpy as np
from scipy import sparse
import pandas as pd

def df_norm(a,b=None,ignore_nan=True,ord=None):
    """
    Provides a norm for numeric pd.DataFrames, which may have missing data.

    If a single pd.DataFrame is provided, then any missing values are replaced with zeros, 
    the norm of the resulting matrix is returned.

    If an optional second dataframe is provided, then missing values are similarly replaced, 
    and the norm of the difference is replaced.

    Other optional arguments:

     - ignore_nan :: If False, missing values are *not* replaced.
     - ord :: Order of the matrix norm; see documentation for numpy.linalg.norm.  
              Default is the Froebenius norm.
    """
    a=a.copy()
    if not b is None:
      b=b.copy()
    else:
      b=pd.DataFrame(np.zeros(a.shape),columns=a.columns,index=a.index)

    if ignore_nan:
        missing=(a.isnull()+0.).replace([1],[np.NaN]) +  (b.isnull()+0.).replace([1],[np.NaN]) 
        a=a+missing
        b=b+missing
    return np.linalg.norm(a.fillna(0).as_matrix() - b.fillna(0).as_matrix())

def df_to_orgtbl(df,tdf=None,sedf=None,conf_ints=None,float_fmt='%5.3f'):
    """
    Returns a pd.DataFrame in format which forms an org-table in an emacs buffer.
    Note that headers for code block should include ":results table raw".

    Optional inputs include conf_ints, a pair (lowerdf,upperdf).  If supplied, 
    confidence intervals will be printed in brackets below the point estimate.

    If conf_ints is /not/ supplied but sedf is, then standard errors will be 
    in parentheses below the point estimate.

    If tdf is False and sedf is supplied then stars will decorate significant point estimates.
    If tdf is a df of t-statistics stars will decorate significant point estimates.
    """
    if len(df.shape)==1: # We have a series?
       df=pd.DataFrame(df)

    if (tdf is None) and (sedf is None) and (conf_ints is None):
        s = '|  |'+'|   '.join([str(s) for s in df.columns])+'  |\n|-\n'
        for i in df.index:
            s+='| %s  ' % i
            for j in df.columns: # Point estimates
                entry='| \('+float_fmt+'\)  '
                if np.isnan(df[j][i]):
                    s+='| --- '
                else:
                    s+=entry % df[j][i]
            s+='|\n'
        return s
    elif not (tdf is None) and (sedf is None) and (conf_ints is None):
        s = '|  |'+'|   '.join([str(s) for s in df.columns])+'\t|\n|-\n'
        for i in df.index:
            s+='| %s  ' % i
            for j in df.columns:
                try:
                    stars=(np.abs(tdf[j][i])>1.65) + 0.
                    stars+=(np.abs(tdf[j][i])>1.96) + 0.
                    stars+=(np.abs(tdf[j][i])>2.577) + 0.
                    stars = int(stars)
                    if stars>0:
                        stars='^{'+'*'*stars + '}'
                    else: stars=''
                except KeyError: stars=''
                entry='| \('+float_fmt+stars+'\) '
                if np.isnan(df[j][i]):
                    s+='| --- '
                else:
                    s+=entry % df[j][i]
            s+='|\n'

        return s
    elif not (sedf is None) and (conf_ints is None): # Print standard errors on alternate rows
        if tdf is not False:
            try: # Passed in dataframe?
                tdf.shape
            except AttributeError:  
                tdf=df[sedf.columns]/sedf
        s = '|  |'+'|   '.join([str(s) for s in df.columns])+'  |\n|-\n'
        for i in df.index:
            s+='| %s  ' % i
            for j in df.columns: # Point estimates
                if tdf is not False:
                    try:
                        stars=(np.abs(tdf[j][i])>1.65) + 0.
                        stars+=(np.abs(tdf[j][i])>1.96) + 0.
                        stars+=(np.abs(tdf[j][i])>2.577) + 0.
                        stars = int(stars)
                        if stars>0:
                            stars='^{'+'*'*stars + '}'
                        else: stars=''
                    except KeyError: stars=''
                else: stars=''
                entry='| \('+float_fmt+stars+'\)  '
                if np.isnan(df[j][i]):
                    s+='| --- '
                else:
                    s+=entry % df[j][i]
            s+='|\n|'
            for j in df.columns: # Now standard errors
                s+='  '
                try:
                    if np.isnan(df[j][i]): # Pt estimate miss
                        se=''
                    elif np.isnan(sedf[j][i]):
                        se='(---)'
                    else:
                        se='\((' + float_fmt % sedf[j][i] + ')\)' 
                except KeyError: se=''
                entry='| '+se+'  '
                s+=entry 
            s+='|\n'
        return s
    elif not (conf_ints is None): # Print confidence intervals on alternate rows
        if tdf is not False and sedf is not None:
            try: # Passed in dataframe?
                tdf.shape
            except AttributeError:  
                tdf=df[sedf.columns]/sedf
        s = '|  |'+'|   '.join([str(s) for s in df.columns])+'  |\n|-\n'
        for i in df.index:
            s+='| %s  ' % i
            for j in df.columns: # Point estimates
                if tdf is not False and tdf is not None:
                    try:
                        stars=(np.abs(tdf[j][i])>1.65) + 0.
                        stars+=(np.abs(tdf[j][i])>1.96) + 0.
                        stars+=(np.abs(tdf[j][i])>2.577) + 0.
                        stars = int(stars)
                        if stars>0:
                            stars='^{'+'*'*stars + '}'
                        else: stars=''
                    except KeyError: stars=''
                else: stars=''
                entry='| \('+float_fmt+stars+'\) '
                if np.isnan(df[j][i]):
                    s+='| --- '
                else:
                    s+=entry % df[j][i]
            s+='|\n|'
            for j in df.columns: # Now confidence intervals
                s+='  '
                try:
                    ci='\([' + float_fmt +','+ float_fmt + ']\)'
                    ci= ci % (conf_ints[0][j][i],conf_ints[1][j][i])
                except KeyError: ci=''
                entry='| '+ci+'  '
                s+=entry 
            s+='|\n'
        return s

def orgtbl_to_df(table, col_name_size=1, format_string=None, index=None):
  """
  Returns a pandas dataframe.
  Requires the use of the header `:colnames no` for preservation of original column names.
  `table` is an org table which is just a list of lists in python.
  `col_name_size` is the number of rows that make up the column names.
  `format_string` is a format string to make the desired column names.
  `index` is a column label or a list of column labels to be set as the index of the dataframe.
  """
  import pandas as pd

  if col_name_size==0:
    return pd.DataFrame(table)
 
  colnames = table[:col_name_size]

  if col_name_size==1:
    if format_string:
      new_colnames = [format_string % x for x in colnames[0]]
    else:
      new_colnames = colnames[0]
  else:
    new_colnames = []
    for colnum in range(len(colnames[0])):
      curr_tuple = tuple([x[colnum] for x in colnames])
      if format_string:
        new_colnames.append(format_string % curr_tuple)
      else:
        new_colnames.append(str(curr_tuple))

  df = pd.DataFrame(table[col_name_size:], columns=new_colnames)
 
  if index:
    df.set_index(index, inplace=True)

  return df

def balance_panel(df):
    """Drop households that aren't observed in all rounds."""
    pnl=df.to_panel()
    keep=pnl.loc[list(pnl.items)[0],:,:].dropna(how='any',axis=1).iloc[0,:]
    df=pnl.loc[:,:,keep.index].to_frame(filter_observations=False)
    df.index.names=pd.core.base.FrozenList(['Year','HH'])

    return df

def drop_missing(X):
    """
    Return tuple of pd.DataFrames in X with any 
    missing observations dropped.  Assumes common index.
    """

    foo=pd.concat(X,axis=1).dropna(how='any')
    assert len(set(foo.columns))==len(foo.columns) # Column names must be unique!

    Y=[]
    for x in X:
        Y.append(foo.loc[:,pd.DataFrame(x).columns]) 

    return tuple(Y)

def use_indices(df,idxnames):
    return df.reset_index()[idxnames].set_index(df.index)

# df_utils ends here

# [[file:~/Research/CFEDemands/Empirics/cfe_estimation.org::*Some%20econometric%20routines][Some\ econometric\ routines:1]]

# Tangled on Mon Oct 30 16:39:40 2017

def arellano_robust_cov(X,u,clusterby=['t','mkt']):
    X,u = drop_missing([X,u])
    clusters = set(zip(*tuple(use_indices(u,clusterby)[i] for i in clusterby)))
    if  len(clusters)>1:
        # Take out time averages
        u = u - u.groupby(level=clusterby).transform(np.mean)
        X = X - X.groupby(level=clusterby).transform(np.mean)
        #u=broadcast_binary_op(u,lambda x,y:x-y, u.groupby(level=clusterby).mean()).squeeze()
        #X=broadcast_binary_op(X,lambda x,y:x-y, X.groupby(level=clusterby).mean()) 
        Xu=X.mul(u.squeeze(),axis=0)
        if len(X.shape)==1:
            XXinv=np.array([1./(X.T.dot(X))])
        else:
            XXinv=np.linalg.inv(X.T.dot(X))
        Vhat = XXinv.dot(Xu.T.dot(Xu)).dot(XXinv)
    else:
        u=(u-u.mean()).squeeze()
        X=X-X.mean()

        Xu=X.mul(u,axis=0)
        if len(X.shape)==1:
            XXinv=np.array([1./(X.T.dot(X))])
        else:
            XXinv=np.linalg.inv(X.T.dot(X))
        Vhat = XXinv.dot(Xu.T.dot(Xu)).dot(XXinv)

    try:
        return pd.DataFrame(Vhat,index=X.columns,columns=X.columns)
    except AttributeError:
        return Vhat


def ols(x,y,return_se=True,return_v=False,return_e=False):

    x=pd.DataFrame(x) # Deal with possibility that x & y are series.
    y=pd.DataFrame(y)
    # Drop any observations that have missing data in *either* x or y.
    x,y = drop_missing([x,y]) 

    N,n=y.shape
    k=x.shape[1]

    b=np.linalg.lstsq(x,y)[0]

    b=pd.DataFrame(b,index=x.columns,columns=y.columns)

    out=[b.T]
    if return_se or return_v or return_e:

        u=y-x.dot(b)

        # Use SUR structure if multiple equations; otherwise OLS.
        # Only using diagonal of this, for reasons related to memory.  
        S=sparse.dia_matrix((sparse.kron(u.T.dot(u),sparse.eye(N)).diagonal(),[0]),shape=(N*n,)*2) 

        if return_se or return_v:

            # This will be a very large matrix!  Use sparse types
            V=sparse.kron(sparse.eye(n),(x.T.dot(x).dot(x.T)).as_matrix().view(type=np.matrix).I).T
            V=V.dot(S).dot(V.T)

        if return_se:
            se=np.sqrt(V.diagonal()).reshape((x.shape[1],y.shape[1]))
            se=pd.DataFrame(se,index=x.columns,columns=y.columns)

            out.append(se)
        if return_v:
            # Extract blocks along diagonal; return an Nxkxn array
            V={y.columns[i]:pd.DataFrame(V[i*k:(i+1)*k,i*k:(i+1)*k],index=x.columns,columns=x.columns) for i in range(n)} 
            out.append(V)
        if return_e:
            out.append(u)
    return tuple(out)

# Some\ econometric\ routines:1 ends here

# [[file:~/Research/CFEDemands/Empirics/cfe_estimation.org::*Utility%20functions%20for%20dealing%20with%20some%20awkward%20multiindex%20issues][broadcast_binary_op]]

# Tangled on Mon Oct 30 16:39:40 2017
def merge_multi(df1, df2, on):
    """Merge on subset of multiindex.
   
    Idea due to http://stackoverflow.com/questions/23937433/efficiently-joining-two-dataframes-based-on-multiple-levels-of-a-multiindex
    """
    return df1.reset_index().join(df2,on=on).set_index(df1.index.names)

def broadcast_binary_op(x, op, y):
    """Perform x op y, allowing for broadcasting over a multiindex.

    Example usage: broadcast_binary_op(x,lambda x,y: x*y ,y)
    """
    x = pd.DataFrame(x.copy())
    y = pd.DataFrame(y.copy())
    xix= x.index.copy()

    if y.shape[1]==1: # If y a series, expand to match x.
        y=pd.DataFrame([y.iloc[:,0]]*x.shape[1],index=x.columns).T

    cols = list(x.columns)
    xindex = list(x.index.names)
    yindex = list(y.index.names)

    dif = list(set(xindex)-set(yindex))

    z = pd.DataFrame(index=xix)
    z = merge_multi(z,y,on=yindex)

    newdf = op(x[cols],z[cols])

    return newdf

# broadcast_binary_op ends here
