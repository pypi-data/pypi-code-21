#!/usr/bin/env python
"""
======================
Basic Analysis Example
======================

"""
# # Example Analysis on Some Randomly Picked Data
# *Using the KM3NeT HDF5 format and Python*
# 
# Author: Tamás Gál <tgal@km3net.de>
# 
# Date: 2017-10-10
# 
# Status: Under construction...

# ## Preparation

# The very first thing we do is importing our libraries and setting up the Jupyter Notebook environment.

# In[1]:


# displays graphs below the cells
get_ipython().magic('matplotlib inline')

import matplotlib.pyplot as plt   # our plotting module
import pandas as pd               # the main HDF5 reader
import numpy as np                # must have
import km3pipe as kp              # some KM3NeT related helper functions

# this is just to make our plots a bit "nicer", you can skip it
import km3pipe.style
km3pipe.style.use("km3pipe")


# ## Accessing the Data File(s)

# In the following, we will work with one random simulation file with reconstruction information from JGandalf which has been converted from ROOT to HDF5 using the ``tohdf5`` command line tool provided by ``KM3Pipe``.
# 
# You can find the documentation here: http://km3pipe.readthedocs.io/en/latest/cmd.html#tohdf
# 
# 

# ### Note for Lyon Users
# If you are working on the Lyon cluster, you can activate the latest KM3Pipe with the following command (put it in your ``~/.bashrc`` to load it automatically in each shell session)::
# 
#     source /afs/in2p3.fr/throng/km3net/src/python/pyenv.sh

# ### Converting from ROOT to HDF5 (if needed)
# 
# Choose a file (take e.g. one from /in2p3/km3net/mc/atm_neutrino/KM3NeT_ORCA_115_23m_9m/v1.1.1/JGandalf/aanet/) load the appropriate Jpp/Aanet version and convert it via::
# 
#     tohdf5 --aa-format=the_file.root --ignore-hits --skip-header
#     
# Note that you may have to ``--skip-header`` otherwise you might encounter some segfaults. There is currently a big mess of different versions of libraries in several levels of the MC file processings.
# 
# The ``--ignore-hits`` will skip the hit information, so the converted file is much smaller (normally around 2-3 MBytes). Skip this option if you want to read the hit information too. The file will still be smaller than the ROOT file (about 1/3).
# 
# Luckily, a handful people are preparing the HDF5 conversion, so in future you can download them directly, without thinking about which Jpp or Aanet version you need to open them.

# ## First Look at the Data

# In[2]:


filepath = "/Users/tamasgal/Data/KM3NeT/ORCA/JGandalf_aanet_muon-CC_3-100GeV_23.root.h5"


# We can have a quick look at the file with the ``ptdump`` command in the terminal::
# 
#     ptdump /Users/tamasgal/Data/KM3NeT/ORCA/JGandalf_aanet_muon-CC_3-100GeV_23.root.h5
#     
# For further information, check out the documentation of the KM3NeT HDF5 format definition: http://km3pipe.readthedocs.io/en/latest/hdf5.html

# In[3]:


get_ipython().system('ptdump /Users/tamasgal/Data/KM3NeT/ORCA/JGandalf_aanet_muon-CC_3-100GeV_23.root.h5')


# The ``/event_info`` table contains general information about each event. The data is a simple 2D table and each event is represented by a single row.
# 
# Let's have a look at the first few rows:

# In[4]:


event_info = pd.read_hdf(filepath, '/event_info')
event_info.head(5)


# Next, we will read out the MC tracks which are stored under ``/mc_tracks``.

# In[5]:


tracks = pd.read_hdf(filepath, '/mc_tracks')


# It has a similar structure, but now you can have multiple rows which belong to an event. The ``event_id`` column holds the ID of the corresponding event.

# In[6]:


tracks.head(10)


# We now are accessing the first track for each event by grouping via ``event_id`` and calling the ``first()`` method of the ``Pandas.DataFrame`` object.

# In[7]:


primaries = tracks.groupby('event_id').first()


# In[8]:


primaries.head(5)


# ## Creating some Fancy Graphs

# In[9]:


plt.hist(primaries.energy, bins=100, log=True)
plt.xlabel('energy [GeV]')
plt.ylabel('number of events')
plt.title('Energy Distribution');


# In[10]:


plt.hist(primaries.bjorkeny, bins=100)
plt.xlabel('bjorken-y')
plt.ylabel('number of events')
plt.title('bjorken-y Distribution');


# In[11]:


zeniths = kp.math.zenith(primaries.filter(regex='^dir_.?$'))
primaries['zenith'] = zeniths

plt.hist(np.cos(primaries.zenith), bins=21, histtype='step', linewidth=2)
plt.xlabel(r'cos($\theta$)')
plt.ylabel('number of events')
plt.title('Zenith Distribution');


# In[12]:


plt.hist2d(primaries.pos_x, primaries.pos_y, bins=100);
plt.xlabel('x [m]')
plt.ylabel('y [m]')
plt.title('2D Plane')
plt.colorbar();


# In[13]:


from mpl_toolkits.mplot3d import Axes3D
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter3D(primaries.pos_x, primaries.pos_y, primaries.pos_z, s=3)
ax.set_xlabel('x [m]', labelpad=10)
ax.set_ylabel('y [m]', labelpad=10)
ax.set_zlabel('z [m]', labelpad=10)
ax.set_title('3D Plane');


# In[14]:


gandalfs = pd.read_hdf(filepath, '/reco/gandalf')
gandalfs.head(5)


# In[15]:


gandalfs.columns


# In[16]:


plt.hist(gandalfs['lambda'], bins=50, log=True);
plt.xlabel('lambda parameter')
plt.ylabel('count')
plt.title('Lambda Distribution of Reconstructed Events');


# In[17]:


gandalfs['zenith'] = kp.math.zenith(gandalfs.filter(regex='^dir_.?$'))


# In[18]:


plt.hist((primaries.zenith - gandalfs.zenith).dropna(), bins=100)
plt.xlabel(r'true zenith - reconstructed zenith [rad]')
plt.ylabel('count')
plt.title('Zenith Reconstruction Difference');


# In[19]:


l = 5
lambda_cut = gandalfs['lambda'] < l
plt.hist((primaries.zenith - gandalfs.zenith)[lambda_cut].dropna(), bins=100)
plt.xlabel(r'true zenith - reconstructed zenith [rad]')
plt.ylabel('count')
plt.title('Zenith Reconstruction Difference for lambda < {}'.format(l));

