#!/usr/bin/env python3
"""
make_bathy.py
Generate planar-slope bathymetry for the SWASH 1D demo case.

Domain:
    x = 0  .....  500 m  ............  600 m
    │           │                       │
    │  slope 1/50                       │
    │  h = 10 m  → 0 m  →  -1 m (dry)   │
    │           │                       │
    offshore    shoreline (SWL)         end of beach

Convention (SWASH):
    bottom level z_b is depth below reference, positive downward.
    z_b > 0  ⇒  cell is under water at rest.
    z_b < 0  ⇒  cell is above reference (handled as dry by SWASH).

Outputs:
    bot.txt   — one row of 601 free-format values, ready for READINP BOTTOM
    bathy.png — sanity-check plot
"""
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------------- params
H0     = 10.0     # offshore still-water depth                   [m]
SLOPE  = 1./50.   # cross-shore bottom slope                     [-]
L_DOM  = 600.0    # cross-shore domain length                    [m]
DX     = 1.0      # grid spacing                                 [m]
X_SHR  = H0 / SLOPE         # shoreline (= 500 m for these settings)
H_DRY  = -1.0     # bottom level on dry land  (1 m above SWL)    [m]

# ---------------------------------------------------------------- grid
x  = np.arange(0., L_DOM + 0.5*DX, DX)                # 601 nodes
zb = np.where(x <= X_SHR,
              H0 - SLOPE * x,                          # under water
              np.maximum(H_DRY, H0 - SLOPE * x))       # beach plateau

# ---------------------------------------------------------------- write
# SWASH free format: one row per y-line. In 1D (myinp = 0) → single row.
np.savetxt("bot.txt", zb.reshape(1, -1), fmt="%8.4f")
print(f"wrote bot.txt  —  {zb.size} values,  z_b ∈ [{zb.min():.2f}, {zb.max():.2f}] m")

# ---------------------------------------------------------------- plot
fig, ax = plt.subplots(figsize=(9, 3.6))
eta = np.zeros_like(x)                                 # still water at z = 0
ax.fill_between(x, -zb, eta, where=eta > -zb,
                color="#1C7293", alpha=0.40, label="water")
ax.fill_between(x, -zb, -H0 - 1.5,
                color="#8C5A3C", alpha=0.65, label="bed")
ax.axhline(0., color="#065A82", lw=1.2, ls="--", label="still water level")
ax.axvline(X_SHR, color="#E76F51", lw=1.0, ls=":", alpha=0.7)
ax.text(X_SHR + 5, -H0 + 0.6, "shoreline", color="#E76F51", fontsize=9, style="italic")

ax.set_xlabel("x  [m]")
ax.set_ylabel("z  [m]")
ax.set_title(f"SWASH 1D demo bathymetry — planar slope {int(1/SLOPE)}:1")
ax.set_xlim(0., L_DOM)
ax.set_ylim(-(H0 + 1.5), 2.)
ax.legend(loc="upper right", frameon=False)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("bathy.png", dpi=130)
print("wrote bathy.png")
