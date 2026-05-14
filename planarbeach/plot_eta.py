#!/usr/bin/env python3
"""
plot_eta_snapshot.py — 2DH version
Top-down view of the instantaneous free surface η(x, y) at chosen time.

Reads:
    bot.txt   — 2D bottom level (from make_bathy.py)
    wlev.mat  — SWASH BLOCK output (LAYOUT 3, WATL)
"""
#%%
import re
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat

# -------------------------------------------------------------- params
T_PLOT  = 1200.0          # requested time                       [s]
DX, DY  = 2.0, 2.0
L_DOM, W_DOM = 600.0, 200.0
ETA_MAX = 1.0             # colour-scale half-range              [m]
WLEVFILE = "wlev.mat"

# -------------------------------------------------------------- helpers
def parse_swash_time(key):
    m = re.search(r"_(\d{2})(\d{2})(\d{2})(?:_(\d{1,3}))?$", key)
    if not m:
        return None
    h, mn, s, sub = m.groups()
    t = int(h)*3600 + int(mn)*60 + int(s)
    if sub:
        t += int(sub) / 10**len(sub)
    return t

def pick_snapshot(matfile, prefixes, t_target):
    data = loadmat(matfile)
    keys = [k for k in data.keys()
            if any(k.lower().startswith(p.lower()) for p in prefixes)]
    if not keys:
        raise SystemExit(f"No matching variables in {matfile}.  "
                         f"Got keys: {list(data.keys())[:10]} ...")
    times = np.array([parse_swash_time(k) for k in keys], dtype=float)
    order = np.argsort(times)
    keys, times = [keys[i] for i in order], times[order]
    idx = int(np.argmin(np.abs(times - t_target)))
    return np.array(data[keys[idx]]), times[idx], keys[idx]

# -------------------------------------------------------------- load

eta, t_now, key = pick_snapshot(WLEVFILE, ["Watl", "watl"], T_PLOT)
ny, nx = eta.shape
zb=eta
x = np.arange(nx) * DX
y = np.arange(ny) * DY

if eta.shape != zb.shape:
    eta = eta.reshape(zb.shape)

# mask dry cells (where eta is below bed) so they show as background
dry = eta <= -zb + 1e-6
eta_m = np.ma.masked_where(dry, eta)

print(f"plotting η  at t = {t_now:.1f} s   (key '{key}')")

# -------------------------------------------------------------- plot
fig, ax = plt.subplots(figsize=(11, 7))

pcm = ax.pcolormesh(x, y, eta_m, cmap="RdBu_r",
                    vmin=-ETA_MAX, vmax=ETA_MAX, shading="auto")

ax.set_xlabel("x  (cross-shore)  [m]")
ax.set_ylabel("y  (alongshore)   [m]")
ax.set_title(rf"$\eta(x, y)$  at  $t$ = {t_now:.1f} s",loc='left')
cb = fig.colorbar(pcm, ax=ax, label="η  [m]")

fname = f"eta2D_t{int(round(t_now)):04d}.png"
fig.savefig(fname, dpi=130)
print(f"wrote {fname}")
plt.show()

# %%
