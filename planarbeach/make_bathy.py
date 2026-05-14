#!/usr/bin/env python3
"""
make_bathy.py — 2DH bathymetry for the oblique-wave longshore-current case.

Same planar 1/50 slope as the 1D case, replicated alongshore.

Domain     : 600 m (cross-shore) x 200 m (alongshore)
Grid       : dx = 2 m, dy = 2 m → (mxc, myc) = (300, 100) in SWASH
Shoreline  : at x = 500 m

Writes bot.txt with shape (myinp+1, mxinp+1) = (101, 301), one row per y-line,
in free format — ready for READINP BOTTOM with idla = 4.
"""
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------------- params
H0     = 10.0      # offshore depth                          [m]
SLOPE  = 1./50.    # cross-shore slope                       [-]
L_DOM  = 600.0     # cross-shore length                      [m]
W_DOM  = 200.0     # alongshore width                        [m]
DX     = 2.0       # cross-shore grid spacing                [m]
DY     = 2.0       # alongshore grid spacing                 [m]
X_SHR  = H0 / SLOPE                # shoreline at 500 m for these settings
H_DRY  = -1.0      # plateau bottom level on dry beach       [m]

# ---------------------------------------------------------------- grid
x = np.arange(0., L_DOM + 0.5*DX, DX)              # 601 nodes
y = np.arange(0., W_DOM + 0.5*DY, DY)              # 101 nodes

# 1D cross-shore profile (positive downward)
zb_1d = np.where(x <= X_SHR,
                 H0 - SLOPE * x,
                 np.maximum(H_DRY, H0 - SLOPE * x))

# Replicate alongshore — bathymetry is y-uniform
zb_2d = np.tile(zb_1d, (y.size, 1))                # shape (ny, nx)

# ---------------------------------------------------------------- write
np.savetxt("bot.txt", zb_2d, fmt="%8.4f")
print(f"wrote bot.txt — {zb_2d.shape[0]} rows × {zb_2d.shape[1]} cols, "
      f"z_b ∈ [{zb_2d.min():.2f}, {zb_2d.max():.2f}] m")

# ---------------------------------------------------------------- plot
fig, ax = plt.subplots(figsize=(11, 4.5))
pcm = ax.pcolormesh(x, y, -zb_2d, cmap="Blues", shading="auto",
                    vmin=-H0-1, vmax=2)
ax.contour(x, y, zb_2d, levels=[0.], colors="#E76F51",
           linewidths=1.4, linestyles="--")
ax.text(X_SHR + 4, W_DOM*0.05, "shoreline",
        color="#E76F51", fontsize=10, style="italic")
ax.set_xlabel("x  (cross-shore)  [m]")
ax.set_ylabel("y  (alongshore)   [m]")
ax.set_title(f"2DH bathymetry — planar slope {int(1/SLOPE)}:1, "
             f"y-uniform, periodic in y")
ax.set_aspect("equal")
cb = fig.colorbar(pcm, ax=ax, label="z  [m]   (negative = below SWL)")
fig.tight_layout()
fig.savefig("bathy.png", dpi=130)
print("wrote bathy.png")
