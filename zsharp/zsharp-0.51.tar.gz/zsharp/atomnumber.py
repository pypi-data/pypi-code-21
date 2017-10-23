# Converting the raw image to column density map

## Housekeeping
import numpy as np
import os.path
import urllib.request
import numba
import pickle
import therpy as tp

# Load pre-compiled data
p_ = tp.getpath('Projects','Data','LookupTable','Lookup_Table_Fast_PreCompData_V2.p')
if not os.path.isfile(p_):
    print("Downloading Database -- Might take some time!")
    url = "https://www.dropbox.com/s/4hklnvawtshjay9/Lookup_Table_Fast_PreCompData_V2.p?dl=1"
    u = urllib.request.urlopen(url)
    data = u.read()
    u.close()
    # Create folder
    os.makedirs(os.path.split(p_)[0], exist_ok=True)
    with open(p_, "wb") as f :
        f.write(data)
precompiled_data_Lookup_Table = pickle.load( open( p_, "rb" ) )
#precompiled_data_Lookup_TableZ=precompiled_data_Lookup_Table
#for i in range(0,len(precompiled_data_Lookup_Table)):
#    u_siZ=precompiled_data_Lookup_Table[i][0]
#    sf_2dZ=precompiled_data_Lookup_Table[i][1]
#    si_2dZ=u_siZ;
#    for j in range(0,sf_2dZ.shape[1]-1):
#        si_2dZ=np.vstack((si_2dZ,u_siZ))
#    si_2dZ=np.transpose(si_2dZ)
#    precompiled_data_Lookup_TableZ[i]=list(precompiled_data_Lookup_TableZ[i])
#    precompiled_data_Lookup_TableZ[i][0]=si_2dZ



def atom_number(img,pixelsize,sigma,Nsat):
    #img: the raw imgage
    #pixelsize, the actual pixel size of the image (on the atoms), the unit should be kept same as cross section
    #sigma: absorption cross section of the atom
    #Nsat: saturation count.
    with np.errstate(all='ignore'):
        if img.shape[0]>=3:
            OD=np.real(-np.log((img[0,:,:]-img[2,:,:])/(img[1,:,:]-img[2,:,:])));
        else:
            OD=np.real(-np.log((img[0,:,:])/(img[1,:,:])));
        IC=(img[0,:,:]-img[1,:,:])/Nsat;
        nimg=(OD+IC)*pixelsize/sigma;
    return nimg

def clean_image(img):
# replace the inf and nan in the image by the mean of the nearby matrix elements

    imgout=img
    yrange=img.shape[0];xrange=img.shape[1];
    x,y=np.meshgrid(range(0,xrange),range(0,yrange))
    
    img_array=imgout.flatten();
    x_array=x.flatten();
    y_array=y.flatten();
    
    xabnormal_list=x_array[np.isnan(img_array)];
    xabnormal_list=np.concatenate((xabnormal_list,x_array[np.isinf(img_array)]))
    
    yabnormal_list=y_array[np.isnan(img_array)];
    yabnormal_list=np.concatenate((yabnormal_list,y_array[np.isinf(img_array)]))
    
    for i in range(0,np.size(xabnormal_list)):
        xi=xabnormal_list[i];
        yi=yabnormal_list[i];
        mask=(np.abs(x_array-xi)+np.abs(y_array-yi))<2;
        
        neighbors=img_array[mask];
        neighbors=neighbors[(~np.isnan(neighbors)) & (~np.isinf(neighbors))];
        r=0;
        with np.errstate(all='ignore'):
            if len(neighbors>0):
                r=np.mean(neighbors)
        if np.isnan(r):
            r=0;
        imgout[yi,xi]=r
    return imgout

@numba.jit(nopython=True)
def interp_od_special_jit(IivIn, IfvIn, sim_data):
    # Unload sim_data
    u_si, sf_2d, ocd_2d = sim_data[0], sim_data[1], sim_data[2]
    rows, cols = sf_2d.shape[0], sf_2d.shape[1]
    # Copy inputs and flatten the arrays
    Iiv = IivIn.copy().flatten()  # Flatten so that we can do 1d loop
    Ifv = IfvIn.copy().flatten()  # We will unflatten the arrays when returning
    # Fix low and high OD regions
    bad_low = (Iiv < Ifv)  # For low od (BG), flip Ii and If and make od -> -od
    Iiv[bad_low], Ifv[bad_low] = Ifv[bad_low].copy(), Iiv[bad_low].copy()
    bad_high = (Ifv < 0)   # For high od where If < 0, make If -> -If
    Ifv = np.abs(Ifv)
    # Prepare
    i0v = np.searchsorted(u_si, Iiv)   # Find the indice for closest si
    Pfv = np.zeros_like(Iiv) * np.nan  # Prepare output array, default it with nan
    # Interpolate OD's
    for i in range(Iiv.size):
        Ii, If, i0 = Iiv[i], Ifv[i], i0v[i]
        # Search 4 closest points
        if i0 >= rows or i0 == 0: continue  # If Ii is outside simulation, result is nan
        i1 = np.searchsorted(sf_2d[i0-1,:], If)
        if i1 >= cols: Pfv[i] = 0; continue # If If > max(sf), result is zero atoms
        elif i1 == 0: continue
        i2 = np.searchsorted(sf_2d[i0,:], If)
        if i2 >= cols: Pfv[i] = 0; continue # If If > max(sf), result is zero atoms
        elif i2 == 0: continue
        i0m1 = i0-1
        x1 = u_si[i0m1]
        x2 = u_si[i0]
        dx = x2 - x1
        dx2 = dx**2
        Ary = sf_2d[i0m1, i1-1]
        Bry = sf_2d[i0, i2-1]
        Cry = sf_2d[i0m1, i1]
        Dry = sf_2d[i0, i2]
        Af = ocd_2d[i0m1, i1-1]
        Bf = ocd_2d[i0, i2-1]
        Cf = ocd_2d[i0m1, i1]
        Df = ocd_2d[i0, i2]
        # Interpolate with 4 nearest points
        s = (Ii - x1) / (dx)
        Erx = x1 + (dx) * s
        Ery = Ary + (Bry - Ary) * s
        Frx = x1 + (dx) * s
        Fry = Cry + (Dry - Cry) * s
        Ef = Af + (Bf - Af)  * (((Erx - x1)**2 + (Ery - Ary)**2) / ((dx2 + (Bry - Ary)**2)))**0.5
        Ff = Cf + (Df - Cf)  * (((Frx - x1)**2 + (Fry - Cry)**2) / ((dx2 + (Dry - Cry)**2)))**0.5
        Pfv[i] = Ef + (Ff - Ef) * (((Ii - Erx)**2 + (If - Ery)**2) / (((Frx - Erx)**2 + (Fry - Ery)**2)) )**0.5
    # Make the bad_low od -> -od
    Pfv[bad_low] *= -1
    # Reshape and return
    return Pfv.reshape(*IivIn.shape)


def atom_number_lut(img,pixelsize,sigma, Nsat,time):
    # calculate the atom number per pixel with the look up table.
    WA=(img[0,:,:]-img[2,:,:,])/Nsat;
    WOA=(img[1,:,:]-img[2,:,:,])/Nsat;
    ODtemp=interp_od_special_jit(WOA, WA, precompiled_data_Lookup_Table[time-1])
    Nimg=ODtemp/sigma*pixelsize;
    
    return Nimg