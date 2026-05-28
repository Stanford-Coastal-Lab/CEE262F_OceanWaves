# CEE262F_OceanWaves
Repository for initiation to wave-resolving modeling (SWASH) in CEE262F Ocean waves lecture by C. Baker at Stanford.

# How to run SWASH

## With Docker (recommended)
1. Follow instructions in https://hub.docker.com/r/delftwaves/swash, to install Docker.
2. Run ```docker run --rm -v .:/home/swash delftwaves/swash swashrun -input <SWASH input> -mpi 4``` in the configuration directory you want to run (e.g. 2DV) (in most laptops 4 cores is working fine). Don't forget to create the bathymetry before if not present.

## On FarmShare
1. TBD

# How to create bathymetry

In 2DV directory, just run ```python3 make_bathy.py```in your terminal.

# How to read SWASH output

You can see instantaneous free surface and velocities using ```python3 plot_eta.py``` or ```python3 plot_u.py```. 

