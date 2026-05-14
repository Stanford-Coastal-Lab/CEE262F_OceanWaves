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
BOTFILE  = "bot.txt"

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
zb = np.loadtxt(BOTFILE)                  # (ny, nx)
ny, nx = zb.shape
x = np.arange(nx) * DX
y = np.arange(ny) * DY

eta, t_now, key = pick_snapshot(WLEVFILE, ["Watl", "watl"], T_PLOT)
if eta.shape != zb.shape:
    eta = eta.reshape(zb.shape)

# mask dry cells (where eta is below bed) so they show as background
dry = eta <= -zb + 1e-6
eta_m = np.ma.masked_where(dry, eta)

print(f"plotting η  at t = {t_now:.1f} s   (key '{key}')")

# -------------------------------------------------------------- plot
fig, ax = plt.subplots(figsize=(11, 4.6))

pcm = ax.pcolormesh(x, y, eta_m, cmap="RdBu_r",
                    vmin=-ETA_MAX, vmax=ETA_MAX, shading="auto")
# shoreline contour (z_b = 0)
ax.contour(x, y, zb, levels=[0.], colors="black", linewidths=1.0)

# always-dry land overlay (brown)
dry_overlay = np.ma.masked_where(zb >= 0., np.ones_like(zb))
ax.pcolormesh(x, y, dry_overlay, cmap="copper", alpha=0.55, shading="auto")

ax.set_xlabel("x  (cross-shore)  [m]")
ax.set_ylabel("y  (alongshore)   [m]")
ax.set_title(rf"$\eta(x, y)$  at  $t$ = {t_now:.1f} s",loc='left')
ax.set_aspect("equal")
cb = fig.colorbar(pcm, ax=ax, label="η  [m]")
fig.tight_layout()

fname = f"eta2D_t{int(round(t_now)):04d}.png"
fig.savefig(fname, dpi=130)
print(f"wrote {fname}")
plt.show()

# %%
