# CEE262F_OceanWaves
Repository for initiation to wave-resolving modeling (SWASH) in CEE262F Ocean waves lecture by C. Baker at Stanford.

# How to run SWASH

## With Docker (recommended)
1. Follow instructions in https://hub.docker.com/r/delftwaves/swash, to install Docker.
2. Run ```docker run --rm -v .:/home/swash delftwaves/swash swashrun -input <SWASH input>```

## On FarmShare
1. TBD

# How to read SWASH output

## With xarray
1. Clone ```swash_pp```(credits: Renan Fonseca da Silva) with ```git clone https://github.com/SimonTreillou/swash_pp.git```
2. Load SWASH output with:
```
import numpy as np 
import matplotlib.pyplot as plt
import sys
sys.path.append('your/path/to/swash_pp/src')
from swash_pp import swash_mat2nc as snc
ds=snc.mat2nc(path_run="./",run_file="input.sws")
```
