#%%
import numpy as np 
import matplotlib.pyplot as plt
import sys
sys.path.append('/Users/simon/Code/Packages/swash_pp/src')
from swash_pp import swash_mat2nc as snc
sys.path.append('/Users/simon/Code/CONFIGS/SurfzoneMixing/Paper')
sys.path.append('/Users/simon/Code/Projects/Tools')
from useful import *

vobs = get_data(paper="clark2010",metric='V',case="3")
# %% Load
ds=snc.mat2nc(path_run="/Users/simon/Code/CONFIGS/SurfzoneMixing/Prod/R3_SWASH/",run_file="input.sws")
x = ds[0]['x'].squeeze()
h=-ds[0]['Botlev'][0,:]
ix = np.argmin(np.abs(h.values+0.5))
x = x-x[ix]
# %% Plot in 2D
plt.plot(x,np.mean(ds[0]['Y-Mvel'],axis=0))
plt.scatter(vobs['x'],vobs['y'],color='k',label='Obs')
# %%
plt.plot(x,h)
# %%
plt.pcolor(ds[0]['X-Mvel'])
plt.colorbar()
# %%
