#!/usr/bin/env python3
"""
plot_velocity_snapshot.py — 2DH version
Velocity-magnitude colourmap with arrow overlay at chosen time.

Reads:
    bot.txt   — 2D bottom level
    vel.mat   — SWASH BLOCK output (LAYOUT 3, VEL)  — has depth-avg u and v
"""
#%%
import re
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat

# -------------------------------------------------------------- params
T_PLOT   = 1200.0
DX, DY   = 2.0, 2.0
L_DOM, W_DOM = 600.0, 200.0
SPD_MAX  = 1.8                    # colour-scale max               [m/s]
SKIP_X   = 25                     # arrow subsample in x
SKIP_Y   = 5                      # arrow subsample in y
VELFILE  = "vel.mat"

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

# depth-averaged x- and y-velocity (skip per-layer keys like vel_k1_x_)
u, t_u, key_u = pick_snapshot(VELFILE,
    ["vel_x_", "Velkx", "Velx_", "Vksix", "Vx_"], T_PLOT)
v, t_v, key_v = pick_snapshot(VELFILE,
    ["vel_y_", "Velky", "Vely_", "Vksiy", "Vy_"], T_PLOT)
zb =u
ny, nx = zb.shape
x = np.arange(nx) * DX
y = np.arange(ny) * DY
if u.shape != zb.shape:
    u = u.reshape(zb.shape)
if v.shape != zb.shape:
    v = v.reshape(zb.shape)

spd = np.sqrt(u**2 + v**2)
spd = u
dry = zb < 9999.0                                    # bed level above SWL
spd_m = np.ma.masked_where(dry, spd)
u_m   = np.ma.masked_where(dry, u)
v_m   = np.ma.masked_where(dry, v)

print(f"plotting |u|  at t ≈ {t_u:.1f} s   ('{key_u}', '{key_v}')")

# -------------------------------------------------------------- plot
fig, ax = plt.subplots(figsize=(11, 4.6))

pcm = ax.pcolormesh(x, y, spd_m, cmap="RdBu",
                    vmin=-SPD_MAX, vmax=SPD_MAX, shading="auto")

# shoreline contour
ax.contourf(x, y, zb, linewidths=1.0)
ax.set_xlabel("x  (cross-shore)  [m]")
ax.set_ylabel("y  (alongshore)   [m]")
ax.set_title(rf"$u(x, y)$  at  $t$ = {t_u:.1f} s",loc='left')
cb = fig.colorbar(pcm, ax=ax, label="u  [m/s]")


fname = f"vel2D_t{int(round(t_u)):04d}.png"
fig.savefig(fname, dpi=130)
print(f"wrote {fname}")
plt.show()

# %%
