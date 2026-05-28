#!/usr/bin/env python3
"""
plot_longshorecurrent.py — 2DH planar beach
Cross-shore view of time-averaged longshore current v(x, y) at chosen time.

Reads:
    vel.txt   — merged SWASH BLOCK ASCII output (run merge_output.py first)
                flat array: n_times × 2 × NY × NX values, 6 per line
                var 0 = cross-shore velocity u  [m/s]
                var 1 = along-shore  velocity v  [m/s]
    wlev.txt  — for water level overlay (same format, 1 var)
"""
#%%
import numpy as np
import matplotlib.pyplot as plt

# ── params (match input.sws) ────────────────────────────────────────────
T_START  = 100.0
DT_OUT   = 5.0
MXC, MYC = 220, 284
XLENC, YLENC = 220., 284.
V_MAX    = 0.5            # colour-scale half-range [m/s]

NX = MXC + 1
NY = MYC + 1
x  = np.linspace(0., XLENC, NX)
y  = np.linspace(0., YLENC, NY)

# ── helper ───────────────────────────────────────────────────────────────
def read_block(path):
    with open(path) as f:
        return np.fromstring(f.read(), sep=' ')

# ── read vel.txt ──────────────────────────────────────────────────────────
# layout: n_times × 2 × NY × NX  (var 0 = u, var 1 = v)
vals    = read_block("vel.txt")
n_times = len(vals) // (2 * NY * NX)
vel     = vals.reshape(n_times, 2, NY, NX)
times   = T_START + np.arange(n_times) * DT_OUT

Vmean = vel[:,1,:,:].mean(axis=(0,1))  # time-averaged along-shore velocity (NY, NX)

print(f"vel    : {vel.shape}   (n_times={n_times}, 2 vars, NY={NY}, NX={NX})")
print(f"t range: {times[0]:.0f} – {times[-1]:.0f} s")

#%% PLOTTING
fig, ax = plt.subplots(figsize=(7,4), dpi=300)

pcm = ax.plot(x, Vmean,lw=3,alpha=0.8,color='red')

ax.set_xlabel("x  (cross-shore)  [m]")
ax.set_ylabel(r"$\overline{V}(x)$  [m/s]")
ax.set_title(rf"Longshore current", loc="left")
ax.set_xlim(0., XLENC)
ax.set_ylim(0., V_MAX)
ax.grid()

fig.tight_layout()
fname = f"Vmean.png"
fig.savefig(fname, dpi=130)
print(f"wrote {fname}")
plt.show()
# %%
