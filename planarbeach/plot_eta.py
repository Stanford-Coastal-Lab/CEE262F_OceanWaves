#!/usr/bin/env python3
"""
plot_eta.py — 2DH planar beach
Top-down view of instantaneous free surface η(x, y) at chosen time.

Reads:
    wlev.txt  — merged SWASH BLOCK ASCII output (run merge_output.py first)
                flat array: n_times × NY × NX values, 6 per line
"""
#%%
import numpy as np
import matplotlib.pyplot as plt

# ── params (match input.sws) ────────────────────────────────────────────
T_PLOT   = 500.0
T_START  = 100.0
DT_OUT   = 5.0
MXC, MYC = 220, 284
XLENC, YLENC = 220., 284.
ETA_MAX  = 1.0           # colour-scale half-range [m]

NX = MXC + 1             # 1001 nodes
NY = MYC + 1             # 51 nodes
x  = np.linspace(0., XLENC, NX)
y  = np.linspace(0., YLENC, NY)

# ── helper: read SWASH BLOCK ASCII (any number of values per line) ──────
def read_block(path):
    with open(path) as f:
        return np.fromstring(f.read(), sep=' ')

# ── read wlev.txt ────────────────────────────────────────────────────────
vals    = read_block("wlev.txt")          # flat 1-D: n_times × NY × NX
n_times = len(vals) // (NY * NX)
wlev    = vals.reshape(n_times, NY, NX)  # (n_times, NY, NX)
times   = T_START + np.arange(n_times) * DT_OUT

it   = int(np.argmin(np.abs(times - T_PLOT)))
tnow = times[it]
eta  = wlev[it]                          # (NY, NX)

print(f"wlev   : {wlev.shape}   (n_times={n_times}, NY={NY}, NX={NX})")
print(f"t range: {times[0]:.0f} – {times[-1]:.0f} s")
print(f"plotting η at t = {tnow:.1f} s   (index {it})")

#%% PLOTTING
fig, ax = plt.subplots(figsize=(10,6), dpi=300)

pcm = ax.pcolormesh(x, y, eta, cmap="RdBu_r",
                    vmin=-ETA_MAX, vmax=ETA_MAX, shading="auto")
fig.colorbar(pcm, ax=ax, label="η  [m]")

ax.set_xlabel("x  (cross-shore)  [m]")
ax.set_ylabel("y  (alongshore)   [m]")
ax.set_title(rf"$\eta(x,y)$  at  $t$ = {tnow:.0f} s", loc="left")
ax.set_xlim(0., XLENC)
ax.set_ylim(0., YLENC)

fig.tight_layout()
fname = f"eta2D_t{int(round(tnow)):04d}.png"
fig.savefig(fname, dpi=130)
print(f"wrote {fname}")
plt.show()
# %%
